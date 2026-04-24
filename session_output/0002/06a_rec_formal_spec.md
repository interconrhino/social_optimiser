# Recommendation: Formal Specification — Session 0002
## Weekly Caseworker Home-Visit Scheduling for Refugee Resettlement

**Technique:** Restless Multi-Armed Bandit (RMAB) with learned per-arm transitions, solved via Whittle-index policy.
**Algorithm:** **Decision-Focused Learning (DF-Whittle)** with **Inverse-Propensity-Weighted loss correction** for historical selection bias.

---

## 1. Formal problem formulation

### Sets

| Symbol | Meaning |
|---|---|
| `N` | Set of active first-year families, i ∈ N, \|N\| ≈ 800 |
| `T` | Weekly decision epochs, t = 1, …, 52 |
| `S = {stable, at-risk, crisis}` | Per-family discrete status space, \|S\| = 3 |
| `A = {0, 1}` | Per-family action: 0 = no visit, 1 = visit this week |

### Parameters

| Symbol | Type | Definition | Source |
|---|---|---|---|
| `K` | Integer | Weekly caseworker capacity = 40 | Operational |
| `x_i` | ℝ^d feature vector | Per-family intake features (~10–20 dims: country of origin, family composition, language, employment history, trauma score, etc.) | Intake records |
| `c` | Scalar ≥ 1 | Crisis-week penalty weight relative to stable-week reward | To elicit from director |
| `P_i(s'\|s, a)` | 3×2×3 tensor per family | Per-family transition probabilities — unknown a priori, learned from data | Learned via DFL from historical trajectories |
| `π_beh(a\|s, x)` | Scalar in [0,1] | Historical caseworker behavioural policy | Estimated from logged data |

### Decision variables

| Symbol | Type | Bounds | Meaning |
|---|---|---|---|
| `a_{i,t}` | Binary | {0, 1} | 1 if family i is visited in week t |
| `w ∈ W` | Neural weights | ℝ^p | Parameters of the feature-to-transition network `f_w : x_i ↦ P̂_i` |

The learned `P̂_i = f_w(x_i)` induces, via Whittle-index decomposition, the visit decisions `a_{i,t}` at each week.

### Observed but not chosen

- `s_{i,t}` — observed status of family i at week t (from caseworker notes / quarterly review).

### Objective

**Maximise** expected cumulative discounted welfare across all families over the horizon:

```
maximise_w  E_{π_w}  [ Σ_{t=1..T}  γ^(t-1)  Σ_{i=1..N}  r(s_{i,t}) ]

where r(stable) = +1,  r(at-risk) = 0,  r(crisis) = −c,  and γ ∈ (0, 1].
```

The expectation is taken over family status trajectories under the Whittle policy `π_w` induced by the learned transitions `f_w(x_i)`.

### Constraints

```
(1)  Σ_{i=1..N}  a_{i,t}  ≤  K = 40        ∀ t ∈ T    [weekly capacity]
(2)  a_{i,t}  ∈  {0, 1}                     ∀ i, t     [binary action]
(3)  s_{i,t+1} ~ P_i(·\|s_{i,t}, a_{i,t})   ∀ i, t     [Markovian transitions]
(4)  Indexability of learned P̂_i           ∀ i        [required for Whittle; verify numerically]
```

**Soft constraints** (handled in a second-stage assignment, not in the RMAB):
- Caseworker-to-family sub-region feasibility.
- Language matching where required.
- Relationship continuity for trauma-sensitive families.

### Uncertainty structure

- **Dynamics:** per-family transition matrices `P_i` are unknown a priori; learned from logged trajectories through the feature mapping `f_w`.
- **Information structure at decision time:** current status `s_{i,t}` and features `x_i` are observable; the true transition kernel is not.
- **Selection bias:** logged trajectories are generated under a non-random behavioural policy `π_beh`; standard MLE of transitions is biased. Addressed by the IPW loss correction below.

---

## 2. Algorithm specification

### Primary: DF-Whittle with IPW correction

**Class:** End-to-end learning + sequential decision policy (RMAB + deep learning).

**Primary reference:** Wang, K., Verma, S., Mate, A., et al. (2023). *Scalable Decision-Focused Learning in Restless Multi-Armed Bandits with Application to Maternal and Child Health.* AAAI 2023. [arXiv:2202.00916](https://arxiv.org/abs/2202.00916).

**IPW correction reference:** Dudík, M., Langford, J., & Li, L. (2011). *Doubly Robust Policy Evaluation and Learning.* ICML 2011.

### Algorithm

1. **Estimate behavioural propensity.** Train `π_beh(a = 1 | s, x)` on the logged (state, feature, action) triples using any binary classifier (logistic regression or gradient-boosted trees; logged data ≈ 125,000 records is ample). Clip propensities to [ε, 1−ε] with ε ≈ 0.05 to prevent extreme weights.
2. **Fit the DFL-Whittle model.** Parameterise `f_w : x ↦ P̂` as a small MLP. For each mini-batch of logged family trajectories, compute the IPW-weighted downstream expected reward under the Whittle policy induced by `f_w`:
   - Compute each family's Whittle index from `P̂_i` via the differentiable-index module (solves the Bellman system at |S| = 3, which admits closed-form differentiation through the indexability fixed point).
   - Simulate the Whittle policy's weekly visit set on the logged cohort, reweighting each observed transition by `1 / π_beh(a_observed | s, x)` so the gradient is unbiased under observational data.
   - Backpropagate from cumulative reward to `w`. Standard Adam optimiser.
3. **Verify indexability.** For each family's learned transition matrix, numerically check that the optimal action in state `s` as a function of subsidy `m` is monotone in `m`. Papers provide the check — runtime negligible at |S| = 3.
4. **Deploy.** At each week t:
   - Observe current state `s_{i,t}` for every active family.
   - Compute the Whittle index `W_i(s_{i,t})` using `f_w(x_i)`.
   - Visit the K = 40 families with highest Whittle index, subject to the soft-constraint assignment layer.

### Theoretical properties

- **Asymptotic optimality.** Whittle policies are asymptotically optimal as N → ∞ under indexability (Weber & Weiss, 1990, *J. Appl. Prob.*).
- **DFL's empirical edge.** In Wang et al. 2023, DF-Whittle produces policies with equal or better expected cumulative reward than two-stage predict-then-optimise baselines, while allowing slightly worse predictive likelihood (because DFL trades predictive loss for decision fit).
- **IPW unbiasedness.** The IPW-weighted DFL gradient is an unbiased estimate of the on-policy gradient under the standard overlap assumption (every action has positive probability under `π_beh` given (s, x)). Variance can be controlled by clipping and by the doubly-robust extension (recommended in production).

### Computational complexity

- **Training:** O(N × |S|² × epochs) for the forward pass per training batch, plus O(|S|³) per arm for the differentiable index solve. At N = 800, |S| = 3, and a reasonable 100 epochs, training completes on a single GPU in hours.
- **Inference:** O(N × |S|³) per week for the index computation, then O(N log N) for the top-K selection. Well under a minute per week on a laptop.

### Known limitations

- **Indexability not guaranteed** under arbitrary learned `P̂`. If indexability fails for a meaningful fraction of families, fall back to **GINO-Q** (Biswas, Verma & Tambe, 2024, [arXiv:2408.09882](https://arxiv.org/abs/2408.09882)).
- **Finite-horizon correction.** T = 52 is not asymptotic; late-horizon effects may slightly bias the decision. Verify empirically via simulator evaluation (below).
- **Soft constraints.** Geography / language / continuity are handled in a second-stage assignment, not in the RMAB — if they bind frequently enough to make most top-index families infeasible in their region, the RMAB's welfare claim overstates achievable welfare. Verify by simulation.

---

## 3. Implementation guidance

### Data requirements

| Data item | Format | Source | Status |
|---|---|---|---|
| Per-family weekly state trajectory (s_t for t = 1..52) | 800 × 52 categorical matrix | Reconstructed from caseworker notes / quarterly reviews | Likely already structured; verify |
| Per-family weekly visit log (a_t for t = 1..52) | 800 × 52 binary matrix | Scheduling records | Should exist |
| Per-family intake features x_i | 800 × d real/categorical matrix, d ≈ 10–20 | Intake assessments | Exists; confirm ML-readable format |
| Historical cohort (same structure, ~2,400 completed families) | For training | Programme archive | Per director; needs reconstruction from notes |
| Crisis-week penalty weight c | Scalar | Director elicitation | To collect |

### Key parameters to calibrate

| Parameter | Suggested start | Sensitivity |
|---|---|---|
| `c` (crisis weight) | 3× at first cut; re-elicit after first quarter-end review | **High** — directly determines how aggressively the policy prioritises near-crisis families |
| Discount γ | 1.0 (total reward) or 0.99 (mild discounting) | Low |
| Feature-network size | Single hidden layer, 64 units | Low at this N |
| Propensity clipping ε | 0.05 | Medium — too aggressive clipping bias; too loose inflates variance |
| Training epochs | Early-stop on simulator-estimated reward on a held-out cohort | Medium |

### Recommended software

Wang et al. 2023 released implementation code; start from there and extend with the IPW loss term. Core stack:

- **Python 3.10+**, **PyTorch** (for the differentiable index module).
- Propensity model: **scikit-learn** (`LogisticRegression` or `GradientBoostingClassifier`).
- ETL from caseworker notes to trajectory matrices: plain Python + pandas.

All dependencies are open source. No commercial solver required.

### Algorithmic steps (concrete)

1. Build the (s, a, s', x) training tuple dataset from 3 years of history.
2. Fit `π_beh(a | s, x)` on this dataset; report calibration metrics and propensity distribution.
3. Initialise `f_w` (MLP) with random weights.
4. For each training epoch:
   - Sample a batch of arm-episodes from the historical dataset.
   - Compute `P̂_i = f_w(x_i)` for each arm in the batch.
   - Run the differentiable Whittle-index computation on each `P̂_i`.
   - Simulate the Whittle policy's action sequence on the batch, weight each observed transition by `1 / π_beh(a_observed | s, x)`, and compute the IPW-weighted cumulative reward.
   - Backpropagate and update `w`.
5. After training, verify indexability numerically on all learned `P̂_i`.
6. For deployment: at each week, read current states, compute Whittle indices, rank families, pass the top K = 40 to the second-stage assignment step (feasibility against geography / language / continuity).

### Computational considerations

Tractable on a single modest GPU (e.g., a laptop-class RTX card) or CPU at this scale. No special infrastructure needed.

---

## 4. Validation

### Evaluation metric

**Expected cumulative welfare per cohort-year** on a held-out validation cohort:
```
Ŵ(π) = Σ_{t=1..52} Σ_{i=1..800} r(s_{i,t}^{π})
```
computed via simulator evaluation (using a DFL-fit simulator as the stand-in for the real environment) AND via doubly-robust off-policy evaluation on the logged data.

### Baseline to beat

**Current practice:** a mix of fixed rotation plus squeaky-wheel triage. Estimate this baseline's expected cumulative welfare on the logged historical cohort directly from observed status trajectories. This is the naive benchmark the new policy must beat.

**Secondary baseline:** a predict-then-optimise pipeline (MLE-fit transitions, same Whittle policy). Report the DFL vs. predict-then-optimise gap — if it is small, the extra DFL complexity may not be justified on this dataset.

### Sensitivity analysis

Test the following (each is a small additional training / evaluation run, not a full redesign):
1. **Crisis weight `c`** — re-run with c ∈ {2, 3, 5, 10}; report how the selected visit set shifts toward at-risk vs. stable-leaning families.
2. **Propensity-model choice** — swap logistic regression for gradient-boosted trees; check whether the policy moves materially (if yes, there is an unobserved-confounder problem worth investigating).
3. **IPW vs. uncorrected DFL** — ablation: compare the policy trained with and without the IPW reweighting. If the gap is large, the selection-bias concern is real; if small, you have quantified that it wasn't binding.

### Pilot approach

Shadow-mode deployment for **one cohort-quarter** (13 weeks) before any change to caseworker workflow:
- Compute the algorithm's recommended weekly top-40 each week.
- Compare against caseworkers' own weekly pick.
- Record agreement rate, and for disagreed families, record outcome at 4-week follow-up.
- After 13 weeks, review with the director. Proceed to A/B or phased-deployment only if the shadow comparison shows material disagreement and outcome evidence in favour of the algorithm.

---

## 5. Key references

- Wang, K., Verma, S., Mate, A., Shah, S., Taneja, A., Madhiwalla, N., Hegde, A., & Tambe, M. (2023). *Scalable Decision-Focused Learning in Restless Multi-Armed Bandits with Application to Maternal and Child Health.* AAAI 2023. [arXiv:2202.00916](https://arxiv.org/abs/2202.00916)
- Weber, R. R. & Weiss, G. (1990). *On an Index Policy for Restless Bandits.* Journal of Applied Probability, 27(3).
- Dudík, M., Langford, J., & Li, L. (2011). *Doubly Robust Policy Evaluation and Learning.* ICML 2011.
- Xu, L., Biswas, A., Fang, F., & Tambe, M. (2023). *Optimistic Whittle Index Policy: Online Learning for Restless Bandits.* AAAI 2023. [arXiv:2205.15372](https://arxiv.org/abs/2205.15372)
- Biswas, A., Verma, S. & Tambe, M. (2024). *GINO-Q: A Near-Optimal Policy for Restless Bandits without Indexability.* [arXiv:2408.09882](https://arxiv.org/abs/2408.09882)
- Hong, Y., Xu, C., Wang, W., & Xie, J. (2024). *Achieving Õ(1/N) Optimality Gap in Restless Bandits through Gaussian Approximation.* NeurIPS 2024. [arXiv:2410.15003](https://arxiv.org/abs/2410.15003)
