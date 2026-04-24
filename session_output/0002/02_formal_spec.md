# Formal Problem Specification

**Session:** 0002
**Domain:** Social services / housing & community support

## Decision Variables

| Variable | Type | Domain | Meaning |
|---|---|---|---|
| `a_{i,t}` | Binary | {0, 1} | 1 if family *i* receives a caseworker home visit in week *t*, 0 otherwise. Indexed over families *i = 1, …, N* and weeks *t = 1, …, T*. |

With N ≈ 800 families and T = 52 weeks, the core decision space has ~41,600 binary variables, though in practice decisions are revealed sequentially — only the current week's **a**_t vector of 800 binaries is committed each week.

A latent per-family state is **observed each week**, not decided:
- `s_{i,t} ∈ {stable, at-risk, crisis}` — observed status of family *i* at the start of week *t*.

## Objective Function

**Direction:** Maximise

**What:** Total cumulative family welfare over the cohort across the 52-week year — measured as stable-weeks earned minus a weighted penalty on weeks spent in crisis. The director confirmed this aggregate is the operational definition of success.

**Form:**

```
maximise  E [  Σ_{t=1..T}  Σ_{i=1..N}  r(s_{i,t})  ]
```

where `r(·)` is a per-family per-week welfare score:

```
r(stable)   = +1
r(at-risk)  =  0    (placeholder — calibratable)
r(crisis)   = −c    (c > 1; the director said crisis is weighted "more heavily")
```

The expectation is over the stochastic realisation of future family status trajectories, which depend on the visit actions taken over time.

## Constraints

| # | Constraint | Type | Form |
|---|---|---|---|
| 1 | Each week, at most 40 families can be visited (caseworker capacity). | Hard | `Σ_{i=1..N} a_{i,t} ≤ K = 40`  ∀ t |
| 2 | Visit decisions are binary — a family is either visited in a given week or not. | Hard | `a_{i,t} ∈ {0,1}`  ∀ i, t |
| 3 | Caseworkers are loosely assigned to sub-regions of the metro area; cross-region visits are operationally expensive. | Soft | — (could be modelled as a per-region sub-budget or a cost term; see Open Questions) |
| 4 | Some families require language-matched or relationship-continuity caseworkers. | Soft | — (matching constraint; may reduce which of the 40 slots is available to a given family in a given week) |

## Parameters (Known Inputs)

| Parameter | Description | Certainty |
|---|---|---|
| N | Number of active first-year families ≈ 800 | Known |
| K | Weekly visit capacity = 40 | Known |
| T | Horizon = 52 weeks | Known |
| `x_i` | Intake feature vector for family *i* (~10–20 features: origin, family composition, language, employment history, trauma screening, neighbourhood, etc.) | Known at intake |
| `c` | Weight on crisis-week penalty relative to stable-week reward | Unknown — needs calibration with the director |
| `P(s' | s, a, x)` | Transition probabilities — how family status evolves from one week to the next as a function of current state, whether visited, and family features | **Unknown a priori** — must be estimated from historical data |

## Uncertainty Structure

**Central uncertainty:** per-family week-to-week status transitions `P(s_{i,t+1} | s_{i,t}, a_{i,t}, x_i)` are not known in closed form. The organisation has ~2,400 completed-family historical trajectories spanning ~125,000 family-week records from which these transitions can in principle be learned.

**The problem is sequential and partially observable in the dynamics sense:**
- Decisions are made weekly (multi-period, 52 rounds).
- Each family's status evolves as a stochastic process that depends on both whether they were visited and on their unobserved underlying features.
- Actions affect the state distribution at the next time step.

**Data-generating-process caveat flagged by the director:** historical visits were selected by caseworker judgement, not at random. This introduces **selection bias** in the observed (state, action, next-state) triples. Any learned predictive model fit naively to this data may misrepresent counterfactual dynamics (what would have happened with a different policy).

**Information structure at decision time each week:** observable — current status `s_{i,t}` of every family and their intake features `x_i`. Hidden — the true per-family transition matrix `P_i(s' | s, a)`.

## Scale

- Decision variables (per week): ~800 binaries
- Decision variables (full horizon): ~41,600 binaries
- Hard constraints (per week): 1 capacity + 800 binary-domain = 801
- Time horizon: **multi-period, 52 rounds**, with decisions and observations alternating each week

## Assumptions Made

1. **Independence of families given features and actions.** Assumed that, conditional on the per-family features and action, each family's status trajectory is independent of other families'. The director did not describe meaningful spillovers between families; this is a common and reasonable modelling assumption here.
2. **Stationarity of the transition structure over the 52-week horizon.** Assumed that the relationship `s_{i,t} → s_{i,t+1}` given features and action does not drift mid-year. The director did not suggest seasonal or calendar effects.
3. **Welfare reward depends only on the current state, not on the action directly.** The director described success as time spent in stable vs crisis — the visit itself is not directly rewarded.
4. **Soft constraints (geography, language, continuity) can be relaxed in a first cut**, with the optimisation run on the core capacity constraint only, and a second-pass assignment step handling the caseworker-to-family matching once the weekly visit set is chosen.

## Open Questions

- What value should `c` (crisis-week weight) take? The director said "more heavily" but did not give a number. 2× stable? 5×? 10×? This affects the ranking of which families the system prioritises.
- Should the state space be richer than 3 levels? (E.g., separate "at-risk" into housing-risk, employment-risk, family-risk sub-flags.) This is a modelling choice that trades off fidelity against data sparsity.
- Does the organisation want a **live** adaptive system (weekly re-planning based on updated state) or a **static** plan computed once and executed? The director's framing ("decide each week which 40 to visit") points strongly at live re-planning.
- How strictly must the soft geography constraints be respected in production? If they're effectively hard (caseworker rosters are not reshuffled weekly), the problem should be solved at the sub-region level independently.
