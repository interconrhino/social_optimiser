# Social Optimiser

A Claude Code agent that helps social innovators identify the right mathematical optimisation approach for their problems.

## What it does

Social innovators often face problems that are structurally optimisable — resource allocation, routing, scheduling, matching, intervention planning — but lack the vocabulary or background to identify which quantitative method applies. This agent bridges that gap.

It conducts a plain-language interview, classifies the problem, researches current state-of-the-art algorithms, and produces a research-grade recommendation: formal problem formulation, specific algorithm with theoretical properties, implementation guidance, and a plain-language summary shareable with non-technical stakeholders.

## The core distinction

Not every social problem can be optimised. Before any analysis, the agent classifies the problem as:

- **Technical** — defined end state, defined activities → the pipeline runs and produces a recommendation
- **Adaptive** — undefined end state or undefined activities → the agent halts, identifies the adaptive sub-type (alignment, power, inertia, etc.), and redirects to more appropriate approaches

Applying optimisation to an adaptive problem misdirects effort. The classification gate exists to prevent that.

## How to use it

Open this folder in Claude Code and describe your problem. The agent will take it from there.

```
> Tell me about the challenge you're facing.
```

Each session saves intermediate outputs to `session_output/NNNN/` for review and auditability.

## Pipeline

```
1. Problem Intake          → interview + adaptive/technical classification
2. Problem Specification   → formal mathematical spec (variables, objective, constraints)
3. Optimisation Matching   → maps formal structure to technique category
4. Method Research         → web search for current SOTA algorithms
5. Method Selection        → selects best algorithm given structure and scale
6. Recommendation          → full research-grade output
```

## Knowledge base

| File | Contents |
|---|---|
| `knowledge/optimization_catalog.json` | 8 technique entries with signals, algorithms, and references |
| `knowledge/adaptive_types.json` | 6 adaptive sub-types with classification signals and redirect messages |
| `1602.00165v1.pdf` | Reference depth benchmark — HEALER (Yadav et al., AAMAS 2016) |

## Recommendation depth

Recommendations are benchmarked against applied operations research — formal enough for a technical implementer, clear enough for a non-technical decision-maker. Every output includes:

- Formal problem formulation (decision variables, objective function, constraints)
- Specific algorithm with approximation guarantees and complexity
- Data requirements and key parameters to calibrate
- Validation approach and baseline to beat
- Plain-language summary for stakeholders
