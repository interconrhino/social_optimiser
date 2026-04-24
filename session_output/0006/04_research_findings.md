# Method Research Findings

**Session:** 0006
**Technique category:** Multi-objective Optimisation (with simulator-in-the-loop / sequential-policy-search inner problem)

## Summary of the research picture

The user's problem is a multi-objective sequential decision problem evaluated against a trusted simulator. The outputs they want are (i) a small curated menu of policies, each near-optimal under a specified stance on balancing four group-level outcomes, and (ii) interpretable group-level outcome trajectories for each menu entry. Three algorithmic families from the current literature combine to give a principled approach:

1. An **outer scalarisation / preference-articulation method** to turn the vector-valued objective into a sequence of scalar problems — one per menu entry. The ε-constraint family (AUGMECON2) and α-fair / p-mean social welfare scalarisation are the established, interpretable choices here. These directly produce a small curated, representative set rather than a dense Pareto frontier.
2. An **inner simulation-based policy search** that, given a scalarised objective, searches for a near-optimal state-dependent policy by running the simulator as a black box. CMA-ES and Bayesian Optimisation are the workhorses for this; Multi-Objective Reinforcement Learning (MORL) is the natural generalisation if the policy class is rich.
3. **Welfare-aware MORL** as a single-pass alternative that learns a Pareto-set / preference-conditioned policy directly, rather than solving many independent scalarised problems.

Because the user has a modest team (3 data staff, Python, some simulation experience), an 8-month engagement, and explicitly prefers a small curated menu (not a dense frontier), the **scalarisation + inner simulation-based policy search** route is the strongest starting point, with MORL available as a later upgrade if the policy class needs to be enriched.

## State-of-the-Art Algorithms

### 1. α-fair / p-mean scalarisation + AUGMECON2-style curated menu, with CMA-ES (or Bayesian Optimisation) as the inner simulation-based policy-search solver  ⭐ Recommended starting point

**How it works:**
The four group-level outcomes y_g(π) form a 4-vector. An α-fair (equivalently, p-mean / CES) social welfare function `W_α(y) = (Σ_g y_g^{1-α})^{1/(1-α)}` collapses them into a single stance-indexed scalar, where α = 0 gives pure totals (utilitarian), α = 1 gives proportional fairness (Nash-product-like), and α → ∞ gives max-min (Rawlsian). Sweeping α across a small ladder of values (e.g. α ∈ {0, 0.5, 1, 2, 5, ∞}) yields a curated menu of 3–10 stance points that each map to a named ethical position. For each stance, run an inner optimiser that (a) proposes a parameterised policy π_θ, (b) evaluates it by averaging simulator rollouts, and (c) updates θ. CMA-ES is the dominant derivative-free black-box optimiser for this kind of noisy-evaluation setting; Bayesian Optimisation is preferable when each simulator run is particularly expensive because it builds a surrogate and is more sample-efficient. AUGMECON2 is the reference algorithm for the ε-constraint alternative: if the user would rather constrain minima (e.g. "maximise totals subject to justice-affected-group outcome ≥ ε"), AUGMECON2 provides a principled and well-studied way to generate an exact non-dominated representative set for multi-objective integer programs. Either framing — α-fair scalarisation or ε-constraint — yields the same structural pipeline: one scalar optimisation per menu entry, executed against the simulator.

**Key references:**
- Mavrotas, G. & Florios, K. (2013). *An improved version of the augmented ε-constraint method (AUGMECON2) for finding the exact Pareto set in multi-objective integer programming problems.* Applied Mathematics and Computation. https://www.sciencedirect.com/science/article/abs/pii/S0096300313002166
- Mo, J. & Walrand, J. (2000). *Fair End-to-End Window-Based Congestion Control.* IEEE/ACM ToN. (Canonical α-fair reference.)
- Hooker, J. (2021). *Fairness through Social Welfare Optimization.* arXiv:2102.00311. https://arxiv.org/pdf/2102.00311
- Hansen, N. (2016). *The CMA Evolution Strategy: A Tutorial.* arXiv:1604.00772. (CMA-ES reference.)
- Frazier, P. (2018). *A Tutorial on Bayesian Optimization.* arXiv:1807.02811. (BO reference.)

**Theoretical properties:**
- α-fair / p-mean scalarisation preserves Pareto efficiency: for any α ≥ 0, argmax of W_α lies on the Pareto front. The family is *axiomatically characterised* (Atkinson; Mo & Walrand) — it is the unique family that is monotonic, symmetric, scale-invariant, and satisfies a principle of transfers.
- AUGMECON2 guarantees it finds the *exact* Pareto set for multi-objective integer programs (when the inner problem is a solvable IP).
- CMA-ES has strong empirical properties on non-convex, noisy, black-box objectives; no global guarantees, but asymptotic local convergence under mild conditions.
- Bayesian Optimisation has regret bounds under GP-surrogate assumptions; practically strong sample efficiency (useful when each simulator rollout costs meaningful compute).

**Social sector use:**
ε-constraint and α-fair scalarisation are routinely used in humanitarian resource allocation, health-programme portfolio design, and fair-allocation problems (see Hooker 2021 survey on social-welfare optimisation for fairness in algorithmic decision-making). Simulation-based policy search with CMA-ES and BO is widely used in operations research for workforce and capacity planning where a trusted simulator is the evaluator.

### 2. Welfare-aware Multi-Objective Reinforcement Learning (MORL) with a nonlinear welfare objective

**How it works:**
Rather than solving M independent scalarised problems, MORL learns a *single* policy (or a *set* of Pareto-dominating policies) that optimises a vector-valued return, using a non-linear welfare scalarisation (Nash social welfare, generalised Gini, p-mean) inside the value-update. Recent work — notably Fan et al. (AAMAS 2023) "Welfare and Fairness in MORL" and Learning-Fair-Pareto-Optimal-Policies (RLJ/RLC 2025) — gives Q-learning-style and actor-critic methods for non-linear welfare functions. Pareto Q-learning (Van Moffaert & Nowé, JMLR 2014) learns a set of Pareto-dominating policies in one run. Preference-conditioned MORL (Pareto Set Learning) trains a network π_θ(s, λ) that, given a stance λ, outputs the corresponding policy — so the board can re-run at any stance without retraining.

**Key references:**
- Fan, Z. et al. (2023). *Welfare and Fairness in Multi-objective Reinforcement Learning.* AAMAS 2023. arXiv:2212.01382. https://arxiv.org/abs/2212.01382
- Van Moffaert, K. & Nowé, A. (2014). *Multi-Objective Reinforcement Learning using Sets of Pareto Dominating Policies.* JMLR. https://jmlr.org/papers/v15/vanmoffaert14a.html
- Roijers, D.M. et al. (2014/2022). *A Survey of Multi-Objective Sequential Decision-Making* and *A practical guide to multi-objective reinforcement learning and planning.* https://arxiv.org/pdf/1402.0590 , https://link.springer.com/article/10.1007/s10458-022-09552-y
- Hayes et al., *Pareto Set Learning for Multi-Objective Reinforcement Learning* (2025). https://arxiv.org/html/2501.06773v1

**Theoretical properties:**
- MORL with non-linear welfare scalarisation (α-fair, Nash, p-mean) can target any point on the Pareto front, including the non-convex portions that linear scalarisation misses.
- Pareto Q-learning returns a set of Pareto-dominating policies with convergence guarantees in tabular settings.
- Sample complexity is higher than for scalarisation + CMA-ES because the policy class is richer and training is end-to-end.

**Social sector use:**
Emerging. Welfare-aware MORL is a young area but is being actively developed specifically for fairness-in-allocation problems (FairDICE 2025, and the AAMAS 2023 and RLJ 2025 papers listed above). For a first production deployment with a 3-person Python data team, the scalarisation + CMA-ES approach (Option 1) is lower-risk; MORL is a natural upgrade if and when the policy class is enriched.

### 3. NSGA-III (reference-direction-based evolutionary multi-objective optimisation)

**How it works:**
NSGA-III (Deb & Jain, 2014) is an evolutionary algorithm that explicitly maintains a population of solutions covering a set of pre-specified *reference directions* in objective space. Rather than producing a dense Pareto frontier, it focuses search on well-distributed representative points — matching the user's "small curated menu" requirement. Each individual in the population encodes a policy π_θ; fitness is the 4-vector of simulator-evaluated group outcomes; the reference-direction selection pressure keeps the final population covering the stance spectrum.

**Key references:**
- Deb, K. & Jain, H. (2014). *An Evolutionary Many-Objective Optimization Algorithm Using Reference-point Based Non-dominated Sorting Approach, Part I: Solving Problems with Box Constraints.* IEEE TEVC.
- Deb, K. et al. (2002). *A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II.* IEEE TEVC. (Reference catalog entry.)

**Theoretical properties:**
- No optimality guarantee; heuristic. Empirically strong on many-objective problems (≥ 3 objectives).
- Naturally produces the desired small representative set on the Pareto front.
- Requires many simulator evaluations (population × generations); sample-hungry compared to BO but very parallelisable.

**Social sector use:**
Used in humanitarian logistics, health programme portfolio design, and energy-equity planning. Good fit when the simulator is cheap and parallel compute is available.

## Recent Developments

- **Welfare-aware MORL** (2023–2026) — nonlinear social welfare functions (Nash, p-mean, generalised Gini) are now natively supported in policy-gradient MORL and offline MORL (FairDICE, 2025). This is a meaningful advance over the earlier state where only linear scalarisation was supported.
- **Pareto Set Learning (PSL)** — a single network is trained to output, for any stance λ, the corresponding Pareto-optimal policy. For the Tri-Valley use case (where the board wants to re-run on new stance weightings after a leadership change), PSL is attractive: train once, serve any stance on demand.
- **Representative-subset selection on Pareto fronts** — active research area (ScienceDirect 2022; AUGMECON variants) on *how to choose* M representative points from the Pareto front for stakeholder-facing menus, rather than dumping the full frontier. This is exactly the "we don't want to show them a thousand Pareto-optimal options" problem the user raised.

## Research gaps

- There is limited published literature specifically on **simulator-in-the-loop multi-objective policy design for public-sector workforce placement**. The closest analogues are health-programme portfolio design and social-housing allocation, which share the multi-group fairness structure but not the apprenticeship-pipeline dynamics.
- The three canonical stances the board names (totals, worst-off, balanced) map cleanly to the α-fair family, but formalising the *balanced/proportional* stance requires a per-group normalisation choice (per-capita vs raw) that the literature treats variably. This should be surfaced explicitly in implementation.

## Sources
- [A Survey of Multi-Objective Sequential Decision-Making (Roijers et al.)](https://arxiv.org/pdf/1402.0590)
- [A practical guide to multi-objective reinforcement learning and planning (Roijers et al. 2022)](https://link.springer.com/article/10.1007/s10458-022-09552-y)
- [Welfare and Fairness in Multi-objective Reinforcement Learning (Fan et al. 2023)](https://arxiv.org/abs/2212.01382)
- [Learning Fair Pareto-Optimal Policies in MORL (RLJ/RLC 2025)](https://rlj.cs.umass.edu/2025/papers/RLJ_RLC_2025_350.pdf)
- [Pareto Set Learning for Multi-Objective Reinforcement Learning (2025)](https://arxiv.org/html/2501.06773v1)
- [Multi-Objective Reinforcement Learning using Sets of Pareto Dominating Policies (Van Moffaert & Nowé, JMLR 2014)](https://jmlr.org/papers/v15/vanmoffaert14a.html)
- [Fairness through Social Welfare Optimization (Hooker 2021)](https://arxiv.org/pdf/2102.00311)
- [AUGMECON2 (Mavrotas & Florios, 2013)](https://www.sciencedirect.com/science/article/abs/pii/S0096300313002166)
- [New ε-constraint methods for MOILP (2022)](https://www.sciencedirect.com/science/article/pii/S0377221722006142)
- [Simulation Based Bayesian Optimization (2024)](https://arxiv.org/abs/2401.10811)
