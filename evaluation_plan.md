# Evaluation Plan — Social Optimiser

Plan for adapting Hyungsick's social_optimiser so we can evaluate it against the 31 AI4SI papers from the previous project.

## Context

- 31 source papers: `/Users/Gillian/Downloads/AI4SI PROJECT/sources/` (PDFs)
- Gold-standard labels: `/Users/Gillian/Downloads/AI4SI PROJECT/project_context/gold_method_labels.jsonl` — one JSONL per paper with `social_problem`, `gold_optimization_type`, `gold_key_method`
- Existing test split (5 papers): `/Users/Gillian/Downloads/AI4SI PROJECT/project_context/EVAL_TEST_5PAPERS.md`
- Hyungsick's pipeline: 6 Claude Code skills in `.claude/skills/`, driven by `CLAUDE.md`
- **Hard constraint from Gillian: no API keys.** Everything runs as Claude Code skills / subagents. We use Claude Code's own Agent tool (the same pattern Hyungsick uses for `method-research`) to orchestrate.

---

## Architecture — four Claude skills + strict context isolation

All four live inside the social_optimiser repo under `.claude/skills/`.

| Skill | Purpose | Context isolation |
|---|---|---|
| **proxy-paper-generator** | Reads the original paper PDF + gold labels, produces `eval/proxy_papers/paper_NN.md` (proxy brief) + `paper_NN_meta.json` (sidecar with gold labels). | Run once per paper by the developer. Meta file is gitignored from the pipeline-runner and simulated-innovator by convention enforced in the eval-harness prompt. |
| **simulated-innovator** | Role-plays the social innovator during intake. Reads only the proxy brief. Forbidden from naming any method. | Spawned as a sub-subagent by the pipeline-runner. No access to meta / source PDFs / gold labels. |
| **recommendation-judge** | Scores a completed session against the gold labels. 5-dimension rubric (0–4 each), plus captured method names, match rationale, failure modes. | Spawned as a separate subagent *after* the pipeline-runner completes. This is the only context with access to both the session output AND the gold labels. |
| **eval-harness** | Orchestrator skill. Spawns pipeline-runner and judge as isolated subagents; never touches gold labels itself. | The skill the developer invokes. The orchestrator running it must start fresh for each paper — no prior gold/source context. |

### Why the isolation matters (lesson from the paper_04 dry run)

When the orchestrator has the original paper or gold labels in its context, the pipeline run is contaminated — the orchestrator will (explicitly or implicitly) steer the pipeline toward the correct answer, because it already knows. The dry run on paper_04 produced a recommendation that *did* match the gold method, but the match was partly the orchestrator's knowledge leaking through: the classification skill's `03_classification.md` pointed downstream research explicitly at "RMAB / DFL" even though the catalog has no such entry. In a genuinely isolated run, the pipeline would have had to decide what to do with a catalog-primary-match of Integer Programming — and that is the honest measurement.

The four-skill architecture enforces isolation:
- The `eval-harness` orchestrator spawns `pipeline-runner` as a subagent with hard scoping rules ("you may read the proxy brief, you may not read source PDFs or meta files").
- `simulated-innovator` is a sub-subagent spawned by the pipeline-runner — also scope-limited to the proxy brief.
- `recommendation-judge` is a second subagent spawned by the orchestrator *after* the pipeline is done — with access to both the session output and the gold labels. It is the only context that sees both sides.

The orchestrator itself has read-no-gold-labels as its invariant. When that holds, the measurement is unbiased.

---

## Step 1 — Proxy paper generator

### Purpose
Produce a rewritten problem description for each of the 31 papers that (a) preserves the optimisation structure that induces the same method, and (b) disguises the social domain well enough that a web search on the proxy does not surface the original paper.

### Skill design
Input: `paper_NN.pdf` + corresponding row of `gold_method_labels.jsonl`.

The skill prompts Claude to:
1. Read the paper and extract the **abstract optimisation structure** — decision variables (what's chosen), objective (what's maximised/minimised), constraints (what binds), dynamics (what's stochastic / sequential), scale.
2. Invent a *new* social domain that shares all of the above. Example: a restless-bandit maternal-health scheduling paper → a restless-bandit wildlife-ranger-patrol scheduling paper. Method structure identical; domain narrative different.
3. Write the proxy as a 1–2 page markdown document in the voice of a social innovator describing their real-world problem (not in paper/academic voice). This matches the input format the social_optimiser expects.
4. **Self-test for search leakage**: before finalising, generate 3 candidate web-search queries a user might plausibly type (domain keywords + problem type). The generator flags queries that could surface the original paper title/abstract; if flagged, it iterates on the domain narrative.

### Output location
`eval/proxy_papers/paper_NN.md` — one per paper. Plus a sidecar `eval/proxy_papers/paper_NN_meta.json` recording: original paper ID, intended method family, flagged search queries.

### Validation
Before trusting the set, spot-check 3 proxies manually:
- Does the mathematical structure match? (We can run the proxy through Hyungsick's problem-specification skill and compare the formal spec to the gold label.)
- Does a web search on the proxy surface the original paper? (Manual test — actually run the search.)

### Questions / risks
- **Some papers may be hard to disguise.** The HEALER paper (homeless-shelter influence maximisation) has such a distinctive domain that any graph-of-people + seeding problem will feel similar. For those, we accept some leakage risk and note it.
- **The generator may drift away from the exact method.** A robust-RMAB paper rewritten as a simple RMAB loses the DRO aspect. The spot-check step catches this; the fix is tighter instructions pinning the structural features that must be preserved.

---

## Step 2 — Simulated-innovator agent

### Purpose
Replace the human user in the social_optimiser's interactive loop. The simulated innovator answers the pipeline's intake questions from the perspective of someone who knows their social problem but has no background in optimisation.

### Design — spawned as a subagent
The cleanest fit with Hyungsick's existing architecture is to have the social_optimiser itself spawn the simulated-innovator via the `Agent` tool — exactly like `method-research` spawns a web-search subagent. We add a new top-level flag to `CLAUDE.md`: if the session is started in "eval mode" with a proxy paper path, the intake skill's first act is to spawn the simulated-innovator subagent and converse with *it* instead of waiting for the user.

### Constraints on the simulated innovator
Loaded into the subagent's system prompt:
- You have access to **only** the proxy paper's problem description, constraints, data-availability notes, and dynamics.
- You do **not** have access to the method label, algorithm name, or any optimisation terminology.
- You speak as a domain practitioner (NGO worker, policy officer) — plain language, real-world phrasing. Do not volunteer mathematical framings.
- If asked "do you have data X?", answer truthfully based on what the proxy paper says is available. Do not fabricate.
- If asked a question the proxy paper does not answer, say so — do not invent.

### Questions / risks
- **Leakage risk from the proxy paper.** If the proxy paper accidentally contains method-suggesting language (e.g. "we use a Markov decision process"), the simulated innovator will leak it. The proxy-paper generator must scrub method-hint language before handing off.
- **Will the social_optimiser notice it's talking to a bot?** Possibly. If it does, that's a design flaw in the intake skill, not in our evaluation — worth reporting back to Hyungsick.

---

## Step 3 — Recommendation judge

### Purpose
Score the social_optimiser's output against the gold label in a way that is defensible for the write-up.

### Rubric (0–4 per dimension, reported separately)
| Dimension | What we score |
|---|---|
| **Method family recovery** | Did the recommendation name the correct optimisation class (e.g. RMAB, MCLP, DRO, DFL)? |
| **Problem formulation fidelity** | Do the decision variables, objective, and constraints in `06a` match the structure implied by the gold label? |
| **Algorithmic depth** | Does the recommendation name a specific algorithm with theoretical properties, or just a family? |
| **Implementation specificity** | Does it name concrete tools (solver, library), parameters to calibrate, validation approach? |
| **Stakeholder clarity** | Is `06b` understandable to a non-technical reader? |

Total score: sum of the 5 dimensions (0–20). We also keep the per-dimension breakdown so we can see *where* the agent does well vs poorly, not just a scalar.

### Judge output
`eval/judgements/paper_NN_run_M.json`:
```json
{
  "paper_id": "paper_04",
  "run_id": 2,
  "scores": {"method_family": 4, "formulation": 3, "depth": 4, "implementation": 4, "clarity": 4},
  "total": 19,
  "method_named": "Whittle index RMAB with decision-focused learning",
  "method_gold": "Whittle index optimization for RMAB ... Decision-Focused Learning",
  "match_rationale": "...",
  "failure_modes": []
}
```

### Controlling for non-determinism
Run each paper **3 times** and report mean + range per dimension. This directly addresses write-up idea #1 — we don't claim "the agent scores X", we claim "the agent scores X ± range across runs".

### Questions / risks
- **Claude judging Claude.** Using Claude as both the agent-under-test and the judge has self-favouring risk. Mitigations: (a) make the judge's prompt explicitly compare against the gold text, not just "is this good?"; (b) sanity-check by having you (Gillian) manually score 3–5 recommendations and compare against the judge's scores on the same runs. If judge correlates with your scores, we trust it.

---

## Step 4 — Pilot subset, iterate, scale

Do not run all 31 papers upfront. Sequence:

1. **Build all three agents on paper_04** (the DFL-RMAB maternal health paper — well-structured, clearly labelled, representative).
2. **Pilot on 5 papers** — reuse `EVAL_TEST_5PAPERS.md` if that split is sensible; otherwise pick 5 to span method families (one RMAB, one DRO, one MCLP-like, one graph-based, one non-standard).
3. **Review pilot results with Gillian.** Look for: proxy-paper quality issues, simulated-innovator leakage, judge miscalibration. Iterate on whichever is weakest.
4. **Expand to full 31** only once the pilot looks clean.

Budget expectation: the pipeline is token-heavy (6 stages × web research). 31 papers × 3 runs = 93 full pipeline runs. Start with 5 × 3 = 15 and see how long that takes before committing to the full set.

---

## Step 5 — Reporting & visualisation

All plots written to `eval/figures/`. At minimum:

1. **Per-paper score distribution.** Horizontal bar chart, one bar per paper, showing mean total score with error bars (min/max across the 3 runs). Sorted by mean. Reveals: which papers the agent handles well vs struggles with.
2. **Per-dimension heatmap.** 5 rubric dimensions × N papers, coloured by mean score. Reveals: does the agent systematically fail on, e.g., "algorithmic depth" but ace "stakeholder clarity"?
3. **Method-family recovery rate.** Confusion-matrix-style grid: gold method family vs recommended method family. Reveals specific confusions (e.g., "RMAB recommended as MDP").
4. **Comparison to AlgorithmSelector baseline** (stretch goal). If time permits, re-run the proxy papers through the old pipeline and plot both on the same chart. This makes the write-up's "why we moved" argument empirical, not just narrative.

Plots produced by a small Python script in `eval/scripts/` that reads the judgement JSONs. Keeping this outside Claude Code (plain matplotlib) is fine — it's deterministic and reproducible.

---

## Open questions I'd like your call on

1. **Should we re-run AlgorithmSelector on the proxy papers as a baseline?** This strengthens the write-up but adds scope. My lean: yes, on the 5-paper pilot only — enough to make a defensible comparison without re-engaging the old system at full scale.
2. **Do we score `06a` and `06b` separately, or roll them up?** My lean: one total, but keep the per-dimension breakdown so the dual-audience design of the social_optimiser is still visible in the data.
3. **Where should the eval artefacts live?** My proposal: `social_optimiser/eval/` (new directory), alongside `session_output/`. Keeps the evaluation infra in the same repo as the agent being evaluated. Alternative: keep it in the AI4SI PROJECT folder. Pro of the proposal: anyone cloning social_optimiser can see and reproduce the evaluation. Con: Hyungsick may not want evaluation scaffolding in his consulting-tool repo — worth asking him before committing to location.
4. **How aggressive is "cannot easily search"?** Do we require that the top 10 Google results for the proxy domain do not contain the original paper, or is "does not appear in the first result page for a plausible user query" sufficient? The stricter criterion is much harder to satisfy for papers in well-trodden domains.
5. ~~**Do we care about the adaptive/technical gate?**~~ **Decided: yes — include.** We'll add 2–3 synthetic adaptive problems covering distinct sub-types (e.g. Alignment, Power, Inertia) and confirm the agent halts at `01_problem_profile.md` with the correct redirect message. These are authored by hand (not by the proxy-paper generator, since there's no ground-truth paper to derive them from). Scored pass/fail: did the gate trigger, and was the sub-type classification correct?

---

## Sequencing (concrete)

1. Build proxy-paper-generator → generate proxy for paper_04 → you (Gillian) spot-check → iterate.
2. Build simulated-innovator skill + wire into eval-mode intake → dry-run on paper_04.
3. Build recommendation-judge → score the paper_04 dry-run → you score it manually → compare.
4. If calibration is close, extend to 5-paper pilot. If not, iterate on the judge.
5. Hand-author 2–3 adaptive problems → run through social_optimiser → confirm gate triggers correctly.
6. Re-run the 5 proxy papers through AlgorithmSelector (live research mode, Anthropic key in `AlgorithmSelector/.env`) as the baseline comparison.
7. Produce plots for write-up (scores per paper, per-dimension heatmap, social_optimiser vs AlgorithmSelector side-by-side, adaptive-gate pass/fail table).

Each stage is a stop point. We don't proceed to the next until the current one is sound.

**Scope cap:** 5 proxy papers + 3 adaptive probes. Do not expand beyond this without explicit approval from Gillian.
