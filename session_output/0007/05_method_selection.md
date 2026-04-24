# Method Selection

**Session:** 0007

## Selected Algorithm

**Name:** **Whittle Index Policy for a Partially Observable Restless Multi-Armed Bandit**, fit using **Decision-Focused Learning (DFL)** for transition-model estimation, and modified with a **ProbFair-style per-subgroup minimum-pull-probability constraint** for equity.

**Category:** Sequential resource allocation under partial observability (RMAB — the `influence_maximisation (POMDP)` family specialised to independent, non-networked arms).

**Type:** **Approximate** — Whittle-index is a principled relaxation-based index policy with asymptotic optimality guarantees (not exact because the underlying problem is PSPACE-hard).

### Why this algorithm (given GreenFurrow's formal structure and scale)

1. **Exact structural fit.** The formal spec — 28,000 independent units each with a latent engagement state that evolves monthly, K = 400 actions per round, T = 6–8 rounds, maximise cumulative engagement — is the canonical RMAB setting. Whittle's relaxation is the standard principled attack on this exact class. Every structural feature of the problem (multi-period, budget-per-period, partial observation between rounds, independent arms, cumulative-over-horizon objective) lines up 1:1 with the assumptions of the Whittle-index derivation.

2. **Direct real-world precedent.** ARMMAN's maternal mHealth programme is a near-identical operational setting (population in the thousands-to-tens-of-thousands, automated voice advisory, small human-caller budget used to re-engage drifters, monthly/weekly decision cadence). A deployed, field-validated Whittle-index pipeline with documented RCT-grade improvement over round-robin already exists there (Mate et al. 2022). GreenFurrow is structurally one step away from ARMMAN's setting — the same algorithm class transfers with minimal modification.

3. **DFL handles the confounded historical data.** The user explicitly flagged that the historical call logs reflect the rotation rule plus helpline-triggered calls, not random assignment. A two-stage approach (fit a transition model by maximum likelihood, then plan) can produce a policy that is optimal against the wrong transition model. DFL optimises the transition-model parameters to minimise the *downstream policy regret* — exactly addressing this confound (Wang et al. 2023). No other RMAB variant addresses this specific pathology as directly.

4. **ProbFair-style fairness constraint matches the user's stated equity requirement.** The user said any replacement rule "must not quietly cut off certain villages or language groups". ProbFair (Li & Varakantham 2022) imposes a strict lower bound on the per-arm pull-probability while preserving the Whittle-index ranking above that floor. Grouping arms by village × language and imposing a per-group floor gives the user precisely the "no-group-systematically-starved" guarantee they asked for, with a one-line modification to the index-sorting step.

5. **Scale is comfortably tractable.** Index computation is O(|S|³) per arm and the state space is small (listening categories over the last few months — say 8 to 16 states). For 28,000 farmers this runs in under a minute on a laptop; the monthly selection is a sort. Two analysts comfortable with Python can build this from open-source RMAB libraries.

### Approximation guarantees

- **Whittle-index policy is asymptotically optimal** as N → ∞ under the indexability condition (Weber & Weiss 1990). ARMMAN-scale experiments show the finite-N gap to the LP upper bound is small (typically <5% on their benchmarks).
- In the partially observable setting, *relaxed indexability* (Liu 2025) gives a verifiable sufficient condition for the index policy to be well-defined and provides efficient online index computation with bounded error. This is the current theoretical state of the art and applies here.
- DFL does not come with closed-form regret bounds — it is an empirical improvement over two-stage estimation, with reported gains of 20–30% on ARMMAN data in the Wang et al. paper.

### Computational complexity

- **Offline model fitting (DFL):** minutes to hours on a laptop for 28,000 farmers × 5 years of history. Small state space, standard PyTorch or JAX.
- **Monthly index computation:** O(N · |S|³) ≈ 28,000 × 10³ ≈ 3 × 10⁷ ops — seconds.
- **Monthly selection:** O(N log N) sort + a per-subgroup floor check — milliseconds.
- Total runtime budget for one monthly run: well under a minute, and fully reproducible.

### Known limitations for this problem

1. **Indexability is not guaranteed a priori** — it must be checked once the Markov chain model is learned. In practice, most public-health RMAB models are indexable, but this is a step the analysts must verify. Liu (2025) gives the online verification procedure.
2. **Finite-horizon (T ≈ 6–8) is small** compared to the asymptotic regime. The policy is still near-optimal empirically at these horizons, but confidence in the margin vs. rotation shrinks for T < 5. Finite-horizon RMAB variants exist (Ghosh et al., AAMAS 2025) and can be swapped in if the pilot shows this matters.
3. **Identifiability from observational data is fundamentally limited.** Even DFL cannot fully recover the call-effect if the historical assignment policy is deterministic in certain states. The pilot's randomised control arm is what closes this gap — without it, quantitative claims about "improvement over rotation" would remain model-dependent.
4. **Explainability is partial.** The index value is a continuous score and can always be ranked, but it is derived from a learned Markov model that is hard to communicate to an auditor. A post-hoc rationaliser ("you were called because you listened for 6 months then stopped for 2 — our data says calls recover about 40% of farmers in this situation") is recommended as a wrapper.
5. **Arm-independence assumption.** The RMAB framework assumes no spillover between arms. Calls do not propagate through a social network in this setting (consistent with the brief), so this holds — but if, in future, the intervention were to shift to village-level peer training, the framework would need to change to a networked-RMAB variant.

## Why not the alternatives

| Alternative | Reason not selected |
|---|---|
| **Plain Whittle-index without DFL** (fit transition model by MLE then plan) | The historical data is confounded by the current rotation-plus-helpline allocation. Two-stage MLE will fit the wrong transitions, and the downstream Whittle policy will be optimal against the wrong model. DFL is a principled fix for this exact pathology. |
| **Monthly Integer Programming / knapsack top-K** (Alternative 1 from classification) | Treats each month as independent; ignores the fact that observations accumulate and that the value of a call depends on a latent state. The user explicitly cares about "early warning signs" and cumulative engagement across the window — both of which require multi-round planning. An IP also gives no principled way to handle partial observability of the engagement state. |
| **Simulation / ABM alone** (Alternative 2) | Does not produce the monthly 400-farmer list. Agent-based simulation is a validation companion — it is the right tool to *evaluate* the Whittle policy against the rotation under different model assumptions before field deployment, but it is not a planner. |
| **Bayesian Contextual Online RMAB (BCoR)** | Strong recent method, but less battle-tested in deployment than the Mate-Wang Whittle line and introduces tuning complexity (prior specification, hyperparameters) that GreenFurrow's two-analyst team would find harder to maintain. Worth revisiting in version 2 after the first pilot cycle. |
| **Decision-Language Model (DLM) reward shaping** | A useful add-on for translating field-director priorities into the objective, but not a standalone planner. Can be layered on later. |
| **Networked / peer-influence RMAB** | Calls in this setting do not propagate through a peer network; the arm-independence assumption holds. Adding networked-arm machinery would introduce modelling burden without modelling gain. |

## What the organisation needs before starting

- **Data to collect / extract:**
  - Per-farmer monthly listen outcome (binary: listened ≥ some threshold, yes/no) and listen duration for all 60 months.
  - Per-farmer monthly "called" indicator from the advisor logs.
  - Static farmer attributes table (district, village, language, farm size, phone type, distance to office, collective membership).
  - Monthly district-level rainfall and market price.
  - Call-outcome notes from advisor logs (whether the call reached the farmer, tone) — optional but useful for modelling call-success probability.
  - The **pilot design document** defining which farmers are in the treatment arm (Whittle-selected) vs the control arm (rotation), and the rule for the split.

- **Skills required:**
  - Python (pandas, NumPy) — both analysts have this.
  - SQL for log extraction — both analysts have this.
  - Exposure to probabilistic modelling / Markov chains — one analyst will need to skill up here (1–2 weeks of reading + a worked example). Not expert-level, but they need to understand what they are fitting.
  - PyTorch or JAX for the DFL fitting — moderate ramp-up; a worked reference implementation from the ARMMAN codebase cuts this to days.
  - No in-house optimisation expertise is strictly needed — open-source RMAB libraries (e.g., the Harvard Teamcore group's released code) wrap the index computation.

- **Estimated effort:**
  - **Month 1–2:** Data extraction, state-representation design (how many engagement states and what they mean operationally), exploratory modelling.
  - **Month 2–3:** Fit DFL model, verify indexability, run the policy against historical data with off-policy evaluation.
  - **Month 3–4:** Pilot design finalisation (treatment vs control split, equity floors, must-call exceptions), tooling for the monthly call-list artefact, dashboard for the field director.
  - **Month 4–12:** Run the 6–8 month pilot, produce monthly lists, monitor, analyse at end.

  Total pre-pilot build: **~3–4 months of analyst time (shared across the two analysts, not full-time).**
