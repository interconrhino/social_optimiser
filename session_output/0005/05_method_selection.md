# Method Selection

**Session:** 0005

## Selected Algorithm

**Name:** DPO-PRO (Direct Preference Optimization with Preference Robustness)
**Category:** Distributionally Robust Preference Learning (χ²-DRO localised to the preference-label conditional, applied on top of DPO fine-tuning of a 3–8B open-weights LLM)
**Type:** Exact (closed-form worst-case; unbiased gradient estimator; solved with standard gradient descent — no inner min–max solver)

**Why this algorithm:**

The user's formal specification has four defining features, and DPO-PRO matches all four natively. First, the core loss is pairwise preference learning (Bradley–Terry structure on soft labels) — DPO-PRO is built on DPO, which is exactly this. Second, the user has explicit per-pair evidence of annotator disagreement (q-values from ~60–90 resident panellists per district); DPO-PRO consumes exactly this kind of soft score q and uses it to calibrate an uncertainty radius per pair. Third, the user has explicitly rejected "hedge against everything" robustness as too timid, and DPO-PRO's χ² ambiguity set is localised to the preference conditional — not the joint — which is the very property the paper claims and which Dr-DPO lacks. Fourth, the method is a drop-in modification of the DPO loss with negligible extra compute and has been demonstrated on an A100 40 GB at batch size 2 on an actual social-sector public-health task (ARMMAN / maternal health), matching the user's compute budget and constraint set almost exactly.

**Approximation guarantees:**

- The worst-case preference inside the χ² ball has a closed form: `p̂(y₁ ≻ y₂ | x) = min{1, q + √(ρ · q(1-q))}`. No approximation is introduced at this step.
- The DPO-PRO loss is equivalent to `ℒ_DPO + min{1-q, √(ρ·q(1-q))} · (ℓ₁ − ℓ₋₁)` — an exact regularised DPO loss.
- Gradient estimate is **unbiased** (Proposition 4.1 of Kim et al. 2025, via Danskin's theorem).
- Therefore the training procedure is exact in the DRO sense; stochasticity enters only through ordinary SGD minibatch noise.
- Note: "exact DRO loss" is not the same as "exact policy optimum" — as with any deep-network training, convergence to global optimum of the non-convex loss landscape is not guaranteed. This limitation is inherited from DPO and is a property of LLM training, not of the DRO layer.

**Computational complexity:**

- Per training step: same as vanilla DPO — one forward + one backward pass through the 3–8B model on a pairwise minibatch. The extra DRO regulariser is an O(batch) scalar computation; negligible.
- Memory: fits on a single A100 40 GB at batch size 2 with LoRA or full-weight updates (as in the paper); two epochs SFT + one epoch DPO-PRO is the reference recipe.
- Total training for a 3–8B model on ~9,000 pairs: comfortably inside a "handful of A100s × six months" budget — likely days to a couple of weeks wall-clock per full run, leaving room for hyperparameter sweeps.
- Inference: identical to any other fine-tuned open-weights LLM of that size. Single-GPU on-premises is feasible; 4-bit or 8-bit quantisation gives further headroom for cities with more modest hardware.

**Known limitations for this problem:**

1. **Preference-function drift between districts.** DPO-PRO's ambiguity set is calibrated from training-time annotator disagreement. It is not an automatic shield against the case where residents in a new city genuinely weight priorities differently (e.g., "climate resilience is now dominant"). Partial mitigations: collect a small pilot pairwise batch in each new district and do a short fine-tune; or widen ρ at deployment; or use the assistant as a *short-list generator* only, with delegates always reviewing.
2. **Expert vs. resident label fusion is not built in.** The paper operates on a single channel of soft labels. The user has two (civic-design reviewers + residents). A principled fusion is not part of DPO-PRO as published — straightforward practical options: (a) use reviewer labels only for ρ-calibration on a held-out set, (b) treat reviewer labels as a prior via an additional weighted loss term, (c) train a small reviewer-to-resident correction model and apply it before soft-score aggregation. Option (a) is the cleanest starting point.
3. **ρ must be tuned.** The only new hyperparameter is the radius ρ. Paper uses a small held-out split for this. With ~9,000 pairs and 180 district-prompts, sensible cross-validation folds should cluster by district to reflect the deployment distribution-shift structure.
4. **No uncertainty estimates at inference.** The method outputs a score; it does not directly output "I am unsure about this pair, please ask a delegate." For the user's stated goal of a *pre-ranking* short list (delegates still review), this is acceptable. If per-pair inference-time uncertainty becomes important, a small ensemble (e.g., 3 LoRA heads) would add that capability at modest extra cost.

## Why not the alternatives

| Alternative | Reason not selected |
|---|---|
| Dr-DPO (Wu et al. 2024) | Uncertainty set covers the joint distribution via KL; produces the "timid across the board" over-conservative behaviour the user has explicitly read about and rejected, and requires exponential-reweighting approximations rather than a closed form. |
| Standard DPO / vanilla preference learning | No distributional robustness at all; reproduces the user's earlier prototype failure mode (over-commits to superficial training patterns and generalises badly to new districts). |
| Symmetric-loss / nrDPO-style noise-rate-corrected losses | Requires assuming and estimating a parametric label-noise model (e.g., symmetric flip rate ε). The user's noise structure is explicitly heteroscedastic (some pairs 60/40, others 95/5) and includes covariate shift, neither of which a fixed symmetric flip rate captures. |
| DRO-REBEL (relative-reward regression) | Newer and less validated; uses a regression rather than pairwise-CE framing, which is a less natural fit for the user's pairwise data collection pipeline and does not yet have a social-sector track record. |
| Classic operations-research methods from the catalog (LP, IP, matching, etc.) | None match the problem structure. The decision variables are LLM parameters, the objective is a robust statistical-learning loss, and there is no resource-allocation / combinatorial structure to exploit. |

## What the organisation needs before starting

- **Data to collect:**
  - Per-pair soft-score `q_i` (fraction of panel preferring bundle 1), which they already have implicitly.
  - A per-pair *confidence / variance* signal — they can compute this from the 60–90 panellists' votes directly (binomial variance, or bootstrap resampling of individual votes).
  - A held-out **district-level** split: reserve 2–3 districts entirely for validation and 1 for "pretend-deployment" testing. This is essential for tuning ρ against the real target (distribution shift), not just in-district held-out pairs.
  - Optional but recommended: a small re-test panel (same panellists, same pairs, some weeks later) to measure intra-annotator consistency and calibrate `q` aggregation.

- **Skills required:**
  - Comfort with HuggingFace `transformers` + `trl` (or equivalent) for DPO-style fine-tuning.
  - Basic familiarity with DRO concepts (one hyperparameter ρ; no inner min–max).
  - LoRA / parameter-efficient fine-tuning experience to keep the 3–8B model within a single-GPU memory budget.
  - Standard ML evaluation: held-out pairwise accuracy, calibration plots (predicted probability vs. empirical agreement), and ranking metrics (Kendall τ or NDCG over delegate-sized short lists).

- **Estimated effort:**
  - Weeks 1–2: data plumbing, per-pair `q` computation, district-level split design, choice of base model (Llama-3 8B or Mistral 7B class).
  - Weeks 3–6: SFT on bundle descriptions + DPO-PRO implementation (short — the DPO-PRO regulariser is roughly ten lines on top of a standard DPO trainer).
  - Weeks 7–14: ρ sweep, ablations against vanilla DPO and Dr-DPO baselines, qualitative review with internal delegates.
  - Weeks 15–20: pilot in one of the three new partner cities, with pre-registered success criteria.
  - Weeks 21–26: roll-out to the remaining two cities and pre-autumn-cycle hardening.
  - Comfortably within the six-month runway for a two-person ML team.
