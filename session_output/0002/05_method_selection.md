# Method Selection

**Session:** 0002

## Selected Algorithm

**Name:** **Decision-Focused Learning for Restless Multi-Armed Bandits (DF-Whittle)**, paired with an **Inverse-Propensity-Weighted (IPW) correction** on the learning loss to address the historical selection bias.

**Category:** Sequential resource allocation under unknown Markov dynamics; RMAB with learned transition kernel and end-to-end training against downstream policy reward.

**Type:** Approximate (asymptotically optimal as N → ∞); empirically near-optimal at the N ≈ 800 scale of this deployment.

---

**Why this algorithm**

Four features of Riverbank's problem drive the choice:

1. **Independent Markovian per-family dynamics with a weekly shared budget.** This is the textbook structure of a restless multi-armed bandit: each family is an "arm" whose state evolves as an MDP, and the organisation can "pull" at most K = 40 arms per period. Whittle-index decomposition is the canonical approximate solver for this structure.
2. **Unknown transition dynamics with rich per-family features and historical trajectories.** Transitions are not observed directly — they must be learned from 3 years of logged data. DF-Whittle is specifically designed for the regime where (a) arm transitions depend on observable features through a parametric model and (b) historical trajectories exist to fit that model.
3. **Decision-quality ≠ predictive accuracy.** Fitting the transition model by maximum-likelihood (predictive loss) treats all transition-probability errors equally. In practice, the errors that matter are the ones that change which 40 families get visited — which is typically a small fraction of all transition estimates. Training the predictive model end-to-end against the downstream Whittle-policy reward concentrates learning effort where it moves the decision.
4. **Selection bias in the historical data.** The director explicitly flagged that past visits were chosen by caseworker judgement rather than at random. Layering an IPW (or doubly-robust) correction onto the DFL loss addresses this without inventing new algorithmic machinery: estimate the behavioural propensity `π_beh(visit | features, state)` from the same historical data, reweight observed trajectories by the inverse of this propensity, then run DFL. This is a minor extension on top of the base algorithm and directly mitigates the deployment risk the director raised.

**Approximation guarantees**

- Whittle-index policies are **asymptotically optimal as N → ∞** under the indexability condition (Weber & Weiss 1990).
- Empirically at N in the hundreds to low thousands — the exact regime of this problem — Whittle policies typically achieve within 1–5% of the oracle optimal on RMAB benchmarks.
- DFL does not improve the asymptotic bound but **reduces decision regret in the finite-data regime** relative to a predict-then-optimise two-stage pipeline, by a margin that is often substantial on social-sector datasets.
- The IPW correction is unbiased under standard overlap conditions (every action has non-zero probability in the behavioural policy given features and state). Doubly-robust variants are robust even to mis-specification of either the propensity or transition model but not both.

**Computational complexity**

- **Training DF-Whittle:** dominated by the differentiable Whittle-index computation, which solves a linear system of size |S| = 3 per arm per step and backpropagates through it. Training time on the Wang et al. 2023 paper scales **linearly in N** and **polynomially in |S|** — a full training run on N = 800 arms and ~125,000 historical records should complete on a single modern GPU in hours, not days.
- **Inference (computing the weekly visit set):** compute the Whittle index for each of the N = 800 arms and pull the top K = 40. Per-week runtime is well under a minute.
- **Indexability check:** one-off numerical check per transition-matrix structure; tractable at |S| = 3.

**Known limitations for this problem**

- **Indexability is not guaranteed** under arbitrary learned transition matrices. If the learned transitions produce non-indexable MDPs for some families, Whittle's guarantees weaken. Fallback: GINO-Q (Biswas et al. 2024) or the fluid-LP policy, both of which handle non-indexable RMABs.
- **Finite-horizon effects.** Whittle's optimality theorems assume T → ∞. At T = 52 with a meaningful end-effect on welfare, finite-horizon corrections may be worth applying — but are unlikely to change the visit set materially.
- **The 3-state space is richer than the binary ARMMAN benchmark.** Transition-estimation variance is higher with more states. Expect to have to bin rare state-transition triples carefully or use informative priors in the feature network.
- **The soft geography / language / continuity constraints are not captured** by the base RMAB formulation. They should be handled by a **second-stage assignment step**: the RMAB picks the 40 families to visit each week; a matching-style assignment then pairs each selected family with a feasible caseworker. This two-stage decomposition is clean and avoids inflating the RMAB state space.

---

## Why not the alternatives

| Alternative | Reason not selected |
|---|---|
| **UCWhittle (online learning)** | Builds exploration in from the start, which is wasteful here: Riverbank has 3 years of historical data, so an offline warm-start is available and exploration should only be used as an adaptive layer in later years, not as the primary policy. |
| **Gaussian-approximation / Fluid-LP index policies** | Tighter asymptotic gap than classical Whittle, but at N = 800 the Õ(1/N) vs Θ(1/√N) distinction is immaterial; this method is better suited as a sanity-check benchmark, not the primary policy. |
| **Predict-then-optimise (MLE transitions + Whittle)** | Would be the simpler baseline, but trains the transition model to minimise predictive loss — a metric that is systematically mis-aligned with downstream decision quality on this class of problem. The director's data (with selection bias) makes this misalignment worse, not better. |
| **Integer Programming per week (the catalog's primary match)** | Solves the per-week selection problem but treats each week independently — loses the temporal coupling that makes early-week visits pay off over the rest of the year. Would systematically under-visit families in "at-risk" because the one-shot IP can't value the downstream-crisis-prevented. |
| **Monte Carlo simulation** | A scenario-analysis tool, not a decision procedure. Will be used downstream to evaluate candidate policies (via importance-sampling policy evaluation on logged data) but is not the primary method. |

---

## What the organisation needs before starting

- **Data to collect / formalise:**
  - Reconstruct the per-family week-by-week `(s_t, a_t, s_{t+1})` trajectories from caseworker notes for the last 3 years (this may already exist in a queryable form — confirm).
  - Finalise the per-family feature vector at intake: confirm which of the 10–20 candidate features are reliably collected and machine-readable.
  - Decide and document the crisis-weight parameter `c` (the director said "more heavily" — needs an actual number, ideally from a short elicitation exercise with the director and senior caseworkers).
  - Collect a hold-out cohort of ~300 families from the most recent 6 months for validation.

- **Skills required:**
  - One data scientist comfortable with PyTorch / JAX (for the differentiable Whittle module) and off-policy evaluation concepts.
  - One analyst to build the ETL from caseworker-note records into the trajectory format.
  - Senior programme input (director + two senior caseworkers) for a short elicitation to set the crisis weight and sanity-check the state-labelling rules.

- **Estimated effort (first full cycle):**
  - Data ETL + feature engineering: **3–4 weeks**
  - Implementation of DF-Whittle + IPW correction (starting from the public Wang et al. 2023 code): **3–4 weeks**
  - Off-policy evaluation of candidate policies: **2 weeks**
  - Shadow deployment (compute weekly recommendations, let caseworkers decide freely, compare outcomes): **3 months**
  - Total to go-live: **approximately 5–6 months**
