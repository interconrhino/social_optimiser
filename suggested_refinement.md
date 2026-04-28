# Suggested Refinement

## Eval context isolation

### Why

The current setup has all eval-infrastructure skill files (`simulated-innovator.md`, `recommendation-judge.md`, `proxy-paper-generator.md`) living in `.claude/skills/` alongside the pipeline skills. The eval-harness spawning prompt grants the pipeline-runner read access to "any file under `.claude/skills/`", which means the pipeline-runner can — and likely will — read `simulated-innovator.md` when it needs to spawn that subagent. That file's frontmatter description explicitly names the AI4SI corpus and the evaluation context. A pipeline-runner that knows it is being evaluated on a named corpus could web-search for that corpus, recover gold labels, and inflate its scores — silently and without any detectable trace in the session output. The same applies to `recommendation-judge.md`, whose scoring rubric reveals the method families under evaluation.

### Proposed changes

**1. Move eval infrastructure outside the agent root**

Create a sibling directory `social_optimiser_eval/` at the same level as `social_optimiser/`. Move all eval-specific content there:

```
Coding/
├── social_optimiser/                   ← Claude Code agent root (unchanged pipeline)
│   ├── CLAUDE.md
│   ├── .claude/skills/
│   │   ├── [pipeline skills only]
│   │   └── eval-harness.md             ← stays (must be invocable as a skill)
│   ├── knowledge/
│   └── session_output/                 ← real user sessions only
│
└── social_optimiser_eval/              ← new eval root, outside agent
    ├── proxy_papers/                   ← from eval/proxy_papers/
    ├── judgements/                     ← from eval/judgements/
    ├── figures/                        ← from eval/figures/
    ├── eval_sessions/                  ← eval runs (separate namespace from real sessions)
    ├── skills/                         ← source definitions, read only by scripts
    │   ├── simulated-innovator.md
    │   ├── recommendation-judge.md
    │   └── proxy-paper-generator.md
    └── scripts/
        ├── simulate_innovator.py       ← NEW
        ├── run_judge.py                ← NEW
        ├── aggregate_and_plot.py       ← from eval/scripts/
        └── run_algorithmselector_baseline.py
```

Remove `simulated-innovator.md`, `recommendation-judge.md`, and `proxy-paper-generator.md` from `.claude/skills/`. The pipeline-runner can now read `.claude/skills/` freely — no eval metadata lives there.

**2. Replace simulated-innovator Agent spawning with a Bash API call**

The pipeline-runner currently spawns the simulated innovator as a Claude Code subagent (using the `Agent` tool), which means both share the same project context. Replace this with a Bash call to `simulate_innovator.py`, which makes a direct Anthropic API call in a fully isolated process:

```
Pipeline-runner asks intake question
  → Bash: python .../simulate_innovator.py \
          --brief .../proxy_papers/paper_04.md \
          --question "..." \
          --history "..."
  → Anthropic API call (own process, own context, no Claude Code session state)
  → stdout: innovator's plain-text reply
  → Pipeline-runner treats stdout as the user's message
```

`simulate_innovator.py` reads the simulated-innovator instructions from `social_optimiser_eval/skills/simulated-innovator.md` at runtime and passes them as a system prompt. The pipeline-runner never reads that file.

**3. Replace recommendation-judge Agent spawning with a Bash API call**

Same pattern: `run_judge.py` reads the judge instructions from `social_optimiser_eval/skills/recommendation-judge.md`, session outputs, and the gold-label sidecar, then calls the Anthropic API and writes the judgement JSON. The orchestrator calls it via Bash and receives a one-line summary on stdout.

**4. Separate eval session numbering from real session numbering**

Eval sessions write to `social_optimiser_eval/eval_sessions/` with their own counter. Real user sessions continue writing to `social_optimiser/session_output/`. The two namespaces no longer interleave.

**5. Update eval-harness.md**

- Replace all `eval/` path references with absolute paths to `social_optimiser_eval/`
- Define `EVAL_ROOT` as a single constant at the top of the skill for easy reconfiguration
- Replace the "spawn simulated-innovator Agent" instruction with the Bash call pattern
- Replace the "spawn judge Agent" instruction with the Bash call pattern
- Remove the HARD SCOPING RULES exclusion list (no longer needed — exclusion is now structural)

### Open questions before implementation

1. Where should `social_optimiser_eval/` live? Proposed: `C:\Users\hyung\OneDrive\Documents\Coding\social_optimiser_eval\`
2. API key env variable: `ANTHROPIC_API_KEY` (standard)?
3. Model for `simulate_innovator.py`: `claude-haiku-4-5` (cheap, fast, sufficient for role-play)?