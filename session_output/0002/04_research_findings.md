# Method Research Findings

**Session:** 0002
**Technique category:** Restless Multi-Armed Bandits (RMAB) with feature-driven transition learning + decision-focused learning (outside the social_optimiser catalog, invoked per the structural-gap note in `03_classification.md`)

## State-of-the-Art Algorithms

### 1. Decision-Focused Learning for RMAB (DF-Whittle) ⭐ Recommended starting point

**How it works.** Learns a neural mapping from per-arm features to per-arm Markov transition matrices, then plugs the learned transitions into a Whittle-index policy for arm-pulling. The model is trained **end-to-end against downstream policy reward** rather than against transition log-likelihood. Achieved by deriving a **differentiable Whittle index** via implicit differentiation through the indexability fixed point — gradients flow from expected cumulative welfare back to the feature network's weights.

**Key reference.** Wang, K., Verma, S., Mate, A., Shah, S., Taneja, A., Madhiwalla, N., Hegde, A., & Tambe, M. (2023). *Scalable Decision-Focused Learning in Restless Multi-Armed Bandits with Application to Maternal and Child Health.* AAAI 2023. [arXiv:2202.00916](https://arxiv.org/abs/2202.00916)

**Theoretical properties.** Whittle-index policies are **asymptotically optimal as N → ∞** under the Weber-Weiss indexability condition. DFL does not improve this worst-case bound but **matches predict-then-optimise in predictive accuracy while dominating it on decision regret** in the application regime — the empirical difference that matters.

**Social-sector use.** Maternal-and-child-health call scheduling in the ARMMAN programme (India). Downstream SAHELI deployment reached ~250,000 beneficiaries; an RCT reported +61% engagement in the treated cohort and ~30% reduction in drop-off.

**Fit to the Riverbank problem:** direct. Binary action, per-arm features, moderate N (800 well below the paper's thousands), unknown transitions, historical trajectory data — every structural requirement is met.

---

### 2. Optimistic Whittle Index / UCWhittle

**How it works.** Online variant of Whittle that maintains UCB-style confidence bounds on per-arm transition probabilities and plans each round using the **most-optimistic plausible transition kernel**. Balances exploration (probe uncertain arms) and exploitation (pull the arms the current model thinks are valuable).

**Key reference.** Xu, L., Biswas, A., Fang, F., & Tambe, M. (2023). *Optimistic Whittle Index Policy: Online Learning for Restless Bandits.* AAAI 2023. [arXiv:2205.15372](https://arxiv.org/abs/2205.15372). Code: [lily-x/online-rmab](https://github.com/lily-x/online-rmab).

**Theoretical properties.** First provable **sublinear regret bound** for online RMAB learning against a Whittle-optimal oracle.

**Social-sector use.** Evaluated on ARMMAN-scale cohorts. Intended as an *online adaptive layer* running after an offline warm-start.

**Fit to the Riverbank problem:** high as a **year-two adaptive layer**. Not the primary method at deployment (because Riverbank has historical data enabling offline learning), but worth running alongside to adapt to distribution shift across cohorts.

---

### 3. Gaussian Approximation / Fluid-LP Index Policies

**How it works.** Replaces the stochastic N-arm RMAB with a fluid (large-N) or Gaussian approximation, yielding a linear (or stochastic) program whose dual solution produces a per-arm index. Particularly valuable when the classical indexability condition is degenerate or fails.

**Key reference.** Hong, Y., Xu, C., Wang, W., & Xie, J. (2024). *Achieving Õ(1/N) Optimality Gap in Restless Bandits through Gaussian Approximation.* NeurIPS 2024. [arXiv:2410.15003](https://arxiv.org/abs/2410.15003).

**Theoretical properties.** **Õ(1/N) optimality gap per arm** — asymptotically tighter than the Θ(1/√N) gap of classical fluid-LP policies.

**Social-sector use.** Benchmark literature rather than deployed.

**Fit to the Riverbank problem:** secondary — **useful as a benchmark / sanity oracle** against the DFL-Whittle primary. If the two methods agree on the weekly visit set most weeks, confidence in the recommended policy is high.

---

## Recent Developments (2022–2025)

- **Decomposition-based DFL for RMAB** — Verma et al. (2024). Reduces DFL training cost by per-arm decomposition of the Whittle gradient; relevant if the feature network is large. [arXiv:2403.05683](https://arxiv.org/abs/2403.05683)
- **Bayesian contextual RMAB** — Biswas et al. (2024). Shares statistical strength across arms with similar feature vectors; useful given Riverbank's rich intake features. [arXiv:2402.04933](https://arxiv.org/abs/2402.04933)
- **Inverse Reinforcement Learning for RMAB** (2024). Recovers the latent behavioural policy from logged trajectories — directly addresses the caseworker-judgement selection-bias concern raised by the director. [Springer 978-981-96-0128-8_15](https://link.springer.com/chapter/10.1007/978-981-96-0128-8_15)
- **GINO-Q** — near-optimal alternative when indexability fails under learned transitions. [arXiv:2408.09882](https://arxiv.org/abs/2408.09882)
- **Neural index policies for heterogeneous / non-binary budgets** (2025). Generalises Whittle-style decomposition when the action space is richer than {0,1}. [arXiv:2510.22069](https://arxiv.org/abs/2510.22069)

## Research gaps and caveats for this specific deployment

1. **Selection-bias in the historical data is the central deployment risk.** Vanilla DFL assumes the observational transitions are recoverable from logged trajectories, but when the logging policy (here, caseworker judgement) depends on unobserved confounders correlated with family fragility, DFL will systematically under-estimate visit effects on already-stable families and over-estimate them on already-crisis families. Mitigations:
   - Fit a *behavioural propensity model* `P(visit | features, state)` and reweight the DFL loss (IPW-DFL).
   - Use doubly-robust off-policy evaluation (Dudík, Langford, Li) for any candidate policy before trusting it.
   - Use the IRL-RMAB approach above to infer the past policy before fitting counterfactual dynamics.

2. **No published RMAB work targets refugee resettlement specifically.** Existing benchmarks are ARMMAN (maternal health) and TB adherence. Transfer is reasonable — the structural fit is exact — but the three-state *stable / at-risk / crisis* space is richer than ARMMAN's binary engagement state. **Numerical verification of indexability** is advised before trusting Whittle (the literature has tools for this; if indexability fails, fall back to GINO-Q).

3. **Horizon T = 52 is short** relative to the N → ∞, T → ∞ regime where Whittle's optimality theorems apply. Finite-horizon RMAB corrections (e.g., risk-aware variants) are worth checking if the year-end evaluation is sensitive to early-vs-late-cohort differences.

4. **Off-policy evaluation for restless bandits is thin.** Most OPE literature is contextual-bandit, not restless. Expect to hand-roll a per-arm doubly-robust estimator plus a simulator built from DFL-fit dynamics to validate any candidate policy before deployment.
