# Optimization Category Classification

**Session:** 0004

## Primary Match

**Technique:** Multi-objective Optimisation
**Catalog ID:** `multiobjective_optimisation`
**Confidence:** Medium-High

**Matching signals:**
- *Two or more objectives that cannot all be maximised simultaneously* → the priority paragraph's clauses (e.g. "prioritise first-gen" vs "do not reduce adult-learner outreach") pull in opposite directions; the user explicitly wants to see trade-offs, not a single point answer.
- *Equity or fairness is a stated goal alongside efficiency* → retention (efficiency) must be balanced with group-level coverage floors (fairness), and side-effects on unnamed groups must be detectable.
- *Stakeholders disagree on which objective matters most* → three funders plus an internal equity committee, each with different preferences; leadership rewrites the paragraph each semester.
- *Decision-makers want to see a range of options, not just one answer* → explicitly stated: "we want to choose whether we balance clauses evenly, protect the worst-served group, or maximise overall impact." This is exactly the weighted-sum / max-min / ε-constraint menu.
- *Need to explicitly explore the trade-off* → the board/equity committee must be able to see "how well a given recipe honours each clause" — i.e. the per-clause scoring is a Pareto-style dashboard.

**Why this fits:**
Rio Valle's core ask is not "which single list is optimal" — it is "how do we turn a stakeholder-written multi-clause priority paragraph into a defensible weekly decision rule, with visible trade-offs." That framing — multiple conflicting objectives, explicit trade-off visibility, and the need to support different scalarisation modes (balance / max-min / retention-max) — is the exact shape of multi-objective optimisation. The underlying per-week decision (pick ~210 of ~2,100 binary calls subject to budget and per-campus caps) is a combinatorial sub-problem, but the distinguishing feature driving method choice is the multi-objective / trade-off structure.

**Contraindications checked:**
- *"Only one objective matters — use LP or IP instead"* — Does **not** apply. The brief explicitly frames multiple objectives and explicit trade-off exploration as central.
- *"Objectives can be combined into a single weighted score with agreed weights — use LP with a composite objective"* — Does **not** apply. The weights are exactly what stakeholders disagree about; the system must show what happens under different choices, not assume they are given.

## Alternative 1

**Technique:** Integer Programming
**Catalog ID:** `integer_programming`
**When this would be preferred instead:** If, in a given semester, leadership commits to a single fixed scalarisation of the priority paragraph (e.g. a specific weighted-sum with agreed weights, or a specific ε-constraint version with fixed floors), the remaining weekly problem is a pure binary-knapsack-style call-selection subject to budget and per-campus caps — a standard integer program. This is also the inner solver that any multi-objective method would repeatedly call.

## Alternative 2

**Technique:** Simulation (Monte Carlo / Agent-Based)
**Catalog ID:** `simulation`
**When this would be preferred instead:** If the primary need were to stress-test proposed decision recipes against uncertainty (noisy engagement proxy, evolving student trajectories, off-policy historical bias) and side-effect detection were the dominant goal rather than trade-off curation, simulation over many semester trajectories would fit. In practice this is a strong *complement* — simulation of candidate recipes to score them on retention and side-effect metrics is the right tool for the side-effect-dashboard requirement — but it is not the organising framework for the overall method.

## Why alternatives were not the primary pick

Integer programming alone solves a single-objective version of the weekly call-list problem, but the user's defining pain point is that there is no single agreed objective — and when a coach reduced the paragraph to a single scoring rule, coverage of an unintended group dropped 30% without anyone noticing. A single-objective IP would reproduce that failure mode. Simulation can score any given recipe but does not itself generate the recipe or expose the trade-off frontier; it is better used as a validation/side-effect-detection layer wrapped around a multi-objective generator. Multi-objective optimisation is the technique that directly addresses the stated pain (per-clause visibility, selectable scalarisation, Pareto view), and it delegates the per-weight inner problem to IP and the per-recipe evaluation to simulation.

## Structural features the catalog does not fully name

For honesty, the problem additionally has: (a) sequential / multi-period structure over 12 weekly epochs with state updates, (b) partial observability of per-student engagement, and (c) a shared budget coupling otherwise per-student dynamics. These features together resemble a restless resource-allocation-under-uncertainty structure; the Influence-Maximisation/POMDP catalog entry captures the sequential-partial-observability axis but is explicitly scoped to *social-network spread* problems, which Rio Valle is not (each student is a direct target; there is no peer-propagation structure). These structural features are flagged for the method-research stage to explore via web search — they may materially shape the chosen algorithm within the multi-objective framing.
