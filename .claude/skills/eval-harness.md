---
name: eval-harness
description: Run the social_optimiser pipeline end-to-end on a proxy paper under strict context isolation — so the agent being evaluated cannot cheat via ground-truth knowledge held by the orchestrator. Spawns one isolated subagent for the pipeline run and a second isolated subagent for the recommendation-judge. Produces session_output/NNNN/ (the pipeline outputs) and eval/judgements/paper_NN_run_M.json (the score). Invoke when running an automated evaluation of the social_optimiser on the AI4SI proxy corpus.
---

# Evaluation Harness

## Design goal: strict context isolation

The lesson from the dry run on paper_04: if the orchestrator has already seen the original paper or the gold label, it contaminates the pipeline — it will (explicitly or implicitly) route the pipeline toward the correct method using knowledge it should not have. Any meaningful measurement requires the entity running the pipeline to have *only* the proxy brief in its context.

This skill enforces that by splitting the evaluation into **three isolated Claude subagents**:

```
ORCHESTRATOR (invokes this skill)
 │
 ├─ 1. Spawns PIPELINE-RUNNER subagent
 │         Scope:  proxy brief ONLY. No gold labels, no source PDFs, no meta files.
 │         Output: session_output/{NNNN}/ (standard pipeline artefacts + Convo.md + eval_tag.json)
 │
 ├─ 2. Spawns RECOMMENDATION-JUDGE subagent (separate context)
 │         Scope:  session_output/{NNNN}/ + eval/proxy_papers/paper_NN_meta.json (gold labels)
 │         Output: eval/judgements/paper_NN_run_M.json
 │
 └─ 3. Reports to the developer: session ID, judge score, any flagged issues
```

The orchestrator itself does NO pipeline work. It only spawns subagents, checks files exist, and reports.

---

## Inputs

- `proxy_paper_id` — e.g., `paper_04`
- `run_id` — integer, for multi-run variance measurement. First run is `1`.

---

## Orchestrator procedure

### 0. Pre-flight

Verify (without reading):
- `/Users/Gillian/Downloads/social_optimiser/eval/proxy_papers/{proxy_paper_id}.md` exists.
- `/Users/Gillian/Downloads/social_optimiser/eval/proxy_papers/{proxy_paper_id}_meta.json` exists.

Compute:
- Next session ID: scan `session_output/`, take max 4-digit number + 1.
- Judge output path: `eval/judgements/{proxy_paper_id}_run_{run_id}.json`.

**Do not** read the proxy brief, do not read the meta file, do not read the source PDF. If you already have any of these in your context from earlier conversation, you are disqualified from being the orchestrator for this paper — start a fresh session.

### 1. Spawn the pipeline-runner

Invoke the Agent tool with the following prompt (fill in placeholders). Wait for completion.

```
You are a Claude Code agent operating as the social_optimiser. You are being run in EVALUATION MODE on a proxy paper.

BEFORE YOU DO ANYTHING ELSE, read these three files in order — they define how you operate:
  1. /Users/Gillian/Downloads/social_optimiser/CLAUDE.md
  2. /Users/Gillian/Downloads/social_optimiser/.claude/skills/problem-intake.md
  3. /Users/Gillian/Downloads/social_optimiser/eval/proxy_papers/{proxy_paper_id}.md   ← this is your "user"

HARD SCOPING RULES:
- You may read: CLAUDE.md, any file under .claude/skills/, any file under knowledge/, the proxy brief at eval/proxy_papers/{proxy_paper_id}.md.
- You MUST NOT read: any file under /Users/Gillian/Downloads/AI4SI\ PROJECT/sources/, any *_meta.json file under eval/proxy_papers/, any file under /Users/Gillian/Downloads/AI4SI\ PROJECT/project_context/ (those contain gold labels), any file under eval/judgements/.
- You are allowed to use WebSearch / WebFetch for the method-research stage — but do not use them to search for the proxy brief's verbatim text. Search for the problem structure you have derived, not for the brief's wording.

SESSION SETUP:
- Your session ID is: {NNNN}
- Create /Users/Gillian/Downloads/social_optimiser/session_output/{NNNN}/
- Write eval_tag.json there immediately with: {"eval_mode": true, "proxy_paper_id": "{proxy_paper_id}", "session_id": "{NNNN}", "run_id": {run_id}, "started_at": "<ISO UTC now>"}.

INTAKE:
When the problem-intake skill wants user input, you invoke the simulated-innovator subagent via the Agent tool. Pass it: the proxy brief path, the current question from intake, and the conversation transcript so far. Treat its reply as if the user had typed it. Continue intake until you have enough to produce the Problem Profile (typically 3–6 exchanges).

The rest of the pipeline (problem-specification → optimization-matcher → method-research → method-selection → recommender) runs as normal, writing outputs to session_output/{NNNN}/ per CLAUDE.md's file-naming rules.

At session close, write Convo.md per CLAUDE.md.

Do not judge your own output. Do not compare your recommendation to any "gold" or "expected" answer — that is a separate subagent's job. Just produce the best recommendation you can from the proxy brief alone.

When done, print a 3-line final report:
  - Session ID
  - Technique recommended (from 05_method_selection.md)
  - Any self-flagged concerns (e.g., "I am not confident the catalog matched this problem well")

Then return.
```

### 2. Verify the pipeline outputs

Check that `session_output/{NNNN}/` now contains: `eval_tag.json`, `01_problem_profile.md`, `02_formal_spec.md`, `03_classification.md`, `04_research_findings.md`, `05_method_selection.md`, `06a_rec_formal_spec.md`, `06b_rec_plain_english.md`, `Convo.md`.

If any file is missing, surface the error to the developer — do not proceed to judging.

### 3. Spawn the judge

Invoke the Agent tool with the following prompt. Wait for completion.

```
You are the recommendation-judge for the social_optimiser evaluation.

Read /Users/Gillian/Downloads/social_optimiser/.claude/skills/recommendation-judge.md for your full instructions.

Your inputs for this run:
- Session folder: /Users/Gillian/Downloads/social_optimiser/session_output/{NNNN}/
- Gold label file: /Users/Gillian/Downloads/social_optimiser/eval/proxy_papers/{proxy_paper_id}_meta.json
- Write your judgement to: /Users/Gillian/Downloads/social_optimiser/eval/judgements/{proxy_paper_id}_run_{run_id}.json

Proceed.
```

### 4. Report

Print a 5-line summary to the orchestrator's conversation:
- Session ID
- Proxy paper ID, run ID
- Recommended technique (from `05_method_selection.md`) and gold technique (from `paper_NN_meta.json`)
- Total score out of 20 (from the judge's output)
- A one-sentence note on any flagged failure modes

---

## What NOT to do

- **Do not** run any pipeline skill yourself. Spawn subagents.
- **Do not** read the gold labels or source PDF in the orchestrator context — that re-contaminates future spawns if the orchestrator retains context.
- **Do not** shortcut multi-run runs. Each `run_id` is an independent spawn; do not reuse a prior session's outputs for a new run.
- **Do not** let the judge and pipeline-runner share a context. They are deliberately separate subagents.
