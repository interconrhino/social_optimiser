# Method Research Findings

**Session:** 0007
**Technique category:** Sequential, budget-constrained selection under partial observability over independent units — i.e., the **Restless Multi-Armed Bandit (RMAB)** family. (Catalogued under `influence_maximisation (POMDP)`; the catalog entry's sequential/partial-observability structure is the right shape, but the networked-influence part does not apply, so we use the RMAB specialisation instead.)

## Why this framing

Each farmer is an independent "arm" with a latent engagement state that evolves stochastically every month — whether or not a call ("active action") is taken. The planner may pull at most K = 400 arms per month for T = 6–8 months and wants to maximise cumulative engagement across the window. This is a textbook **finite-horizon, budget-constrained, partially observable restless bandit** problem. The closest real-world analogue in the literature is **ARMMAN's maternal mHealth call-scheduling programme** in India — a weekly automated voice-advisory to pregnant beneficiaries with a small human-caller budget used to re-engage drifters. The problem structure is essentially identical to GreenFurrow's (population ~ tens of thousands, budget on order of a few hundred calls per round, multi-round, latent engagement state, observational data gathered under a non-random allocation rule).

## State-of-the-Art Algorithms

### 1. Whittle Index Policy (with Threshold / Partially Observable extensions) — Recommended starting point

**How it works:** Whittle's relaxation decouples the N-arm budget-constrained problem into N independent single-arm problems by introducing a per-arm "subsidy for passivity". For each arm (farmer) in its current state, a scalar **Whittle index** is computed that represents the marginal value of calling that farmer now. Every month the planner simply ranks all farmers by their current Whittle index and calls the top K. The index is computed offline from the estimated per-farmer Markov transition model; it is updated as observations arrive. The policy is *asymptotically optimal* as N → ∞ under an indexability condition, and its computation is pleasantly decomposable — one farmer at a time.

**Key references:**
- Whittle, P. (1988). *Restless bandits: activity allocation in a changing world.* Journal of Applied Probability 25A: 287–298. (Original formulation.)
- Mate, A., Killian, J., Xu, H., Perrault, A., Tambe, M. (2020). *Collapsing Bandits and Their Application to Public Health Interventions.* NeurIPS 2020. (Closest-form extension to monthly public-health engagement calls: partially observable states that "collapse" when acted upon.)
- Mate, A. et al. (2022). *Field Study in Deploying Restless Multi-Armed Bandits: Assisting Non-Profits in Improving Maternal and Child Health.* AAAI / Harvard Teamcore. (ARMMAN deployment — the direct analogue to GreenFurrow's setting.)
- Verma, S. et al. (2023). *Towards Soft Fairness in Restless Multi-Armed Bandits.* AAAI 2023. (arXiv:2207.13343) — fairness-constrained variant.
- Li, D., Varakantham, P. (2022). *Efficient Resource Allocation with Fairness Constraints in Restless Multi-Armed Bandits.* UAI 2022. (arXiv:2206.03883) — the **ProbFair** policy with per-arm lower-bound pull probability, which directly answers the user's equity constraint.
- Liu, K. (2025). *Relaxed Indexability and Index Policy for Partially Observable Restless Bandits.* Management Science 71(12): 10106–10121. (arXiv:2107.11939) — current best theoretical framework for the partially-observable case with tractable index computation.

**Theoretical properties:**
- **Optimality:** Asymptotically optimal as N → ∞ under indexability (Weber & Weiss 1990); empirically near-optimal on public-health RMAB benchmarks; beats myopic/greedy and round-robin baselines consistently.
- **Complexity:** Index computation is O(|S|³) per arm per month for a |S|-state Markov chain, then an O(N log N) sort per month to pick the top-K. At N ≈ 28,000 with small state spaces (say |S| ≤ 10), this runs in seconds on a laptop.
- **PSPACE-hard in general** (Papadimitriou & Tsitsiklis 1999), which is *why* an index policy is attractive — it is a principled tractable approximation rather than exact solve.

**Social sector use:** Core algorithm used by **ARMMAN** to allocate human service-calls to pregnant women whose engagement with a weekly automated voice advisory is dropping. ARMMAN + Google Research reported RCT evidence that the Whittle-index allocation materially increases engagement vs. the prior round-robin + triage rule (Mate et al. 2022; Harvard Teamcore research page). Also applied to tuberculosis adherence, food-rescue volunteer engagement (Contextual Budget Bandit, arXiv:2509.10777, 2025), and anti-poaching patrol.

### 2. Decision-Focused Learning (DFL) for RMABs

**How it works:** Instead of (a) estimating the per-arm Markov model from data and (b) plugging those estimates into a Whittle-index computation, DFL trains the transition-model estimator end-to-end to minimise *policy regret* — i.e., the upstream model parameters are learned to make the *downstream Whittle-index decisions* as good as possible. This matters here because GreenFurrow's historical data is *confounded* (non-random allocation); naive MLE of transition probabilities can optimise the wrong thing, while DFL directly optimises expected engagement under the policy produced.

**Key reference:** Wang, K., Verma, S., Mate, A., Shah, S., Taneja, A., Madhiwalla, N., Hegde, A., Tambe, M. (2023). *Scalable Decision-Focused Learning in Restless Multi-Armed Bandits with Application to Maternal and Child Health.* AAAI 2023 (arXiv:2202.00916).

**Theoretical properties:** No closed-form optimality bound — this is an empirical learning approach — but it consistently outperforms two-stage (MLE-then-plan) Whittle on ARMMAN data when the data-generating policy differs from the target policy, which is GreenFurrow's exact situation.

**Social sector use:** Deployed at scale on ARMMAN maternal-health programme; reported ~30% improvement over standard two-stage Whittle on the same dataset in the referenced paper.

### 3. Bayesian Contextual / Online RMAB (BCoR) and Language-Model-Shaped RMAB (DLM)

**How it works:** A Bayesian approach that maintains posteriors over each farmer's transition model and updates monthly as new listen observations arrive; explicitly handles **underserved subgroups** and **contextual covariates** (district, language group, phone type — all of which GreenFurrow has). A more recent variant (Decision-Language Model, DLM, arXiv:2402.14807, 2024) uses an LLM to propose reward shapings that reflect programme-specific priorities expressed in plain language (e.g. "don't let any language group go under X% coverage over the window").

**Key references:**
- Boehmer, N. et al. (2024/2025). *Context in Public Health for Underserved Communities: A Bayesian Approach to Online Restless Bandits (BCoR).* arXiv:2402.04933.
- Verma, S. et al. (2024). *A Decision-Language Model (DLM) for Dynamic Restless Multi-Armed Bandit Tasks in Public Health.* arXiv:2402.14807.

**Theoretical properties:** BCoR has regret bounds vs. the Bayes-optimal index policy; DLM is primarily an engineering advance for operationalising the priority structure. Both are newer and less battle-tested in deployment than the Mate-Wang line.

## Recent Developments (2023–2026)

- **Fairness / equity constraints** are now well-studied: ProbFair (Li et al. 2022), soft-fairness (Verma et al. 2023), probabilistic fairness KDD 2023 (Herlihy et al.), and frequency/window constraints (arXiv:2502.00045, 2025). All give plug-in modifications to the Whittle-index recipe that add a per-arm minimum pull-probability — directly addressing the user's "don't cut off any village or language group" constraint.
- **Off-policy evaluation of RMAB policies** under confounded historical data is now a focused subfield, motivated specifically by ARMMAN's situation (historical data from a non-random allocation). Recent RCT-retrospective-reshuffling estimators (Boehmer et al. 2024) let you evaluate candidate RMAB policies against a fielded control arm with lower variance than naive IPS. This is directly relevant to GreenFurrow's board-approved pilot design.
- **LLM-assisted reward shaping** (DLM, 2024) is a new but unproven-in-field direction that would let the field director state fairness and priority intent in natural language.
- **Network-extended RMAB** (arXiv:2512.06274, Dec 2025) generalises to networked arms — *not needed here* because calls do not propagate through a social network in this setting. Flagged for completeness.

## Research gaps

- **Confounded-data identification.** The canonical RMAB deployment papers assume either random historical assignment or a pilot with a random arm. GreenFurrow has neither historical randomisation nor (yet) a running pilot. The literature addresses this via DFL (endogenise the downstream policy during training) or RCT-retrospective-reshuffling post-hoc, but there is no turnkey, field-tested protocol that handles this cleanly for a small-analyst-team NGO.
- **Explainability.** Whittle-index values are continuous scores that can be ranked and explained per-farmer as "this farmer's model says calling them now is worth X engagement-months", which is auditable — but the *model* that produced those scores is a Markov chain fit on historical data, which is itself hard to explain to a district auditor. An additional layer (a simple post-hoc rationaliser: "this farmer was selected because they listened 6 months straight and then stopped for 2") is commonly bolted on in practice but is not standardised.
- **Small time-horizon (T ≈ 6–8).** Whittle's asymptotic-optimality results are cleanest as the horizon grows; finite-horizon variants (Ghosh et al., AAMAS 2025, "Finite-Horizon Single-Pull Restless Bandits") are newer and less deployed.

## References cited (consolidated)

1. Whittle, P. (1988). Restless bandits: activity allocation in a changing world. *J. Appl. Probab.* 25A: 287–298.
2. Weber, R. R., & Weiss, G. (1990). On an index policy for restless bandits. *J. Appl. Probab.* 27(3): 637–648.
3. Mate, A., Killian, J., Xu, H., Perrault, A., Tambe, M. (2020). Collapsing Bandits and Their Application to Public Health Interventions. *NeurIPS 2020.*
4. Mate, A., Madaan, L., Taneja, A., Madhiwalla, N., Shah, S., Mehta, J., Hegde, A., Jain, M., Tambe, M. (2022). Field Study in Deploying Restless Multi-Armed Bandits: Assisting Non-Profits in Improving Maternal and Child Health. *AAAI 2022.*
5. Wang, K. et al. (2023). Scalable Decision-Focused Learning in Restless Multi-Armed Bandits. *AAAI 2023.* arXiv:2202.00916.
6. Li, D., Varakantham, P. (2022). Efficient Resource Allocation with Fairness Constraints in Restless Multi-Armed Bandits (**ProbFair**). *UAI 2022.* arXiv:2206.03883.
7. Verma, S. et al. (2023). Towards Soft Fairness in Restless Multi-Armed Bandits. arXiv:2207.13343.
8. Herlihy, C., Prins, A., Srinivasan, A., Dickerson, J. P. (2023). Planning to Fairly Allocate: Probabilistic Fairness in the Restless Bandit Setting. *KDD 2023.*
9. Liu, K. (2025). Relaxed Indexability and Index Policy for Partially Observable Restless Bandits. *Management Science* 71(12).
10. Boehmer, N. et al. (2024/2025). Context in Public Health for Underserved Communities: A Bayesian Approach to Online Restless Bandits. arXiv:2402.04933.
11. Verma, S. et al. (2024). A Decision-Language Model (DLM) for Dynamic Restless Multi-Armed Bandit Tasks in Public Health. arXiv:2402.14807.
12. Harvard Teamcore research page: *AI for Assisting NGOs in Improving Maternal and Child Health Outcomes.*
