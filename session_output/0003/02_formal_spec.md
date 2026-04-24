# Formal Problem Specification

**Session:** 0003
**Domain:** social welfare / case management (economic inclusion & well-being of newly-arrived refugee families)

## Decision Variables

Let **F** = set of active families, |F| ≈ 800.
Let **T** = {1, 2, …, 52} = weeks in the planning horizon.

- **x_{i,t}** ∈ {0, 1} — binary. Equals 1 if family i ∈ F is visited by a caseworker in week t ∈ T, 0 otherwise.

A policy / decision rule **π** specifies, for each week t and each possible information state at the start of week t, which 40 families to visit — i.e. π maps state → a vector (x_{1,t}, …, x_{|F|,t}) with exactly 40 ones.

### Auxiliary (latent / derived, not chosen) state variables

- **s_{i,t}** ∈ {Stable, At-risk, Crisis} — the situation of family i at the start of week t. Evolves stochastically; not directly chosen. Transitions depend on whether the family is visited, on family-specific features / history, and on the previous state.

## Objective Function

**Direction:** Maximise
**What:** Expected aggregate family welfare across the cohort over the 52-week horizon, defined as the total family-weeks spent in the Stable category minus a weighted count of weeks in Crisis.
**Form:**

maximise_{π} E_π [ Σ_{t=1..52} Σ_{i ∈ F} ( 1{s_{i,t} = Stable} − w · 1{s_{i,t} = Crisis} ) ]

where:
- E_π[·] is expectation over the stochastic trajectories of family states under policy π
- w ≥ 1 is the user-supplied crisis penalty weight ("we weight crisis weeks more heavily because the damage lasts")
- 1{·} is the indicator function.

The At-risk state contributes 0 directly, though it matters because it predicts future transitions.

## Constraints

| # | Constraint | Type | Form |
|---|---|---|---|
| 1 | Exactly 40 visits per week (one per caseworker) | Hard | Σ_{i ∈ F} x_{i,t} = 40, for every t ∈ T |
| 2 | Each family receives at most one visit per week | Hard | x_{i,t} ∈ {0, 1} (by construction) |
| 3 | Visits are non-anticipative — the week-t decision can depend only on information observable up to the start of week t | Hard | x_{i,t} is a function of history H_t, not of future realisations |
| 4 | Plausible equity / duty-of-care floor (flagged by intake, not numerically specified by user): no family should go more than K weeks without a visit | Soft (user-configurable; not a stated hard constraint, but must be surface-able) | Σ_{τ = t−K+1..t} x_{i,τ} ≥ 1 for all i, t ≥ K |
| 5 | Caseworker capacity of one visit per week per caseworker | Hard (already encoded by the total of 40) | (aggregated into #1) |

Assignment of specific caseworkers to specific families (routing / territory) is explicitly treated as downstream and out of scope for this optimisation.

## Parameters (Known Inputs)

| Parameter | Description | Certainty |
|---|---|---|
| |F| ≈ 800 | active-family cohort size | Known |
| C = 40 | caseworker weekly visit capacity | Known |
| T = 52 | weekly horizon | Known |
| w | crisis penalty weight (Stable-week = +1, Crisis-week = −w) | User-set; known |
| φ_i | intake feature vector for family i (country, family composition, languages, employment/education, trauma score, neighbourhood, co-arrival cohort, medical history) | Known |
| P(s_{i,t+1} | s_{i,t}, x_{i,t}, φ_i, history) | per-family state-transition kernel: probability that family i is in a given state next week, conditional on current state, whether visited this week, and features | **Estimated** from ~2,400 historical family trajectories; confounded by past caseworker priority decisions |
| effect of a visit | reduction in probability of transitioning Stable→At-risk or At-risk→Crisis; varies across families and states | Estimated |
| drift rate without visit | depends on vulnerability features (e.g. single caregiver, no English, trauma score) | Estimated |

## Uncertainty Structure

- **What is uncertain:** the future trajectory (s_{i,1}, s_{i,2}, …, s_{i,52}) of every family. Concretely: the transition probabilities between Stable, At-risk, and Crisis, both with and without a visit, for each family.
- **How it is modelled:** as a per-family **stochastic process on a 3-state space** (Stable / At-risk / Crisis), where transition probabilities depend on (i) current state, (ii) whether a visit occurs this week, and (iii) family-specific features and history. Transitions across families can be treated as independent conditional on the information we have (a standard simplification, though neighbourhood-level correlation is a noted second-order concern).
- **Partial observability:** state is fully observed only during a visit. Between visits, the programme infers state from caseworker notes, referrals, and elapsed time. A common simplification is to treat state as observable each week via recent-enough contact + features; a more complete formulation would treat the between-visit state as only partially observed (belief state updated via Bayes' rule using intake features, last observed state, and time since last contact).
- **Sequential decision-making:** yes — decisions are made weekly for 52 rounds; each week's information (updated family statuses from visits and from any crisis events surfaced through other channels) feeds the next week's decision.
- **Estimation uncertainty:** transition model is learned from **observational (non-randomised)** data. Past visit assignments depended on caseworker judgement, so naive estimation of "visit effect" is confounded. Causal-inference care (e.g. doubly-robust estimation, or careful propensity adjustment) is needed upstream of the scheduler.

## Scale

- **Decision variables per week:** |F| ≈ 800 binaries, of which exactly 40 must equal 1 — i.e. the weekly action space has size C(800, 40), astronomically large, so any method must exploit structure (e.g. per-family priority indices) rather than enumerate joint actions.
- **Decision variables over the horizon:** ≈ 800 × 52 = 41,600 binaries, embedded in a policy (not a static schedule) because each week's selection should respond to the updated state of the cohort.
- **Constraints:** 52 weekly-capacity constraints (equality), plus per-week per-family binary domain, plus non-anticipativity, plus (optional) ~800 × 52 coverage-floor constraints if a maximum-gap equity rule is adopted.
- **Time horizon:** Multi-period, 52 weekly rounds, closed-loop (policy, not open-loop plan).

## Assumptions Made

1. **Families' transitions are conditionally independent** across families given their features and states. Flagged for validation; neighbourhood-level correlated shocks may require a richer model.
2. **State is approximately observable each week** for the purpose of scheduling (via last visit + time-since + features + any surfaced crisis signals). A fully partially-observed formulation is possible but not required by the brief.
3. **A family's transition kernel depends only on its own state, visit, and features** — i.e. no coupling through caseworker identity or neighbourhood. Caseworker-to-family assignment is a separate downstream problem.
4. **Visit capacity is a hard equality** (= 40), not ≤ 40. The user's wording implies full utilisation of caseworker time each week.
5. **The crisis weight w is a single user-set scalar**; the user did not name it but explicitly described "weighted more heavily". Sensitivity analysis in w is expected.
6. **Equity / coverage floor** is included as a soft, configurable constraint rather than hard, because the user did not specify one — but a responsible recommendation must expose the knob.

## Open Questions

- What numeric value should w take? (Sensitivity analysis recommended.)
- Should the system support a strict max-gap rule (e.g. "no family unvisited for more than 8 weeks")? If so, what value of K?
- Should the 40-per-week capacity be treated as exactly-40 or up-to-40?
- Do we need to plan explicitly for new arrivals mid-year (cohort is dynamic) or treat |F| as piecewise-constant over the pilot?
- Is there any family-subset the programme is required to visit every week regardless of model output (e.g. flagged safeguarding cases)?
