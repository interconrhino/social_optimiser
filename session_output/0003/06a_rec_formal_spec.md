# Optimisation Recommendation — Formal Specification (for data scientists / analysts)

**Session:** 0003
**Problem domain:** Social welfare / case management — weekly caseworker home-visit prioritisation for newly-arrived refugee families
**Technique:** Restless Multi-Armed Bandits (RMAB) with a per-round budget constraint
**Algorithm:** Whittle Index Policy with a learned per-family transition model (with Decision-Focused Learning as a recommended phase-2 upgrade)

---

## 1. Formal Problem Formulation

### Decision Variables

- **x_{i,t}** ∈ {0, 1}, for every family i ∈ F (|F| ≈ 800) and every week t ∈ {1, …, 52} — equals 1 if family i receives a home visit in week t, else 0.

The object being optimised is not the static matrix (x_{i,t}) but a **policy** π mapping the observed cohort state at the start of each week t to a vector (x_{1,t}, …, x_{|F|,t}) with exactly 40 ones. Per-family decisions at time t may depend only on history observable up to time t (non-anticipativity).

### Latent State

- **s_{i,t}** ∈ S = {Stable, At-risk, Crisis} — family i's situation at the start of week t. Evolves stochastically; not a decision variable. Observed during a visit; inferred otherwise.

### Objective Function

**Maximise** the expected total family-welfare score over the 52-week horizon:

  J(π) = E_π [ Σ_{t=1}^{52} Σ_{i ∈ F} R(s_{i,t}) ]

where R(Stable) = +1, R(At-risk) = 0, R(Crisis) = −w, and w ≥ 1 is the user-set crisis penalty weight (user's wording: "we weight crisis weeks more heavily because the damage lasts"; recommend w ∈ [2, 5] with sensitivity analysis).

### Constraints

| # | Constraint | Form |
|---|---|---|
| 1 | Weekly caseworker capacity | Σ_{i ∈ F} x_{i,t} = 40, ∀ t ∈ {1, …, 52} (hard equality) |
| 2 | Each family visited at most once per week | x_{i,t} ∈ {0, 1} (by construction) |
| 3 | Non-anticipativity | x_{i,t} ∈ σ(H_t), where H_t is history at start of week t |
| 4 | Coverage floor (optional, strongly recommended) | ∀ i, t ≥ K_max: Σ_{τ = t − K_max + 1}^{t} x_{i,τ} ≥ 1, suggested K_max = 8 |

### Parameters

| Symbol | Meaning | Value / Source |
|---|---|---|
| |F| | Active-cohort size | ≈ 800 (Riverbank) |
| K | Weekly visit budget | 40 |
| T | Horizon (weeks) | 52 |
| w | Crisis penalty weight | user-set; default 3, sensitivity over {1, 2, 3, 5} |
| K_max | Max-gap coverage floor | user-set; default 8 weeks |
| φ_i | Family feature vector | intake data (country of origin, family composition, languages, employment / education, trauma-screening score, neighbourhood, co-arrival cohort, medical history) |
| P_{i}^{a}(s' | s) = P(s_{i,t+1} = s' | s_{i,t} = s, x_{i,t} = a, φ_i) | Per-family transition kernel, two actions a ∈ {0, 1} (not visited, visited) | **Estimated** from ~2,400 historical families' weekly trajectories, with causal-inference adjustment for historical confounding |

### Uncertainty Structure

- **What is uncertain:** future state trajectories (s_{i,1}, …, s_{i,52}) for every family.
- **Model:** Each family is a **2-action, 3-state Markov Decision Process** (MDP). Inter-family independence assumed conditional on features. Transitions differ between a = 0 (no visit) and a = 1 (visit). The "restless" property — arms' states evolve under both actions — is essential: even an unvisited family's state drifts.
- **Observation model:** State s_{i,t} is fully observed when a = 1 (the visit reveals the family's current situation). Between visits, state is inferred from last observed state + elapsed time + features + any externally-surfaced crisis signals (eviction notices, school calls, etc.). The phase-1 recommendation assumes quasi-full observability each week via this inference; a phase-2 upgrade to a **collapsing bandit** / partially-observable formulation is possible if validation shows value.
- **Sequential:** yes, 52 weekly decision epochs; closed-loop policy (not a pre-committed schedule).

---

## 2. Recommended Algorithm

**Algorithm:** Whittle Index Policy for Restless Multi-Armed Bandits
**Class:** Lagrangian index policy for a stochastic-control MDP — an asymptotically-optimal heuristic decomposition of a budget-coupled weakly-coupled MDP

### Why this algorithm

The problem has the defining RMAB structure: N independent Markov arms with a per-round cardinality budget. Solving the coupled problem exactly is infeasible — the joint state space is |S|^|F| = 3^800 and the per-round action space is C(800, 40). Whittle (1988) showed that **Lagrangian relaxation of the budget constraint** decouples the N-arm problem into N single-arm subproblems, each of which yields a scalar **Whittle index** λ_i(s) = the subsidy for passivity at which the decision-maker is indifferent between pulling and not pulling arm i in state s. The decision rule is then: **each week, compute λ_i(s_{i,t}) for every family and visit the 40 with the highest index.** This achieves near-optimal performance at trivial computational cost and — critically for Riverbank — produces a scalar priority score per family that supervisors can interpret, debate, and override.

Compared to a myopic "visit the 40 closest to crisis" rule, the Whittle index explicitly credits *expected future* reward improvement, catching "quietly slipping" families before they reach crisis — which is precisely the failure mode Riverbank identified in its current process.

### Theoretical properties

- **Optimality:** Asymptotically optimal as N → ∞ with K/N fixed, under **indexability** (a monotonicity condition on per-arm passive-optimal sets) + a global-attractor condition (Weber & Weiss 1990; Verloop 2016). For N = 800, K / N = 0.05, numerical experiments in adjacent deployed systems report within a few percent of dynamic-programming upper bounds.
- **Finite-horizon gap bounds:** Brown & Smith (2020); Zhang & Frazier (2021).
- **Complexity:** Offline — each arm's index is computed by solving a 2-action, 3-state MDP (microseconds). Online — per-week policy evaluation is O(N · |S|) = O(2,400 ops); weekly scheduling in milliseconds on a laptop.
- **Key reference:** Whittle, P. (1988). *Restless bandits: Activity allocation in a changing world.* J. Appl. Probab. 25A: 287–298.

### Known limitations

1. **Indexability** must be verified for the fitted transition kernel; not guaranteed a priori. If it fails, fall back to a **Lagrangian / Fluid-LP priority rule** (Hu & Frazier 2017) or **Neural Whittle Index** (NeurWIN; Nakhleh et al. NeurIPS 2021).
2. **Observational-data confounding** in the offline estimation of P_i^a is the single highest-risk element. Must be addressed upstream via (a) propensity adjustment of the historical caseworker policy, (b) doubly-robust estimation, and ideally (c) a small prospective randomisation in the pilot to obtain unbiased signal.
3. **Partial observability** between visits is smoothed over by the phase-1 assumption. If validation shows large gaps, migrate to a **Collapsing Bandits** (Mate et al., NeurIPS 2020) formulation; same Whittle-index family, richer state.
4. **Equity / coverage floor** is not native. Enforce via the max-gap override (if any family has gone K_max weeks unvisited, force a visit and Whittle-rank the remaining 40 − (forced) slots).
5. **Caseworker routing** (which specific caseworker visits whom) is a separate downstream problem; solve via Hungarian / min-cost bipartite matching after Whittle selection.

---

## 3. Implementation Guidance

### Data Requirements

| Data item | Description | Format | Source |
|---|---|---|---|
| Trajectory table | One row per (family i, week t): state s_{i,t}, visited x_{i,t}, next-state s_{i,t+1} | Pandas DataFrame / Parquet, ~125k rows | Derived from existing weekly visit logs + quarterly status reviews + caseworker notes |
| Feature matrix Φ | One row per family, columns = intake features (country, family composition, languages, employment history, education, trauma score, co-arrival group, neighbourhood, medical conditions) | DataFrame | Existing intake records |
| Historical visit propensities | For each (state, features), probability the past programme visited | Scalar per (s, φ) — estimated | Fit via logistic regression on historical data (the "past policy" model) |
| Current cohort state | Most recent assessment s_{i,t} for each currently-active family | Live feed — DataFrame updated weekly | Caseworker weekly notes + ETL pipeline |
| Validation cohort | Held-out cohort from most recent completed programme year | Same structure as trajectory table | Hold out one year of data from model training |

### Key parameters to calibrate

- **w (crisis penalty weight).** Controls how aggressively the policy diverts visits to families near crisis. Sensitivity **high**: the ordering of priorities changes materially with w. Recommended starting point: w = 3. Evaluate w ∈ {1, 2, 3, 5} on validation cohort.
- **K_max (max-gap coverage floor).** Controls how much equity the programme demands. Sensitivity **medium**: tighter K_max reduces global reward by a few percent but increases worst-case coverage. Recommended starting point: K_max = 8.
- **State-inference staleness threshold.** How many weeks can a family's state estimate be "carried forward" before it must be treated as unknown? Sensitivity **medium**. Recommended: treat as "unknown, assume At-risk" after 6 weeks without direct contact.
- **Propensity-adjustment model features.** Which features enter the historical-policy model? Sensitivity **high** for debiasing quality. Recommended: use the same feature set as the transition model; fit via cross-validated regularised logistic regression.

### Algorithmic steps

**Offline (one-time, then periodic re-fitting):**

1. Reconstruct the **trajectory table** from historical logs.
2. Fit the **past-policy / propensity model** π̂_hist(visit | s, φ) on historical data.
3. Fit the **per-family transition kernel** P̂_i^a(s' | s, φ), using either:
   - Multinomial logistic regression with family features, separately for a = 0 and a = 1, with **inverse-propensity weighting (IPW)** or **doubly-robust** estimation to correct historical-policy confounding; OR
   - Gradient-boosted multinomial classifier with the same weighting.
4. **Verify indexability** numerically per family: for each family, sweep the Lagrange multiplier λ and check that the set {s : passive-optimal} grows monotonically.
5. **Compute the Whittle index** λ_i(s) for every (family, state) pair. For a 3-state per-arm MDP this has closed-form-adjacent solutions (Nino-Mora's adaptive-greedy algorithm is the standard choice; implement in ~100 lines of NumPy).
6. **Store** {λ_i(s_1), λ_i(s_2), λ_i(s_3)} for every family.

**Online (each week):**

7. Read the current state s_{i,t} of every active family (from caseworker weekly notes / inference).
8. Look up λ_i(s_{i,t}) for every i.
9. **Apply max-gap override:** force-visit any family with time-since-last-visit ≥ K_max.
10. **Whittle-rank the remainder:** select the families with the largest λ_i until the total visit count reaches 40.
11. Output the selection with per-family priority scores to supervisors for review / override.
12. Log the realised visits and caseworker-assessed state transitions.

**Periodic (monthly or quarterly):**

13. Append the last period's data to the trajectory table; re-fit transition and propensity models; recompute Whittle indices.

**Optional phase 2 (months 4–6 of the pilot, if in-house capacity allows):**

14. Replace the two-stage (fit transitions, then compute Whittle index) with **Decision-Focused Learning** (Wang et al., AAAI 2023, arXiv:2202.00916): train the transition model with a differentiable Whittle-index surrogate as the loss, so the model is optimised for decision quality, not prediction accuracy. Reported to produce large real-world gains in ARMMAN's maternal-health deployment.

### Computational considerations

- Expected complexity at Riverbank scale: weekly scheduling in **<1 second** on a laptop. Offline fitting and indexability verification in **< 1 hour** on a laptop.
- Scaling: linear in N; scales easily to tens of thousands of families.
- Software (all open-source):
  - numpy, pandas, scikit-learn for data handling and model fitting.
  - scipy.optimize for the per-arm MDP solves (or a 50-line value-iteration in numpy).
  - A ~200-line Python module implementing the Whittle-index computation and the weekly selection rule.
  - Optional phase 2: PyTorch for Decision-Focused Learning.
  - Gurobi / HiGHS / CBC only if the user later wants an exact LP-relaxation upper bound for validation.

---

## 4. Validation

### Evaluation metric

Primary: the user's own objective, J(π) = Σ (stable-weeks) − w · Σ (crisis-weeks), evaluated on the held-out validation cohort via **off-policy evaluation** (importance-weighted estimator using the fitted past-policy propensities, or doubly-robust estimator).

Secondary:
- Coverage distribution: median / 5th / 95th percentile of visits-per-family-per-year. Flags starvation.
- Crisis-rate reduction: fraction of family-weeks spent in Crisis under the candidate policy vs. historical baseline.
- Max-gap violations: % of families with >K_max weeks between visits.
- Robustness: stability of the selected policy under ±20% perturbations of transition probabilities.

### Baseline to beat

1. **Current Riverbank practice:** mix of fixed rotation + caseworker triage. Reconstruct on the validation cohort and evaluate J.
2. **Myopic rule:** visit the 40 currently-closest-to-crisis each week. A non-trivial lower bound that the Whittle policy should beat by catching trending-but-not-yet-crisis families.
3. **Uniform random rotation:** pure round-robin, as in the ARMMAN comparator.

Expected improvement: based on deployed RMAB systems in adjacent domains (ARMMAN maternal health, collapsing-bandit chronic care), relative reduction in crisis-weeks of ~15–40% over current practice is a plausible target. Do not promise this figure to stakeholders — validate it first.

### Sensitivity analysis

1. **Crisis weight w.** Vary over {1, 2, 3, 5}. Does the policy's top-40 selection change? By how much does J change?
2. **Transition-kernel perturbations.** Perturb each P̂_i^a by ±20%. Does the weekly selection remain stable?
3. **Max-gap K_max.** Vary over {6, 8, 10, 12}. Does the coverage-vs-reward trade-off move smoothly?
4. **Propensity-model specification.** Refit with alternative feature sets. Does the transition-kernel estimate — and hence the Whittle ranking — change?
5. **Observability assumption.** What happens if we treat state as unknown after 4 weeks vs. 8 weeks?

### Pilot approach

- **Months 1–2: data pipeline and model fitting.**
- **Months 3–4: shadow mode.** System recommends each week; caseworkers continue current process; compare what the model would have prioritised against what actually happened. Build trust and surface edge cases.
- **Month 5: partial rollout.** In a randomly-selected half of the metro, supervisors follow the model's recommendation (with override); in the other half, current practice continues. Approximate A/B evaluation.
- **Month 6: evaluate and iterate.** Compare J, crisis rates, and coverage across the two halves. If Whittle beats baseline, expand; if not, diagnose and refit.

---

## 5. Key References

- **Whittle, P. (1988).** Restless bandits: Activity allocation in a changing world. *Journal of Applied Probability* 25A: 287–298. [Seminal.]
- **Weber, R. & Weiss, G. (1990).** On an index policy for restless bandits. *Journal of Applied Probability* 27: 637–648.
- **Mate, A., Killian, J., Xu, H., Perrault, A., Tambe, M. (2020).** Collapsing Bandits and Their Application to Public Health Interventions. NeurIPS. arXiv:2007.04432.
- **Wang, K., Verma, S., Mate, A., Shah, S., Taneja, A., Madhiwalla, N., Hegde, A., Tambe, M. (2023).** Scalable Decision-Focused Learning in Restless Multi-Armed Bandits with Application to Maternal and Child Health. AAAI. arXiv:2202.00916.
- **Verma, S. et al. (2023).** Restless Multi-Armed Bandits for Maternal and Child Health: Results from Decision-Focused Learning. AAMAS.
- **Baek, J. et al. (2024).** A Bayesian Approach to Online Learning for Contextual Restless Bandits with Applications to Public Health. arXiv:2402.04933.
- **Nino-Mora, J. (2023).** Markovian restless bandits and index policies: A review. arXiv:2601.13045.
- **Nakhleh, K. et al. (2021).** NeurWIN: Neural Whittle Index Network for Restless Bandits via Deep RL. NeurIPS.
- **Gittins, J., Glazebrook, K., Weber, R. (2011).** *Multi-armed Bandit Allocation Indices.* Wiley. [Textbook.]
