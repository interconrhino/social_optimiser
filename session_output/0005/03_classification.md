# Optimization Category Classification

**Session:** 0005

## Primary Match

**Technique:** Distributionally Robust Preference Learning (out-of-catalog; closest in-catalog analogue is "Simulation / Scenario Analysis Under Uncertainty", but the true structure is a robust statistical-learning / DRO problem on a pairwise-preference Bradley–Terry model).
**Catalog ID:** (no direct match in `optimization_catalog.json`); nearest catalog ID for discussion = `simulation`.
**Confidence:** Medium-High that the technique family is *distributionally robust preference learning*; Low that any existing catalog entry is the correct drop-in match.

**Matching signals (vs. the 8-entry catalog):**
- Decision variables are continuous (LLM parameters) — superficially LP-shaped, but the loss is non-linear and non-convex → Linear Programming is not a structural match.
- No binary selection or subset choice → Integer Programming, Matching, Constraint Satisfaction all ruled out.
- No routing, no network of locations → Network/Routing ruled out.
- No explicit multi-objective Pareto trade-off requested → Multi-objective Optimisation ruled out.
- No sequential influence cascade, no social-network structure over which an intervention propagates → Influence Maximisation (POMDP) ruled out.
- Central feature is **uncertainty + distribution shift**, and the user wants a training recipe that is robust to that uncertainty → Simulation is the nearest catalog family, but Simulation is about scenario-testing of a decision, not about fitting parameters under worst-case distributional perturbation.

**Why this fits (out-of-catalog framing):**

Structurally, the problem is: given a noisy empirical pairwise-preference dataset, fit a scoring function (parameterised by LLM weights) such that the *worst-case* preference-ranking loss over a bounded neighbourhood of the empirical label distribution is minimised. That is the defining form of **distributionally robust optimisation (DRO)** applied to **pairwise / preference learning**. The user's explicit design requirement — that robustness be "surgical" and targeted at the preference-label component of the data rather than hedging against every possible training-time perturbation — is a textbook description of a **reward-side / conditional DRO** formulation, as opposed to generic input-space DRO. The LLM fine-tuning wrapper is implementation; the optimisation problem underneath is preference learning with a robust loss.

**Contraindications checked (against the nearest catalog family, Simulation):**
- Simulation contraindication: "A single best decision needs to be computed — use LP/IP instead." Partially applies here: we DO need to compute a single best θ, not explore scenarios. This is why Simulation is not a clean match — the user's task is training, not scenario-testing.
- Simulation contraindication: "Uncertainty is low." Does not apply — uncertainty is central.

## Alternative 1

**Technique:** Classical (non-robust) preference learning — Bradley–Terry / learning-to-rank with standard cross-entropy loss (e.g., what would be produced by a generic RLHF-style reward-model fine-tune on the pairwise data).
**Catalog ID:** (out-of-catalog).
**When this would be preferred instead:** If the user did not care about deployment distribution shift and did not have heteroscedastic label noise with per-pair evidence of disagreement — i.e., if the training panel were roughly representative of deployment districts and preferences were consistent.

## Alternative 2

**Technique:** Generic worst-case / fully-robust training (e.g., hedging against every source of training-time noise at once — a broad DRO ball over the joint distribution of inputs and labels).
**Catalog ID:** (out-of-catalog).
**When this would be preferred instead:** If the user did not know which sources of noise to hedge against, or if label noise and input distribution shift were tightly coupled. The user has explicitly rejected this framing: they report that it produces an assistant that is timid across the board, i.e., it pays the robustness tax everywhere instead of where it is actually needed.

## Why alternatives were not the primary pick

Alternative 1 (standard preference learning) would reproduce the failure mode the user already observed with their earlier prototype: over-commit to surface patterns in the training panel and generalise badly to new districts. Alternative 2 (fully-generic DRO) produces the timidity pathology the user has read about and rejected. The primary pick — DRO *localised to the preference-label / reward conditional* — is the formulation that matches the user's explicit requirement: be cautious exactly where the training preference signal is ambiguous or likely to shift, and not elsewhere.

## Note on catalog coverage

The 8-entry `optimization_catalog.json` covers classical operations-research shapes (allocation, routing, matching, POMDP-influence). It does not currently cover the **statistical-learning / robust-ML** family, which is where this problem lives. The method-research stage should therefore search the ML literature for "distributionally robust preference learning" / "robust reward modelling" / "DRO for RLHF" / "pairwise preference learning with label noise and covariate shift," rather than searching within the catalog's algorithm-example lists.
