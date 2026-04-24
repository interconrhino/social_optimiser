# Formal Problem Specification

**Session:** 0006
**Domain:** Workforce development / economic inclusion (multi-year placement policy design)

## Decision Variables

The object being chosen is a **policy** π, not a single allocation. The policy maps the current system state to a quarterly allocation.

Let:
- G = {school-leavers, mid-career displaced, returners, justice-affected}, |G| = 4
- P = {green energy, advanced manufacturing, allied health, logistics}, |P| = 4
- T = {1, …, 20} (quarters)
- s_t ∈ S: the state at the start of quarter t (backlog per group, active apprentices per group × sub-programme, employer-relationship state per group, staff-hours remaining, slot capacity realised for the quarter)

**Primary decision variables (per-quarter allocation, induced by the policy):**
- x_{g,p,t} ∈ ℤ₊ for g ∈ G, p ∈ P, t ∈ T — integer count of slots allocated to group g in sub-programme p in quarter t. Non-negative integer, bounded by available slot capacity.

**The object actually chosen:**
- π : S → ℤ₊^{|G|×|P|} — a state-dependent decision rule. The policy is the decision variable; x_{g,p,t} = π(s_t) is its application at each quarter. Policies may be parameterised (e.g., by share-vectors, priority weights, or thresholds) for tractable search.

**Second-level choice (preference vector):**
- λ ∈ Λ ⊂ ℝ^k — a **stance parameter** indexing where on the fairness-vs-totals spectrum the board sits. Λ is designed to cover utilitarian, Rawlsian, and egalitarian stances with interpretable intermediate points. The deliverable is a small set {π*(λ₁), …, π*(λ_M)} with M ∈ [3, 10], each π*(λ_i) being the best policy under stance λ_i.

## Objective Function

**Direction:** Maximise (under each chosen stance).

**What:** For a given stance λ, maximise a stance-dependent scalarisation of the four group-level outcome trajectories produced by running policy π against the simulator over 20 quarters.

Let **y_g(π)** = expected cumulative (or appropriately discounted) successful sustained placements for group g ∈ G over the 20-quarter horizon, computed by the trusted simulator under policy π. This gives a 4-vector **y(π) = (y_{school}, y_{displaced}, y_{return}, y_{justice})**.

**Form (parameterised by stance λ):**

`π*(λ) = argmax_{π ∈ Π} U_λ( y(π) )`

where U_λ is the stance-specific social welfare function. Three canonical stances are explicitly named by the user:

- **Totals (utilitarian):** `U_total(y) = Σ_g y_g`
- **Worst-off (Rawlsian / maximin):** `U_rawls(y) = min_g y_g` (or a smoothed/weighted variant, e.g., α-fair with large α)
- **Balanced (proportional / egalitarian):** a function that penalises inter-group disparity — e.g., `U_bal(y) = Σ_g y_g − β · Var_g(y_g / n_g)` or a Nash-product `Π_g y_g^{w_g}`.

These three stances correspond to well-known points on the **α-fair / CES family** of social welfare functions, which provides a natural one-parameter family interpolating between them — giving a principled way to generate the intermediate menu entries.

The menu deliverable is:
`MENU = { π*(λ₁), π*(λ₂), …, π*(λ_M) }` for M ∈ [3, 10] stance points chosen to cover the stance spectrum non-redundantly (each π*(λ_i) meaningfully different from neighbours in outcome space).

## Constraints

| # | Constraint | Type | Form |
|---|---|---|---|
| 1 | Quarterly slot capacity | Hard | Σ_{g,p} x_{g,p,t} ≤ C_t for all t, with C_t ∈ [400, 600] |
| 2 | Caseworker-hour budget per quarter | Hard | Σ_{g,p} h_g · x_{g,p,t} ≤ H_t for all t (h_g = caseworker hours per placement for group g; higher for justice-affected) |
| 3 | Non-negativity and integrality | Hard | x_{g,p,t} ∈ ℤ₊ |
| 4 | Pipeline-state dynamics | Hard (governed by simulator) | s_{t+1} = f(s_t, x_{·,·,t}, ξ_t) — simulator-defined transition over backlogs, active apprentices, employer-relationship state; ξ_t captures stochastic elements |
| 5 | Group eligibility and backlog bounds | Hard | x_{g,·,t} ≤ available eligible intake for group g at quarter t (from state s_t) |
| 6 | Sub-programme-specific employer slot caps | Hard | x_{·,p,t} ≤ E_{p,t}(s_t) — employer-side availability per sub-programme, state-dependent because of employer-relationship decay |
| 7 | Policy representation constraint (implementation) | Soft / structural | π must belong to an interpretable, implementable policy class (e.g., parameterised priority rules, share-vector policies, or a trained neural/tree policy) so the board can see and audit it |
| 8 | Menu diversity / coverage | Structural (on the menu, not on each π) | The M selected stance points must (i) each yield a distinct, near-optimal policy under its stance, and (ii) collectively span the α-fair (or equivalent) parameter range |

## Parameters (Known Inputs)

| Parameter | Description | Certainty |
|---|---|---|
| C_t | Slot capacity in quarter t | Estimated; forecast from employer commitments & funding |
| H_t | Staff-hour budget in quarter t | Known / planned |
| h_g | Caseworker-hours per placement for group g | Estimated from 9 years of operational data |
| Intake arrival rates by group | New candidates per group per quarter | Estimated; stochastic |
| Outcome success rates per (group, sub-programme) | Probability of sustained placement | Estimated from 9-year history + 14k participant records |
| Employer-relationship decay/renewal dynamics | How current-quarter reliability affects future slot supply | Encoded inside the simulator |
| α / stance parameters λ | Weighting of fairness vs totals | **Deliberately varied** — this is the menu axis |
| Horizon T | 20 quarters | Known |
| |G|, |P| | 4 groups, 4 sub-programmes | Known |

## Uncertainty Structure

- Intake arrivals per group, per-placement success probabilities, and employer slot renewal are **stochastic**, encoded in the commissioned simulator which the board trusts for scenario comparison.
- The simulator is the ground-truth evaluator: **each candidate policy is scored by simulator rollouts** (Monte-Carlo-style over the stochasticity).
- This is effectively a **sequential decision problem under uncertainty with a trusted simulator** — the state evolves stochastically, decisions affect future state, and the evaluation is done by rollout rather than closed-form.
- Partial observability is not emphasised in the brief (the agency observes its own placements and outcomes); the primary uncertainty is stochastic transition + intake.
- Crucially, **the stakeholder objective is multi-dimensional and the weighting across the four dimensions is itself uncertain** (different boards, different governments). This motivates producing a **menu** of policies indexed by a stance parameter, not a single optimal policy.

## Scale

- Decision variables per quarter (raw integer allocation): 4 × 4 = 16.
- Raw open-loop action-vector length over horizon: 16 × 20 = 320.
- Policy space: much larger — a space of decision rules S → ℤ₊^{16}. Tractable search requires restricting to a parameterised policy class (e.g., share-vector policy with priority weights, or a shallow neural/tree policy).
- Simulator evaluations: each scalar objective score requires N Monte-Carlo rollouts of 20 quarters → roughly the expensive unit of compute.
- Menu size: M ∈ [3, 10] — so we need M well-chosen stance points, each solved for a near-optimal policy.
- Time horizon: multi-period (20 rounds), closed-loop (state-dependent policy).

## Assumptions Made

1. The commissioned simulator is usable as a black-box oracle f: (π, seed) → trajectory of group-level outcomes, and we can run it many times. The user explicitly stated the board trusts it for scenario comparison.
2. The three named ethical stances (totals / worst-off / balanced) fit cleanly on a one-parameter α-fair (or equivalent CES) family of social welfare functions, which lets us index the menu with a small number of stance points covering the spectrum.
3. We are treating groups as the planning unit (the user stated "our planning unit is the group, not the individual").
4. The policy class will need to be restricted to something interpretable and implementable (structural constraint #7). This is a modelling decision we should confirm with the user before implementation.
5. We assume y_g(π) is well-defined as the expected 20-quarter cumulative successful sustained placements for group g under π; the exact form (cumulative, discounted, time-averaged) can be tuned but does not change the structural specification.

## Open Questions

- Should group-level outcomes be weighted by group size (per-capita) or taken raw? This changes what "balanced" means and should be surfaced to the board.
- Does the agency want the policy to be a simple interpretable rule (e.g., fixed share vector adjusted by backlog thresholds) or is a black-box policy acceptable if its stance-conditional outcome curves are shown to the board?
- How noisy is the simulator? (Affects how many rollouts per candidate policy, and whether noise-aware search is needed.)
- Are there any hard political/legal floors on group allocations (e.g., statutory minimum for justice-affected adults)? These would become hard constraints on every policy in the menu, independent of stance.
