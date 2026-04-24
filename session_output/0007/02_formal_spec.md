# Formal Problem Specification

**Session:** 0007
**Domain:** Food security / smallholder agriculture (climate-smart advisory retention)

## Decision Variables

Let:
- `N` ≈ 28,000 = set of enrolled farmers, indexed by `i ∈ {1, …, N}`.
- `T` ∈ {6, 7, 8} = number of monthly decision epochs in the pilot window, indexed by `t ∈ {1, …, T}`.
- `K` = 400 = personal follow-up call budget per month.

**Primary decision variable:**
- `a_{i,t} ∈ {0, 1}` (**binary**) — 1 iff farmer `i` is selected for a proactive advisor follow-up call in month `t`, 0 otherwise.

At every epoch `t`, the policy observes the prior history and must choose an **action vector** `a_t = (a_{1,t}, …, a_{N,t})` satisfying the per-period budget.

## Objective Function

**Direction:** Maximise

**What:** Total expected number of farmer-months of *active engagement* (i.e., farmer actually listens to the monthly automated voice message) accrued across the pilot window, summed over all farmers and all months.

**Form (schematic):**

```
maximise  E[ Σ_{t=1..T} Σ_{i=1..N}  Listen_{i,t}(a_{1..t}, history) ]
```

where `Listen_{i,t} ∈ {0, 1}` is a random variable (1 if farmer `i` listens in month `t`) whose distribution depends on (a) the farmer's latent engagement state, (b) whether a personal call has been placed, and (c) seasonal context. The expectation is taken over the stochastic evolution of each farmer's engagement state and the stochastic response to calls.

**Note on cumulative vs single-month credit:** The user explicitly stated they value cumulative engagement across the window, not any one month — so the objective is a sum across `t`, not a terminal-month indicator.

## Constraints

| # | Constraint | Type | Form |
|---|---|---|---|
| 1 | Per-month call budget: at most 400 proactive calls can be placed | **Hard** | `Σ_{i=1..N} a_{i,t} ≤ K = 400`  ∀ t |
| 2 | Binary selection: farmer is either called or not in a given month | **Hard** | `a_{i,t} ∈ {0,1}`  ∀ i, t |
| 3 | Equity / coverage: no village `v` or language group `g` is systematically under-served over the window | **Soft / side-constraint** | e.g., `Σ_{t} Σ_{i ∈ v} a_{i,t} / |v| ≥ α · (K·T / N)`  for some fairness floor α ∈ (0, 1] |
| 4 | Helpline calls are additional and not counted against the 400-quota | **Hard (scoping)** | The 400-quota covers only *proactive* selections; helpline-triggered calls are exogenous. |
| 5 | Explainability: the selection rule must produce, for each farmer-month decision, a reason stateable to an advisor / auditor | **Hard (non-mathematical)** | Encoded as a preference for transparent scoring / ranking rules over opaque ones. |

## Parameters (Known Inputs)

| Parameter | Description | Certainty |
|---|---|---|
| `N` (≈28,000) | Enrolled farmer count | **Known** (growing, but known each month) |
| `K` (=400) | Monthly call budget | **Known** |
| `T` (∈6..8) | Pilot horizon in months | **Known** (board-approved pilot design) |
| Monthly listen history `L_{i,s}` for s<t | Binary + duration | **Known** (5 years of logs) |
| Historical call indicator `c_{i,s}` for s<t | Whether farmer was called in month s | **Known** |
| Farmer attributes (district, village, language, age band, farm size, crop mix, phone type, distance to office, collective membership) | Static covariates | **Known** |
| District-level rainfall and market prices | Seasonal context by month | **Known** |
| Per-farmer "engagement state" (latent propensity to listen next month) | The unobservable driver of `Listen_{i,t}` | **Unknown / to be inferred** |
| Transition dynamics of engagement state with and without a call | How state evolves when called vs not called | **Unknown / to be estimated, but estimation is *confounded* by the historical rotation-plus-helpline policy** |

## Uncertainty Structure

This problem has **two interacting sources of uncertainty**:

1. **Partial observability of the per-farmer engagement state.** We observe a noisy proxy (did they listen this month? for how long?) but the underlying willingness-to-engage state — shaped by life circumstances, season, trust in the programme — is latent. State evolves stochastically month to month.

2. **Unknown (and confounded) effect of a personal call on future engagement.** The historical data was generated under the rotation policy plus ad-hoc helpline calls, not random assignment. So the conditional effect of being called on next-month listening is not cleanly identifiable from observational data alone; the pilot's control arm is explicitly needed to pin this down.

**Sequential structure:** This is a **multi-period problem with information revealed between rounds.** Each month the policy observes the latest listen outcomes and then chooses the next 400 calls. There are ~6–8 such decision rounds in the pilot.

**Heterogeneity:** Each farmer is an independent "unit" whose state evolves over time. The joint problem has ~28,000 coupled-only-by-the-budget subproblems per month.

## Scale

- Decision variables per month: ~28,000 binaries; over 8 months, ~224,000 decision variables total.
- Constraints: 8 budget constraints (one per month), plus equity floors per village × language group (low dozens of groups).
- Time horizon: **Multi-period, 6–8 rounds, sequential with observation between rounds**.

## Assumptions Made

1. The per-farmer engagement state evolves approximately Markovian given observed covariates and listen history — i.e., "recent listening pattern + attributes" is a reasonable sufficient statistic for near-term propensity. The user did not volunteer this assumption; we flag it here because it materially shapes what can be modelled.
2. Calls are independent across farmers (no spillover through the village-level peer network in the call channel itself). Calls don't reach a farmer's neighbour. This is consistent with the brief's description.
3. Call capacity (400) is a hard monthly cap and roughly fungible across advisors and districts at the planning level — routing of the 400 across the 12 advisors is an operational post-processing step, not part of the optimisation.
4. Listening to the automated message is a sufficient short-horizon proxy for the ultimate outcomes (yield, pesticide use, income). The user made this connection explicitly.

## Open Questions

1. How many farmers per month is the org willing to "freeze" for a clean randomised control arm in the pilot, and for how long? (This affects identifiability, not the optimisation structure.)
2. Are there any farmers the org would *never* want skipped (e.g., those currently in acute distress)? If so, those become must-call side-constraints.
3. What is the minimum inter-call cooldown (should a farmer not be called two months in a row, or is that acceptable if the policy recommends it)?
4. The fairness floor `α` — what concrete level of per-village/per-language minimum coverage does the org want to guarantee? The user said "must not quietly cut off" groups, but hasn't picked a numerical floor.
