# Optimisation Recommendation — Formal Specification

**Session:** 0006
**Problem domain:** Workforce development / economic inclusion (multi-year placement policy design)
**Technique:** Multi-objective Optimisation via α-fair (p-mean) scalarisation over a curated menu of stance points
**Algorithm:** α-fair scalarisation sweep + CMA-ES simulation-based policy search (inner solver), with AUGMECON2-style ε-constraint as an interchangeable inner formulation for floor-expressed stances

---

## 1. Problem Formulation

### Sets and indices
- G = {school-leavers, mid-career displaced, returners, justice-affected}, |G| = 4
- P = {green energy, advanced manufacturing, allied health, logistics}, |P| = 4
- T = {1, …, 20} (quarters over a 5-year horizon)
- Λ = α-ladder of stance points, |Λ| = M, M ∈ [3, 10]

### Decision Variables

**Primary (policy):**
- `π_θ : S → ℤ₊^{|G|×|P|}` — a parameterised, state-dependent quarterly allocation rule, θ ∈ ℝ^d with d ≈ 20–50. Concrete example: share-vector parameters `w_{g,p}` per (group, sub-programme) pair, modulated by backlog-pressure coefficients `β_g` so that under-served groups get a dynamic boost. θ is continuous; the policy output is integer (rounding + capacity-respecting projection).

**Induced (per-quarter allocation when π_θ is rolled out):**
- `x_{g,p,t} ∈ ℤ₊` — slots allocated to group g in sub-programme p in quarter t; determined by π_θ(s_t).

**Outer (stance selector):**
- `α ∈ Λ` — scalarisation parameter indexing the stance. The deliverable is the map α ↦ π*(α).

### Objective Function

**Maximise** a stance-dependent scalarisation of the four group-level 20-quarter outcome trajectories produced by the simulator.

Let `y_g(π_θ) = E[ Σ_{t=1}^{20} successful_sustained_placements_{g,t}(π_θ) ]`, estimated by averaging N Monte-Carlo simulator rollouts.

For each stance α, solve:

`π*(α) = argmax_{θ} W_α( y(π_θ) )`

where the **α-fair (p-mean) social welfare function** is:

```
W_α(y) = ( (1/|G|) Σ_g y_g^{1-α} )^{1/(1-α)}   for α ≥ 0, α ≠ 1
W_1(y) = ( Π_g y_g )^{1/|G|}                    (Nash / proportional-fairness limit)
W_∞(y) = min_g y_g                              (Rawlsian / max-min limit)
```

**Named stance points on the α-ladder:**
| α | Name | Meaning |
|---|---|---|
| 0 | Utilitarian (totals) | Maximise the sum Σ_g y_g |
| 0.5 | Mildly egalitarian | Slight concavity; tempered totals |
| 1 | Proportional / Nash | Maximise Π_g y_g — strongly equity-aware but efficiency-respecting |
| 2 | Strongly egalitarian | Heavily penalises inter-group disparity |
| 5 | Near-Rawlsian | Approaches max-min while preserving smooth gradients |
| ∞ | Rawlsian (worst-off) | Maximise min_g y_g |

This six-point ladder is the default menu; the board can request more or fewer points.

### Constraints

| Label | Plain language | Symbolic |
|---|---|---|
| **Capacity** | Total slots allocated per quarter ≤ available slot capacity | `Σ_{g,p} x_{g,p,t} ≤ C_t` ∀ t, C_t ∈ [400, 600] |
| **Caseworker budget** | Caseworker hours used ≤ staff-hour budget | `Σ_{g,p} h_g · x_{g,p,t} ≤ H_t` ∀ t |
| **Integrality** | Slot counts are non-negative integers | `x_{g,p,t} ∈ ℤ₊` |
| **Pipeline dynamics** | State evolves per the commissioned simulator | `s_{t+1} = f(s_t, x_{·,·,t}, ξ_t)` — simulator-defined |
| **Eligibility / backlog** | Can't place more than the eligible backlog of a group | `Σ_p x_{g,p,t} ≤ BacklogAvailable_{g,t}(s_t)` ∀ g, t |
| **Employer slot caps** | Each sub-programme can't exceed employer-side availability, which decays with unreliable placements | `Σ_g x_{g,p,t} ≤ E_{p,t}(s_t)` ∀ p, t |
| **Statutory floors (if any)** | Any legally mandated group minimums must hold for every policy on the menu | `Σ_p x_{g,p,t} ≥ F_{g,t}` ∀ g, t (only if applicable; to confirm with user) |
| **Menu diversity** | Menu entries must be meaningfully different in outcome space | `‖ y(π*(α_i)) − y(π*(α_j)) ‖ ≥ δ` ∀ i ≠ j (post-hoc redundancy filter) |

### Parameters

| Symbol | Meaning | Value / Source |
|---|---|---|
| C_t | Slot capacity in quarter t | Forecast from employer commitments + funding |
| H_t | Staff-hour budget in quarter t | Internal budget |
| h_g | Caseworker-hours per placement, group g | Estimated from 9-year operational data |
| λ_{g,t} | Intake arrival rate, group g, quarter t | Estimated; stochastic |
| p_{g,p} | Success probability for (group, sub-programme) | Estimated from 9-year data + 14k participant records |
| E_{p,t}(·) | Employer slot availability function | Encoded in simulator |
| N | Monte-Carlo rollouts per evaluation | Tune via noise-calibration (suggested start: N = 50) |
| M | Menu size | 3–10 (user-chosen; default 6) |
| δ | Redundancy threshold in outcome space | Tune post-generation (suggested: 5% of best-observed trajectory norm) |
| d | Policy dimensionality | 20–50 (design choice; start small) |

### Uncertainty Structure

Intake arrivals, per-placement success, and employer slot renewal are stochastic. The commissioned simulator encapsulates all uncertainty and is used as a **black-box stochastic evaluator**: `y_g(π_θ) ≈ (1/N) Σ_{n=1}^N y_g^{(n)}(π_θ)` with independent random seeds. Policy search uses **common random numbers** within a CMA-ES generation to reduce variance on relative comparisons. Partial observability is not central (the agency observes its own placements and outcomes); the primary uncertainty is stochastic transition.

---

## 2. Recommended Algorithm

**Algorithm:** α-fair (p-mean) scalarisation sweep over a curated ladder of stance points, with CMA-ES as the inner derivative-free stochastic policy-search solver. Interchangeable inner formulation: AUGMECON2-style ε-constraint for stances the board prefers to express as floors.

**Class:** Multi-objective scalarisation + derivative-free simulation-based optimisation (outer: axiomatic social-welfare scalarisation; inner: evolution-strategy policy search against a black-box simulator)

### Why this algorithm

The three board-named stances (totals, worst-off, balanced) land exactly on well-studied points of the α-fair / p-mean family of social welfare functions, so a small α-ladder produces a curated menu where each entry has an *ethically named*, board-legible meaning — not an arbitrary Pareto point. α-fair scalarisation is Pareto-efficient for every α, so every menu entry is guaranteed non-dominated (modulo inner-solver approximation). The inner problem — a 20-quarter state-dependent policy evaluated by a trusted black-box simulator — is textbook territory for CMA-ES: moderate-dimensional, non-convex, noisy, and derivative-free. By restricting the policy class to an interpretable parameterisation (share vector + backlog-pressure terms, d ≈ 20–50), the approach stays within CMA-ES's empirical sweet spot and produces policies the board can read and audit. No neural-network training, no GPU infrastructure, no specialist RL expertise required — appropriate for a 3-person Python data team on an 8-month engagement, while leaving a clean upgrade path to welfare-aware MORL if the policy class proves limiting.

### Theoretical properties
- **Optimality (outer):** For every α ≥ 0, argmax W_α lies on the Pareto front — the α-fair family is axiomatically characterised as the unique family of monotonic, symmetric, scale-invariant social welfare functions satisfying the principle of transfers (Atkinson 1970; Mo & Walrand 2000).
- **Optimality (inner):** CMA-ES is derivative-free with no global guarantee on a non-convex simulator objective. Asymptotic local convergence under mild conditions; strong empirical performance on noisy black-box problems of this dimensionality.
- **Complexity:** M × (CMA-ES generations × population × rollouts-per-evaluation). With M = 6, d = 30, 200 generations, population ~12, N = 50, this is ~720k simulator rollouts — hours on a multi-core workstation if each rollout is sub-second; scale to a small cloud cluster otherwise.
- **Key references:**
  - Mo, J. & Walrand, J. (2000). *Fair End-to-End Window-Based Congestion Control.* IEEE/ACM Transactions on Networking. (α-fair axiomatic characterisation.)
  - Hansen, N. (2016). *The CMA Evolution Strategy: A Tutorial.* arXiv:1604.00772. (CMA-ES.)
  - Mavrotas, G. & Florios, K. (2013). *An improved version of the augmented ε-constraint method (AUGMECON2).* Applied Mathematics and Computation. (Alternative inner formulation.)
  - Hooker, J. (2021). *Fairness through Social Welfare Optimization.* arXiv:2102.00311. (Social-welfare-optimisation applied to fairness in algorithmic decision-making.)
  - Roijers, D.M. et al. (2022). *A practical guide to multi-objective reinforcement learning and planning.* Autonomous Agents and Multi-Agent Systems. (Survey framing for the sequential-decision side; upgrade path.)

### Known limitations
- **Simulator fidelity is the ceiling** — every number is conditioned on the simulator being right. Report *relative* differences between menu entries, not absolute outcome forecasts. Back-test the simulator on the 9 years of historical data.
- **Policy class restriction** — CMA-ES only finds the best policy *within* the parameterised class. If the class is too narrow, some menu entries may be suboptimal even under their own stance. Enrich the class iteratively; upgrade to welfare-aware MORL only if needed.
- **Evaluation noise** — simulator stochasticity can mislead CMA-ES if N (rollouts per evaluation) is too small. Use common random numbers and tune N via a preliminary noise-calibration study.
- **Redundancy in menu** — adjacent α values may produce near-identical outcome trajectories. Apply a post-generation redundancy filter (keep only entries differing by ≥ δ in outcome space) and optionally re-space the α-ladder.
- **Per-capita vs raw normalisation** — the "balanced/proportional" stance requires an explicit per-group normalisation choice; this is a modelling decision to surface to the board, not a hidden implementation detail.

---

## 3. Implementation Guidance

### Data Requirements

| Data item | Description | Format | Source suggestion |
|---|---|---|---|
| Simulator API | Input: policy callable; output: 4-group outcome trajectory over 20 quarters, seeded | Python callable | Existing — documented interface to the commissioned simulator |
| h_g | Caseworker hours per placement, by group | 4-vector | Derived from 9-year operational records |
| C_t, H_t forecasts | Slot capacity and staff-hour budget per quarter | 20-vector each | Internal planning + employer commitments |
| Historical back-test data | 9 years of quarterly allocations and outcomes | DataFrame | Existing operational records |
| Statutory floors F_{g,t} | Any legal minimums for any group | 4×20 matrix or 0 | Legal / compliance — confirm with user |
| Per-capita denominators | Intake volume or waitlist by group, if "balanced" is per-capita | Time series per group | Intake records |

### Key Parameters to Calibrate

- **α-ladder (stance points):** Default `{0, 0.5, 1, 2, 5, ∞}`. Sensitivity: high (this defines the menu). Adjust to taste — a denser ladder near α = 1 (proportional) is common if the balanced stance is politically central.
- **Policy dimensionality d:** Start at d = 16 (one share-vector entry per (group, sub-programme)) and extend to d ≈ 30–50 by adding backlog-pressure coefficients β_g and employer-relationship discount terms. Sensitivity: medium — too small misses good policies, too large slows CMA-ES.
- **Rollouts per evaluation N:** Start at N = 50 and tune via a noise-calibration study (increase until the CMA-ES selection ranking between top candidates is stable). Sensitivity: high on result reliability, linear on cost.
- **CMA-ES population size:** Default λ_CMA = 4 + ⌊3 ln d⌋ ≈ 12. Sensitivity: low; CMA-ES is robust to population choice.
- **CMA-ES generations:** 200–500 per stance. Sensitivity: medium — monitor convergence curves and early-stop.
- **Redundancy threshold δ:** Set post-generation as ~5% of the best-observed trajectory norm. Sensitivity: low to medium — affects menu cleanliness, not correctness.

### Algorithmic Steps

1. **Define the policy class.** Parameterise π_θ as a closed-form rule mapping (backlog_g, active_apprentices_{g,p}, employer_relationship_state_g, quarter-capacity C_t, staff budget H_t) → allocation x_{g,p,t}. A concrete starting form: softmax-weighted shares with additive backlog-pressure terms, projected to respect integrality and capacity.
2. **Wire up the simulator as an evaluator.** Write `evaluate(θ, N, seeds) → y ∈ ℝ^4`: roll out π_θ for 20 quarters over N random seeds, average group outcomes. Use common random numbers across candidates within one CMA-ES generation.
3. **Calibrate noise.** Pick a reference policy; measure variance of y across seeds; choose N so that the standard error of each y_g is below ~5% of its mean.
4. **For each α in the ladder** (parallelisable across stances):
   a. Define scalar objective `f_α(θ) = W_α( evaluate(θ, N, seeds) )`.
   b. Run CMA-ES on f_α for ~200–500 generations; record the best θ* and its y(θ*).
5. **Apply menu diversity filter.** Drop any α whose y(π*(α)) is within δ of a neighbour's; optionally re-space the α-ladder and re-run the dropped points.
6. **Package the menu.** For each surviving menu entry, produce: (i) the policy parameters θ*, (ii) a human-readable description of the policy's behaviour, (iii) the 20-quarter trajectory for each of the four groups (mean and uncertainty band from N rollouts), (iv) the stance label (α value + named stance).
7. **Validate.** Back-test each menu entry on the 9-year historical data (replay the simulator with historical intake and employer dynamics, scoring the policy against actual outcomes where comparable); run sensitivity analyses on C_t, H_t, and h_g ±20%.

### Computational Considerations
- **Expected cost:** ~10⁵–10⁷ simulator rollouts total (see theoretical section). Fully parallelisable across CMA-ES population and across stances.
- **Scaling behaviour:** Cost grows roughly linearly in M (menu size), linearly in generations, linearly in N, and roughly linearly in population (which grows as O(ln d)). Comfortable on a 16–64 core workstation or small cloud VM for typical parameterisations.
- **If scale grows** (more groups, more sub-programmes, longer horizon, more menu entries): first swap CMA-ES for Bayesian Optimisation with a GP surrogate (more sample-efficient when each rollout is expensive); if d grows beyond ~100, switch to welfare-aware MORL (Option 2 in research findings) with a neural or linear policy.

**Software:**
- `cma` (Python — Hansen's reference CMA-ES implementation) for the inner solver; drop-in alternatives are `pymoo` and `scikit-optimize`.
- `pymoo` for the outer multi-objective framework if the team prefers a single integrated package (it supports scalarisation, NSGA-III as a fallback, and evaluation bookkeeping).
- `scikit-optimize` / `BoTorch` if Bayesian Optimisation is preferred for the inner solver.
- All open-source, matches the user's strong preference.

---

## 4. Validation

### How to evaluate solution quality
For each menu entry π*(α):
- **Primary:** the α-fair welfare W_α( y(π*(α)) ) compared to (i) the organisation's current placement practice re-evaluated on the simulator, and (ii) a naive proportional-share baseline.
- **Diagnostic:** the 4-vector y(π*(α)) of group-level 20-quarter cumulative successful sustained placements, reported with Monte-Carlo uncertainty bands.
- **Menu-level:** coverage of the outcome space — verify the M menu entries span the totals-to-worst-off spectrum without redundancy.

### Baseline to beat
- **Naive baseline 1 (current practice):** the organisation's existing quarterly allocation rule, re-simulated with the same N rollouts. Every menu entry should beat it under *its own* stance, and no menu entry should do markedly worse than it on every group.
- **Naive baseline 2 (proportional-share):** fixed equal shares across groups and sub-programmes. Cheap to compute; helps isolate how much of the improvement comes from optimisation vs simple rebalancing.
- **Expected improvement:** a meaningful optimised menu should show (a) the utilitarian entry (α = 0) beating current practice on total placements by a materially visible amount, and (b) the Rawlsian entry (α = ∞) lifting the worst-off group's outcome substantially above current practice while preserving most of the totals — exactly the trade-off the board wants to see.

### Sensitivity analysis
1. **Slot capacity C_t ±20%** — how much does the menu's composition shift under funding expansion or contraction? Critical for board-level planning.
2. **Caseworker cost h_g ±20%** — does the advantage of the Rawlsian entry disappear if justice-affected placements become cheaper or more expensive per head?
3. **Per-group success rate estimates p_{g,p} ±20%** — tests whether menu rankings are robust to simulator calibration error.
4. **Simulator seed variation** — re-run the full menu generation with different master seeds; stable menus should show near-identical outcome trajectories for each stance.
5. **α-ladder density** — halve and double the ladder density; does the curated menu still cover the spectrum?

### Pilot approach
- **Phase 1 (months 1–3):** build the end-to-end pipeline on a reduced problem (2 groups × 2 sub-programmes × 8 quarters); verify that CMA-ES reliably recovers known-good policies on synthetic ground-truth cases.
- **Phase 2 (months 3–5):** full-scale menu generation on the real 4-group × 4-sub-programme × 20-quarter problem with the commissioned simulator; back-test the α = 0 menu entry against the last 2 years of operational data.
- **Phase 3 (months 5–8):** board-facing presentation with the curated menu, outcome charts per group, and a short methodology note. If the board adopts one entry, implement for the next strategy cycle and plan a mid-cycle re-run with updated intake data.
- **Deployment safeguard:** for the first cycle after board adoption, run the chosen menu entry alongside the agency's existing practice for one quarter (A/B at the sub-programme level where feasible) before full roll-out.

---

## Key References

- Mo, J. & Walrand, J. (2000). *Fair End-to-End Window-Based Congestion Control.* IEEE/ACM Transactions on Networking 8(5): 556–567.
- Atkinson, A.B. (1970). *On the Measurement of Inequality.* Journal of Economic Theory 2(3): 244–263.
- Hansen, N. (2016). *The CMA Evolution Strategy: A Tutorial.* arXiv:1604.00772.
- Mavrotas, G. & Florios, K. (2013). *An improved version of the augmented ε-constraint method (AUGMECON2) for finding the exact Pareto set in multi-objective integer programming problems.* Applied Mathematics and Computation 219(18): 9652–9669.
- Hooker, J.N. (2021). *Fairness through Social Welfare Optimization.* arXiv:2102.00311.
- Roijers, D.M., Vamplew, P., Whiteson, S. & Dazeley, R. (2014). *A Survey of Multi-Objective Sequential Decision-Making.* Journal of Artificial Intelligence Research 48: 67–113.
- Hayes, C.F. et al. (2022). *A practical guide to multi-objective reinforcement learning and planning.* Autonomous Agents and Multi-Agent Systems 36(26).
- Fan, Z., Peng, N., Tian, M. & Fain, B. (2023). *Welfare and Fairness in Multi-objective Reinforcement Learning.* AAMAS 2023. arXiv:2212.01382.
- Deb, K. & Jain, H. (2014). *An Evolutionary Many-Objective Optimization Algorithm Using Reference-point Based Non-dominated Sorting Approach, Part I.* IEEE Transactions on Evolutionary Computation 18(4): 577–601.
- Frazier, P.I. (2018). *A Tutorial on Bayesian Optimization.* arXiv:1807.02811.
