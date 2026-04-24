"""Run AlgorithmSelector (the prior pipeline) against the social_optimiser proxy briefs
and materialise its output as session-like folders so the same recommendation-judge rubric
can grade both systems apples-to-apples.

Input:  /Users/Gillian/Downloads/social_optimiser/eval/proxy_papers/paper_*.md
Output: /Users/Gillian/Downloads/social_optimiser/eval/algorithmselector_baseline/paper_NN/
          ├── 05_method_selection.md     (predicted family + rationale)
          ├── 06a_rec_formal_spec.md     (problem_spec + citations)
          ├── 06b_rec_plain_english.md   (rationale restated)
          └── raw_response.json          (full AlgorithmSelector response for audit)

Uses the Anthropic API key from /Users/Gillian/Downloads/AI4SI\ PROJECT/AlgorithmSelector/.env.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Load the Anthropic key and other config before importing the AlgorithmSelector modules.
AS_ROOT = Path("/Users/Gillian/Downloads/AI4SI PROJECT/AlgorithmSelector")
AS_SRC = AS_ROOT / "apps" / "api" / "src"
sys.path.insert(0, str(AS_SRC))

# Load .env manually — we do not want to depend on pydantic-settings picking it up from cwd.
ENV_PATH = AS_ROOT / ".env"
if ENV_PATH.exists():
    for raw_line in ENV_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from config import settings  # noqa: E402
from models.session import (  # noqa: E402
    AnswerClarificationsRequest,
    ClarificationAnswer,
    StartSessionRequest,
)
from services.coordinator_service import CoordinatorService  # noqa: E402


REPO = Path("/Users/Gillian/Downloads/social_optimiser")
PROXIES_DIR = REPO / "eval" / "proxy_papers"
OUTPUT_DIR = REPO / "eval" / "algorithmselector_baseline"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAPERS = ["paper_01", "paper_02", "paper_03", "paper_04", "paper_05"]


def configure() -> None:
    """Force the AlgorithmSelector into live Anthropic mode."""
    settings.llm_provider = "anthropic"
    settings.research_mode = "live"
    settings.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not in environment after loading .env.")
    settings.llm_api_key = settings.anthropic_api_key
    if not settings.llm_model or not settings.llm_model.startswith("claude"):
        settings.llm_model = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")


def answer_for_field(field: str, proxy_text: str) -> str:
    """Thin set of defaults for clarification questions, patterned on run_project_predictions.py."""
    normalised = field.strip().lower()
    defaults = {
        "utility scoring weights": "Use the primary social outcome first, then fairness or coverage, then operational workload.",
        "label quality": "Historical data is available but reflects a non-random past policy and may be noisy or biased.",
        "intervention effect": "A limited intervention is available and expected to improve outcomes when targeted well.",
        "service floor policy": "Maintain minimum service levels for underserved or high-need groups.",
        "decision variable": "Choose which limited resources, interventions, or actions to assign given the context described.",
        "objective function": "Maximise the stated social benefit while respecting fairness, capacity, and feasibility.",
        "constraints": "Respect the budget, staff capacity, timing, eligibility, and operational rules in the brief.",
        "narrower operational decision": "Prioritise, allocate, or schedule limited resources for the affected population.",
    }
    return defaults.get(normalised, "Use the operational detail in the brief as the basis for your answer.")


def run_one(paper_id: str) -> dict:
    proxy_path = PROXIES_DIR / f"{paper_id}.md"
    proxy_text = proxy_path.read_text()

    service = CoordinatorService()

    session_id = f"baseline_{paper_id}"
    resp = service.start_session(
        StartSessionRequest(session_id=session_id, narrative=proxy_text, prior_state={})
    )

    rounds = 0
    max_rounds = 3
    while resp.status == "needs_clarification" and rounds < max_rounds:
        answers = [
            ClarificationAnswer(
                question_id=q.question_id,
                answer=answer_for_field(q.field, proxy_text),
            )
            for q in resp.pending_questions
        ]
        resp = service.answer_clarifications(
            AnswerClarificationsRequest(session_id=session_id, answers=answers)
        )
        rounds += 1

    artifacts = resp.artifacts

    recommended = ""
    rationale = ""
    alternatives: list[str] = []
    if artifacts.recommendation and artifacts.recommendation.recommended_method_family:
        recommended = artifacts.recommendation.recommended_method_family
    if artifacts.ranking and artifacts.ranking.ranked_methods:
        if not recommended:
            recommended = artifacts.ranking.ranked_methods[0].method_family
        rationale = artifacts.ranking.ranked_methods[0].rationale or ""
        alternatives = [m.method_family for m in artifacts.ranking.ranked_methods[1:3]]
    if not recommended and artifacts.problem_spec:
        recommended = artifacts.problem_spec.problem_type.value

    problem_spec_json = (
        artifacts.problem_spec.model_dump_json(indent=2) if artifacts.problem_spec else "{}"
    )

    citations: list[dict] = []
    if artifacts.research:
        for card in artifacts.research.evidence_cards:
            for cit in card.citations:
                citations.append(
                    {
                        "method_family": card.method_family,
                        "title": cit.title,
                        "url": cit.url,
                        "source_type": cit.source_type,
                    }
                )

    return {
        "paper_id": paper_id,
        "recommended_method_family": recommended,
        "rationale": rationale,
        "alternatives": alternatives,
        "problem_spec_json": problem_spec_json,
        "citations": citations[:10],
        "clarification_rounds": resp.clarification_rounds,
        "status": resp.status,
    }


def materialise(result: dict) -> None:
    paper_id = result["paper_id"]
    out = OUTPUT_DIR / paper_id
    out.mkdir(parents=True, exist_ok=True)

    (out / "raw_response.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # 05_method_selection.md
    alt_lines = "\n".join(f"- {a}" for a in result["alternatives"]) or "_(none)_"
    sel = f"""# Method Selection (AlgorithmSelector baseline)

**Paper:** {paper_id}
**System:** AlgorithmSelector (prior pipeline)

## Selected Algorithm

**Name:** {result['recommended_method_family'] or '(no recommendation produced)'}

**Why this algorithm (AlgorithmSelector's rationale, verbatim):**

{result['rationale'] or '_(no rationale returned by the pipeline)_'}

## Alternatives

{alt_lines}

## Clarification rounds

{result['clarification_rounds']}

## Status

{result['status']}
"""
    (out / "05_method_selection.md").write_text(sel)

    # 06a — AlgorithmSelector does not produce a formal spec in this deliverable.
    # Write what it DID produce (problem_spec + citations) honestly.
    cit_rows = "\n".join(
        f"| {c['method_family']} | {c['title']} | {c['source_type']} | {c.get('url','')} |"
        for c in result["citations"]
    ) or "_(no citations returned)_"
    rec_formal = f"""# Recommendation: Formal Specification — AlgorithmSelector baseline ({paper_id})

AlgorithmSelector's deliverable is a method-family classification plus a problem-spec summary.
It does not produce a formal mathematical formulation, algorithm-specific theoretical properties,
or implementation guidance. This file reproduces what the pipeline did produce; the recommendation-judge
will grade it accordingly.

## 1. Problem specification (as produced by AlgorithmSelector)

```json
{result['problem_spec_json']}
```

## 2. Recommended method family

{result['recommended_method_family'] or '_(none)_'}

## 3. Rationale

{result['rationale'] or '_(no rationale)_'}

## 4. Research citations returned by the pipeline

| Method family | Title | Source | URL |
|---|---|---|---|
{cit_rows}

## 5. What is NOT in this deliverable

- No formal decision variables, objective, constraints, or parameters.
- No specific algorithm named beyond a family label.
- No theoretical properties, complexity analysis, or approximation ratios.
- No concrete implementation steps, software stack, or validation plan.
- No plain-language stakeholder summary.
"""
    (out / "06a_rec_formal_spec.md").write_text(rec_formal)

    # 06b — AlgorithmSelector has no plain-language stakeholder file.
    rec_plain = f"""# Plain English Summary — AlgorithmSelector baseline ({paper_id})

AlgorithmSelector does not produce a plain-language recommendation for a non-technical
stakeholder. Its deliverable is a method-family classification and a short rationale.
This placeholder file represents the absence of a stakeholder-facing deliverable and will
be scored accordingly on the stakeholder-clarity dimension.

## What AlgorithmSelector would tell the programme director

> {result['rationale'] or '_(no rationale returned)_'}
"""
    (out / "06b_rec_plain_english.md").write_text(rec_plain)


def main() -> None:
    configure()
    print(f"Config: llm_provider={settings.llm_provider}, model={settings.llm_model}, research_mode={settings.research_mode}")
    for paper_id in PAPERS:
        print(f"\n=== Running AlgorithmSelector on {paper_id} ===")
        try:
            result = run_one(paper_id)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED: {exc}")
            result = {
                "paper_id": paper_id,
                "recommended_method_family": "",
                "rationale": f"Pipeline error: {exc}",
                "alternatives": [],
                "problem_spec_json": "{}",
                "citations": [],
                "clarification_rounds": 0,
                "status": "error",
            }
        materialise(result)
        print(f"  Recommended: {result['recommended_method_family']!r}")
        print(f"  Alternatives: {result['alternatives']}")
        print(f"  Clarification rounds: {result['clarification_rounds']}")

    print(f"\nAll outputs under {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
