# Method Research Findings

**Session:** 0003
**Technique category:** Sequential K-of-N selection under independent Markov dynamics per item, per-round budget — catalog-mapped to "Influence Maximisation (POMDP)" but the structural literature that matches most precisely is **Restless Multi-Armed Bandits (RMABs) with Whittle index policies**.

## Structural fit in one paragraph

The problem is: each week, from |F| ≈ 800 items ("arms"), each evolving on its own 3-state Markov chain (Stable / At-risk / Crisis) with a transition kernel that depends on whether the arm is "pulled" (visited) this week, select exactly K = 40 arms to pull, so as to maximise expected cumulative reward (Σ stable-weeks − w · crisis-weeks) over a 52-week horizon. The per-item Markov chain has state-dependent transitions under both action and inaction, so *arms keep evolving even when not pulled* — the defining feature of a **restless** bandit. This is a canonical RMAB with an exactly-K-per-round budget.

## State-of-the-Art Algorithms

### 1. Whittle Index Policy for Restless Multi-Armed Bandits ⭐ Recommended starting point

**How it works:**
Whittle (1988) showed that the intractable joint planning problem across N correlated-by-budget Markov arms can be *decoupled* by Lagrangian relaxation of the per-round budget. This yields, for each arm and each state, a scalar **Whittle index** — the "subsidy for passivity" at which the planner would be indifferent between pulling and not pulling that arm. The policy at run time is beautifully simple: each week, **compute each family's Whittle index given its current state, rank all 800 families, and visit the 40 with the highest indices.** The index reduces a C(800, 40)-sized joint optimisation to 800 independent per-arm calculations — a speedup from astronomical to linear in N.

**Key references:**
- Whittle, P. (1988). *Restless bandits: Activity allocation in a changing world.* Journal of Applied Probability 25A: 287-298. (Seminal.)
- Gittins, J., Glazebrook, K., Weber, R. (2011). *Multi-armed Bandit Allocation Indices.* Wiley. (Textbook.)
- Nino-Mora, J. (2023). *Markovian restless bandits and index policies: A review.* arXiv:2601.13045. (Recent review.)

**Theoretical properties:**
- Under a technical **indexability** condition on the per-arm MDP, the Whittle index is well-defined.
- Under indexability plus a "global attractor" condition, the Whittle index policy is **asymptotically optimal** as N, K → ∞ with K/N fixed (Weber & Weiss 1990; Verloop 2016). In words: for large cohorts like Riverbank's 800, the gap-to-optimal shrinks to zero.
- For finite horizon, recent work gives explicit gap-to-optimal bounds (Brown & Smith 2020; Zhang & Frazier 2021) that also vanish with N.
- Runtime: per-week policy evaluation is **O(N · |S|)** = O(800 · 3) = trivial; index computation per arm requires solving a small 2-action MDP on 3 states, also trivial.

**Social sector use:**
This is *the* algorithm family being deployed in social-good ML right now. Notable recent deployments:
- **ARMMAN maternal-and-child-health programme (India):** Whittle-index RMAB used to schedule weekly call interventions to at-risk mothers. Live since ~2022 under the SAHELI system. Field-randomised evaluation with ~9,000 beneficiaries showed statistically significant reduction in engagement drop-off vs. a round-robin baseline (Verma et al., AAMAS 2023; Wang et al., AAAI 2023).
- **Public-health adherence / chronic-disease follow-up** — "Collapsing Bandits" (Mate, Killian, Xu, Perrault, Tambe — NeurIPS 2020, arXiv:2007.04432) models exactly the case where a health worker can only "see" a patient's state when intervening — a partial-observability structural cousin of Riverbank's problem.
- **Community-health-worker scheduling** (Boehmer et al., 2024).

### 2. Decision-Focused Learning (DFL) on top of Whittle Index — recent SOTA upgrade when transition model is learned from data

**How it works:**
A two-stage pipeline ("predict-then-optimise") typically first trains a transition-model (here: how (state, features, visit) → next state) to maximise predictive accuracy, then plugs it into the Whittle index policy. **DFL instead trains the transition model end-to-end to directly maximise the Whittle-index policy's downstream decision quality.** This directly addresses Riverbank's concern that the historical data is observational and confounded: the predictive loss and the operational loss are not the same, and DFL aligns them.

**Key reference:**
Wang, K., Verma, S., Mate, A., Shah, S., Taneja, A., Madhiwalla, N., Hegde, A., Tambe, M. (2023). *Scalable Decision-Focused Learning in Restless Multi-Armed Bandits with Application to Maternal and Child Health.* AAAI 2023 / arXiv:2202.00916.

**Theoretical properties:**
- Uses a *differentiable surrogate* of the Whittle index so that gradients flow through the policy back to the predictive model.
- Scales linearly in the number of arms (prior DFL approaches scaled exponentially).
- No formal approximation ratio — empirically dominates two-stage predict-then-optimise in the ARMMAN deployment.

**Social sector use:**
The ARMMAN field study mentioned above used DFL. Deployed in production at scale.

### 3. Online / Bayesian Whittle Index (when transition probabilities are still being learned from live data) — complementary

**How it works:**
When transition probabilities are uncertain (either because historical data is limited or because caseworker-induced confounding makes point estimates unreliable), **online learning variants** of the Whittle policy (e.g. *Optimistic Whittle Index* — Xiong et al. 2022; *BCoR* — Baek et al. 2024, arXiv:2402.04933) use upper-confidence-bound or Bayesian posterior-sampling machinery to balance exploration (try pulling less-seen arms to learn their dynamics) against exploitation (pull the arms the current model says are highest-priority).

**Key references:**
- Jung, Y., Tewari, A. (2019). *Regret bounds for Thompson sampling in episodic restless bandit problems.* NeurIPS.
- Wang, S. et al. (2023). *Optimistic Whittle Index Policy: Online Learning for Restless Bandits.*
- Baek, J. et al. (2024). *A Bayesian Approach to Online Learning for Contextual Restless Bandits with Applications to Public Health.* arXiv:2402.04933.

**Theoretical properties:**
- Sub-linear regret guarantees, typically O(√(T log T)) against the offline Whittle benchmark.
- Well-suited to a pilot where the programme wants to *learn* the effect of visits, not just deploy a fixed policy.

**Social sector use:**
Proposed as the natural successor to the ARMMAN deployment, currently research-stage (2024).

## Recent Developments (last 3 years, 2023–2026)

- **Contextual / feature-aware RMABs** (Baek, Boehmer, Lozano-Duran, Park, 2024). Transition probabilities are modelled as a function of arm features (here: intake features φ_i), allowing the model to generalise to newly-arriving families with no prior trajectory. Extremely relevant to Riverbank's stated wish to *"flag newly-arriving families for closer early attention."*
- **Decision-Focused Learning for RMAB** (Wang et al. 2023, Verma et al. 2023) — as above; field-validated on ARMMAN.
- **LLM-designed rewards** (Behari et al. 2024) — allows programme staff to specify prioritisation preferences in natural language; operationally interesting for Riverbank's desire for supervisor override.
- **Neural Whittle Index** (Nakhleh et al. NeurIPS 2021) — deep-RL-learned index when indexability is not provable analytically. Useful as a fallback if Riverbank's per-family transition structure turns out not to satisfy clean indexability conditions.

## Research gaps

- **Observational-data confounding for offline transition estimation** in RMAB remains an active research area. The ARMMAN line of work uses historical round-robin baselines; Riverbank's historical data is not round-robin — past caseworker priority decisions confound it. This is the highest-risk element of the project and will need careful upstream causal inference (e.g. doubly-robust estimation or inverse-propensity weighting on the past policy) before feeding the transition model into the Whittle index. Some recent work addresses this (Chen et al. 2023 on off-policy RMAB evaluation) but the area is less mature than the online / bandit learning-to-act half.
- **Fairness / coverage-floor constraints** (e.g. "no family goes more than K weeks without a visit") are not natively respected by the unconstrained Whittle policy. Lagrangian augmentation or a simple post-hoc override rule ("if a family's gap > K, force a visit this week and Whittle-rank the remaining 40 − (forced count) slots") is the standard workaround.

## Sources

- [Restless bandits: Activity allocation in a changing world — Whittle (1988)](https://www.jstor.org/stable/3214163)
- [Scalable Decision-Focused Learning in RMAB, Wang et al. AAAI 2023](https://arxiv.org/abs/2202.00916)
- [Collapsing Bandits, Mate et al. NeurIPS 2020](https://arxiv.org/abs/2007.04432)
- [Bayesian Approach to Online Learning for Contextual Restless Bandits, Baek et al. 2024](https://arxiv.org/html/2402.04933)
- [Markovian restless bandits and index policies: A review](https://arxiv.org/html/2601.13045)
- [Optimistic Whittle Index Policy](https://www.researchgate.net/publication/360993695_Optimistic_Whittle_Index_Policy_Online_Learning_for_Restless_Bandits)
- [NeurWIN: Neural Whittle Index Network](https://proceedings.neurips.cc/paper/2021/file/0768281a05da9f27df178b5c39a51263-Paper.pdf)
- [ARMMAN / SAHELI research group — Harvard Teamcore](https://teamcore.seas.harvard.edu/ai-assisting-ngos-improving-maternal-and-child-health-outcomes/)
