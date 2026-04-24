# Method Selection

**Session:** 0003

## Selected Algorithm

**Name:** Whittle Index Policy for Restless Multi-Armed Bandits (RMAB), with a learned per-family transition model — and, if in-house ML capacity allows in a second phase, Decision-Focused Learning (DFL) to train that transition model end-to-end for Whittle-index decision quality.
**Category:** Sequential stochastic decision-making under a per-round budget constraint with independent Markov-evolving items ("restless bandits").
**Type:** Approximate (asymptotically optimal as N → ∞ with K/N fixed; trivially fast to execute).

**Why this algorithm:**
The problem has four structural features that together single out the Whittle index: (i) a per-round cardinality budget (exactly 40 of 800 each week), (ii) items that evolve on their own 3-state Markov chain both when acted on and when not — the "restless" property, (iii) a long multi-period horizon (52 weeks) where decisions today affect future state distributions, and (iv) a linearly-separable reward (stable-weeks − w·crisis-weeks) that decomposes across families. This combination is the canonical RMAB setting, and the Whittle index is the canonical algorithm for it: it **Lagrangian-decouples** the cross-family coupling introduced by the budget and reduces the intractable joint planning problem (weekly action space of size C(800, 40), joint state space of size 3^800) to **800 independent 3-state MDP calculations per week** — an astronomical-to-linear speedup. At run time each week, each family gets a scalar priority; visit the top 40. That is exactly the decision rule Riverbank has asked for.

**Approximation guarantees:**
- Under **indexability** of the per-family 3-state MDP (a mild technical condition that can be verified numerically by checking that the set of "passive-optimal" states grows monotonically in the subsidy parameter), the Whittle index is well-defined.
- Under indexability plus a global-attractor condition, the Whittle index policy is **asymptotically optimal** as N → ∞ with K/N fixed (Weber & Weiss 1990; Verloop 2016). For N = 800, K = 40 (K/N = 5%), the sub-optimality gap is empirically small in RMAB studies.
- Finite-horizon gap-to-optimal bounds exist (Brown & Smith 2020; Zhang & Frazier 2021) and also shrink with N.
- If indexability fails for Riverbank's transition kernel, fall back to a **Lagrangian / Fluid-LP priority rule** (Hu & Frazier 2017) with a weaker but non-empty guarantee, or to **NeurWIN** (Nakhleh et al. 2021), which learns an index policy via deep RL without requiring analytic indexability.

**Computational complexity:**
- Per-family Whittle-index computation: solve a small 2-action, 3-state MDP → microseconds.
- Across N = 800 families per week: O(N · |S|) = O(2,400 elementary operations). Weekly scheduling runs in well under a second on a laptop.
- Offline transition-model estimation: standard supervised learning (multinomial regression or gradient-boosted model) on ~2,400 × ~52 ≈ 125,000 family-week transitions — trivial data size for two analysts on SQL/Python.
- DFL training (optional second phase): linear in N, polynomial in |S|; reported training runtimes of hours on ARMMAN-scale problems (Wang et al. AAAI 2023).

**Known limitations for this problem:**
1. **Observational-data confounding.** The transition kernel is estimated from historical data in which visits were *not* randomly assigned — past caseworker priority calls drive both the visit pattern and the family's observed trajectory, so naive supervised learning overstates the "effect of a visit" on already-prioritised families and understates it elsewhere. This must be mitigated *upstream* of the Whittle index (doubly-robust estimation, inverse-propensity weighting on an estimate of the past caseworker policy, or — best — a small prospective pilot with partial randomisation in which some otherwise-borderline families are visited and some aren't). Without this step, the Whittle index is a very sharp knife pointed at a biased target.
2. **Partial observability.** Between visits, a family's state is inferred, not observed. The standard RMAB formulation assumes full observability each decision epoch; Riverbank's setting is closer to a **Collapsing Bandit** (Mate et al. NeurIPS 2020) — we recommend starting with a fully-observed approximation (state = last caseworker assessment, possibly staled by elapsed weeks) and moving to a collapsing-bandit formulation only if validation shows the simpler model leaves significant value on the table.
3. **Fairness / coverage floor.** The vanilla Whittle policy can starve a family that is persistently mid-ranked. A simple, transparent remedy is a hard "max-gap" override: **if any family has not been visited in ≥ K_max weeks, force-visit it and let the Whittle index fill the remaining slots.** This preserves almost all of the optimality while protecting duty of care.
4. **Caseworker-routing not modelled.** The Whittle index says *which* 40, not *which caseworker visits whom*. Downstream assignment (respecting geography, language, continuity of relationship) is a separate small problem — Hungarian / min-cost bipartite matching each week — that can be layered on after the Whittle selection.

## Why not the alternatives

| Alternative | Reason not selected |
|---|---|
| Integer Programming with a static per-week cardinality constraint (rank by current-state risk and pick top 40) | Treats each week as independent; cannot credit the fact that *a visit today reduces the probability of a future-week crisis*. Discards the sequential-planning structure the user explicitly asked for. |
| Exact POMDP / full MDP via value iteration on the joint state | Joint state space of size 3^800 ≈ 10^382 — astronomically beyond any tractable solver. Exact dynamic programming is infeasible. |
| Myopic heuristic (visit the 40 currently-closest-to-crisis) | Equivalent to a one-step-lookahead policy; ignores the long-horizon "pay off across the year" structure and typically under-serves families that are *trending* badly but not yet near crisis. |
| Reinforcement learning on the joint policy (e.g. DQN with a 800-dim action) | Combinatorial action space of size C(800, 40); black-box RL has no structural advantage here and is sample-inefficient compared to Whittle's structural decomposition. |
| Monte-Carlo simulation alone | Excellent *evaluation* tool but does not produce a decision rule; belongs in the validation phase alongside Whittle, not as the primary method. |
| Generic scheduling / constraint satisfaction | Designed for hard-rule timetabling, not for stochastic long-horizon reward maximisation; has no mechanism to reward *expected* future trajectory improvement. |

## What the organisation needs before starting

- **Data to collect / assemble:**
  - A clean **state-trajectory table** for all past families: (family_id, week, state ∈ {Stable, At-risk, Crisis}, visited this week Y/N, features φ). Derivable from existing records but will take careful ETL.
  - An **estimate of the past caseworker policy** (propensity of visiting a family in a given state and week, as a function of features). Needed for confounding correction. Can be fit as a logistic regression on historical data.
  - A **held-out validation cohort** — e.g. last programme year's families — reserved for evaluating candidate policies before live rollout.
  - A **documented value for w**, the crisis-weight, ideally with sensitivity bounds (we recommend evaluating w ∈ {1, 2, 3, 5}).

- **Skills required:**
  - An in-house analyst comfortable with Python, multinomial / ordered logistic regression, and basic matrix operations (Markov-chain arithmetic). Both existing analysts qualify.
  - For the end-to-end DFL upgrade (phase 2, optional): familiarity with PyTorch / JAX — likely via a technical partner.
  - A programme-side stakeholder who can articulate the crisis-weight w and the max-gap K_max, and who can own the "when does the supervisor override" rules.

- **Estimated effort:**
  - **Phase 0 (weeks 1–4):** data pipeline, state reconstruction from notes, feature engineering, historical EDA. 2 analysts × 4 weeks.
  - **Phase 1 (weeks 5–10):** fit transition model (with propensity-adjusted / doubly-robust estimator); verify indexability numerically; implement Whittle index computation; simulate candidate policies on historical data (off-policy evaluation); build a weekly-recommendation report that a supervisor can review and override. 2 analysts × 6 weeks, supported by part-time external optimisation advisor.
  - **Phase 2 (weeks 11–24):** shadow-mode deployment (model recommends; caseworkers continue current process; compare) followed by pilot rollout in a subset of the metro area. Add Decision-Focused Learning on top of the predict-then-optimise baseline if capacity allows.
  - **Total pilot effort:** comfortably within the six-month pilot window the user described. Open-source stack throughout (numpy, scipy, scikit-learn for estimation; a ~200-line Python module for Whittle index computation; PyTorch only if DFL is attempted).
