# Formal Problem Specification

**Session:** 0004
**Domain:** Education (student-success / retention outreach)

## Decision Variables

Let the indexing be:
- `i ∈ {1, ..., N_t}` — students currently on the at-risk watch-list in week `t` (typical N_t ≈ 2,100 across the network; with per-campus subsets).
- `c ∈ {1, 2, 3, 4}` — campuses.
- `t ∈ {1, ..., T}` with `T = 12` — weekly decision epochs per semester.

Primary decision variable:
- **`x_{i,t} ∈ {0, 1}`** — **binary**. Equals 1 if student `i` is called in week `t`, 0 otherwise. Defined for every student `i` currently on campus `c(i)`'s watch-list in week `t`.

Per week, the vector `x_t = (x_{1,t}, ..., x_{N_t,t})` is the weekly call list.

Total per-semester decisions: T × (average weekly watch-list size) ≈ 12 × 2,100 ≈ 25,200 binary decisions (re-solved weekly as new information arrives).

## Objective Function

**Direction:** Maximise

**What:** A weighted combination of (a) expected total retained/engaged students over the 12-week semester and (b) a clause-satisfaction score derived from the semester's plain-English priority paragraph, with a selectable scalarisation mode (weighted-sum / max-min over clauses / lexicographic).

**Form:**

Primary objective (semester-long expected engagement gain from calls):

```
maximise  E[ Σ_{t=1..T} Σ_{i ∈ W_t} r_{i,t}(x_{i,t}, s_{i,t}) ]
```

where:
- `W_t` = watch-list in week `t`,
- `s_{i,t}` = latent engagement/at-risk state of student `i` in week `t` (not directly observed),
- `r_{i,t}(·)` = expected contribution to end-of-semester retention/engagement from action `x_{i,t}` given state `s_{i,t}`.

Concurrently, for each clause `k = 1..K` of the priority paragraph, define a clause-satisfaction score:

```
C_k(x) = f_k( { x_{i,t} } , demographic attributes of i )
```

e.g. `C_k = Σ_{i ∈ G_k, t} x_{i,t} / Σ_{i ∈ G_k, t} 1` (coverage of group G_k) or a relative-to-baseline preservation score.

The system must support three composed objectives, selectable by leadership:

1. **Weighted sum**: `maximise α · Retention(x) + Σ_k β_k · C_k(x)` with user-set weights.
2. **Max-min over clauses**: `maximise min_k C_k(x)` subject to a retention floor.
3. **Lexicographic / ε-constraint**: `maximise Retention(x)` subject to `C_k(x) ≥ τ_k ∀ k`.

All three produce an explicit *per-clause* dashboard so the board can see how each clause is honoured.

## Constraints

| # | Constraint | Type | Form |
|---|---|---|---|
| 1 | Total network call capacity per week | Hard | `Σ_i x_{i,t} ≤ B = 210` for every `t` |
| 2 | Per-campus call capacity per week | Hard | `Σ_{i : c(i)=c} x_{i,t} ≤ B_c` for each campus `c`, with `Σ_c B_c = 210` |
| 3 | Binary decisions | Hard | `x_{i,t} ∈ {0,1}` |
| 4 | Eligibility: only students on the week-`t` watch-list can be called | Hard | `x_{i,t} = 0` if `i ∉ W_t` |
| 5 | Clause preservation floors (from priority paragraph) | Soft (or Hard, at leadership's choice) | `C_k(x) ≥ τ_k` for each clause `k` — e.g. coverage of adult learners ≥ last-semester level |
| 6 | Unintended-side-effect guards (demographic slices not named in the paragraph) | Soft (monitoring) | `|coverage_g(x) − baseline_g| ≤ δ` for monitored slice `g` (flag if violated) |
| 7 | Auditability / transparency | Non-mathematical, meta | The decision rule must be describable as a computable recipe; per-clause scores must be reportable |

## Parameters (Known Inputs)

| Parameter | Description | Certainty |
|---|---|---|
| `B = 210` | Total weekly network call capacity | Known |
| `B_c` | Per-campus weekly capacity | Known |
| `T = 12` | Number of weekly decision epochs | Known |
| `W_t` | Week-`t` watch-list (set of flagged students) | Known each week |
| Student features (age band, income band, first-gen, home campus, programme, dependants, prior-term GPA band, distance band) — 8–12 per student | Demographics and intake data | Known |
| `y_{i,t} ∈ {0,1}` | Weekly engagement proxy (LMS + assignment submission) | Observed (noisy proxy for latent state) |
| Historical call log (3 years, ~12,000 students) | Past actions by coaches | Known but **biased** (non-random assignment) |
| `{G_k}`, `{τ_k}`, `{β_k}` | Groups / floors / weights implied by the semester's priority paragraph | Estimated — requires translation from plain English |
| `p(s_{i,t+1} | s_{i,t}, x_{i,t})` | Transition dynamics of latent engagement under call / no-call | Estimated from data (off-policy) |
| `p(y_{i,t} | s_{i,t})` | Observation model linking latent state to observed proxy | Estimated |

## Uncertainty Structure

This problem is **sequential and partially observed**.

- **Latent state**: each student's true engagement / risk level `s_{i,t}` is not directly observed; only the noisy weekly proxy `y_{i,t}` plus slow-moving demographics are seen.
- **Dynamics**: `s_{i,t}` evolves week to week. A call intervenes in that dynamic — students called this week have different future trajectories than those not called. So the problem is inherently dynamic per-student, not a one-shot ranking.
- **Inter-student independence (working assumption)**: absent evidence of peer effects, the evolution of one student's state given the action on them is assumed independent of other students' states, conditional on features. (Calls compete only through the shared weekly budget.)
- **Off-policy / biased historical data**: call log is not a randomised trial. Any estimate of call-effect and transition dynamics must correct for selection bias in past coaching decisions.
- **Priority paragraph uncertainty**: the mapping from plain-English clauses to `(G_k, τ_k, β_k)` is itself uncertain and may be revised during the semester.
- **Entry/exit**: students enter and leave the watch-list `W_t` over weeks.

**Problem is therefore sequential, stochastic, partially observed, with a shared resource (call budget) coupling otherwise per-student decisions across a population.**

## Scale

- Decision variables: ~2,100 binary variables per weekly decision × 12 weeks (re-solved each week; ~25,200 total binaries across a semester).
- Constraints per week: 1 network-capacity + 4 per-campus capacity + eligibility + K clause-floor constraints (K small, ≈ 3–6) → small constraint count but over many students.
- Time horizon: **Multi-period (12 weekly rounds) with re-optimisation each week as new data arrives.**
- Per-student: modest state space (engagement proxy + slow demographics) but large *population* (~2,100 concurrently in play).

## Assumptions Made

1. **Decision granularity is one binary per (student, week)**, not a coach-level scheduling decision. User confirmed coach-to-student assignment is out of scope.
2. **Calls are fungible within a campus** (any coach on a campus can take any student on that campus's list, to first approximation).
3. **Per-campus capacities sum to the network capacity of 210**, and both must be respected. Exact per-campus split was not given — treated as a known input.
4. **Inter-student independence** of engagement dynamics given features (no peer-effects modelling).
5. **Call effect is student-specific and state-specific** (some students benefit more from a call at certain risk levels than others); this is what the historical data is used to estimate.
6. **The priority paragraph can be decomposed into K clauses**, each mapped to (group, direction, target level); this translation is explicit and auditable.
7. **Side-effect monitoring is a reporting layer**, computed over all "meaningful" demographic slices (not just the ones named in the paragraph).

## Open Questions

- Exact per-campus weekly capacity split `B_c` — leadership can set, but has not been stated.
- Whether calls to the same student in consecutive weeks are allowed or discouraged (a cooldown policy). The brief implies "a student we call this week might stabilise and not need another call for a month" — suggesting an implicit, not enforced, cooldown.
- Whether funders' expectations allow the max-min / weighted-sum / ε-constraint choice to be made centrally, or whether each funder demands a specific one.
- Degree of off-policy bias in historical call logs — needs empirical diagnosis before relying on learned transition/reward estimates.
