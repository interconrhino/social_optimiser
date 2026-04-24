# Method Research Findings

**Session:** 0005
**Technique category:** Distributionally Robust Preference Learning for LLM Fine-Tuning (DRO applied to the preference-label / reward conditional of a pairwise-preference objective)

## State-of-the-Art Algorithms

### 1. DPO-PRO (Direct Preference Optimization with Preference Robustness) ⭐ Recommended starting point

**How it works:**
DPO-PRO is a distributionally robust version of DPO in which the uncertainty set is placed **only around the observed soft preference probability** `q = P(y₁ ≻ y₂ | x)` — not around the full joint training distribution. It uses a **χ² (chi-squared) divergence ball** of radius ρ, giving the ambiguity set `Q(x,y₁,y₂,ρ) = {p : χ²(p ∥ q) ≤ ρ}`. The worst-case preference inside this ball has a closed form, `p̂ = min{1, q + √(ρ · q(1-q))}`, which means the DRO loss can be written as the ordinary DPO loss plus a regularisation term `min{1-q, √(ρ·q(1-q))} · (ℓ₁ − ℓ₋₁)`. The regulariser *penalises model overconfidence exactly on pairs where the preference signal is ambiguous* (q near 0.5) and has no effect on cleanly-decided pairs. This is the "surgical robustness" the user asked for — label-conditional only.

Per-pair soft scores `q_i` are derived from annotator agreement / repeated queries on the same pair. The method is a drop-in modification of the DPO loss with one extra hyperparameter (ρ), gradient estimates are unbiased (by Danskin's theorem, per Proposition 4.1 of the paper), and extra compute is negligible over vanilla DPO.

**Key reference:**
Kim, C.W., Verma, S., Tec, M. & Tambe, M. (2025). *Preference Robustness for DPO with Applications to Public Health.* arXiv:2509.02709. https://arxiv.org/abs/2509.02709
(A companion short paper by the same team is arXiv:2510.23590, "Lightweight Robust Direct Preference Optimization"; arXiv notes substantial text overlap — treat as the same method.)

**Theoretical properties:**
- χ² ambiguity set with closed-form worst-case inside the ball → loss is an explicit regularised DPO loss (no min–max solver needed).
- Gradient is unbiased (Proposition 4.1 via Danskin's theorem).
- "Significantly less conservative" than Dr-DPO and other full-distribution DRO variants because the ambiguity set does not cover the input marginal.
- Compatible with standard gradient-based optimisation; negligible overhead over DPO.
- Experiments use a single Nvidia A100 40 GB, batch size 2, two epochs SFT + one epoch DPO-PRO.

**Social sector use:**
The headline application in the paper is **public health** — specifically fine-tuning an LLM to support ARMMAN's maternal-health mobile programme (2,100 beneficiaries, K=210 weekly call allocations modelled as a Restless Multi-Armed Bandit). This is directly relevant: it demonstrates the method on a real, noisy, social-sector preference-learning pipeline with on-premises inference constraints similar to the user's.

### 2. Dr-DPO (Distributionally Robustifying DPO)

**How it works:**
Dr-DPO places a DRO ball over the **empirical pairwise distribution as a whole** (joint over (x, y₁, y₂, c)), typically with a KL divergence. This gives both pointwise-noise robustness (through the standard DPO β regularisation, which Dr-DPO shows is implicitly DRO) and an extra pairwise-noise robustness term controlled by a second hyperparameter β'. Because the divergence is KL over the full joint, the worst-case does not admit a simple closed form and the method uses an exponential-reweighting approximation.

**Key reference:**
Wu, J. et al. (2024). *Towards Robust Alignment of Language Models: Distributionally Robustifying Direct Preference Optimization.* arXiv:2407.07880. https://arxiv.org/abs/2407.07880

**Theoretical properties:**
- KL-ball DRO over the joint distribution; robust to both pointwise and pairwise noise.
- No closed form → uses exponential reweighting (heuristic approximation).
- Reveals that vanilla DPO is itself implicitly a pointwise DRO — useful theoretical context.
- Tends to be more conservative than DPO-PRO because the ambiguity set covers more of the distribution — this is precisely the "timid across the board" failure mode the user wants to avoid.

**Social sector use:** Primarily evaluated on general LLM alignment benchmarks; not specifically social sector.

### 3. Symmetric-loss robust policy optimization (rDPO / nrDPO family)

**How it works:**
Instead of a DRO framing, this family assumes a parametric label-noise model (e.g., symmetric noise with known flip rate ε) and uses a **symmetric / unbiased pairwise loss** that is provably robust under that noise model. Drop-in replacement for the DPO binary cross-entropy.

**Key reference:**
"On Symmetric Losses for Robust Policy Optimization with Noisy Preferences" (2025). arXiv:2505.24709. https://arxiv.org/html/2505.24709
Also: Noise-Aware DPO for RLAIF (2025, MDPI Applied Sciences 15, 19: 10328). https://www.mdpi.com/2076-3417/15/19/10328

**Theoretical properties:**
- Exact noise-rate correction under the assumed flip-noise model.
- Simple and easy to tune, but **relies on knowing or estimating a noise model**; does not natively handle covariate shift / preference-function drift between districts.

## Recent Developments

- The robust-DPO literature has moved rapidly in 2024–2025. The two dominant framings are now (i) **DRO localised to the preference conditional** (DPO-PRO) and (ii) **DRO over the joint** (Dr-DPO). Newer work (2025–2026) consistently reports that (i) is less conservative and more practical.
- An adjacent stream — DRO-REBEL (Distributionally Robust Relative-Reward Regression, arXiv:2509.19104) — extends the idea to regression losses over relative rewards rather than pairwise cross-entropy, and is worth watching but is not yet as well-validated on social-sector tasks as DPO-PRO.
- There is also an emerging thread on sequential / active preference elicitation (query new annotators when ambiguous), which could complement DPO-PRO at deployment but is out of scope for the current six-month pilot.

## Research gaps

- **Preference-function drift across deployment districts** (as opposed to label noise in training) is only partially covered by DPO-PRO's χ² ball. DPO-PRO's ambiguity set is calibrated from per-pair annotator disagreement, which captures "the resident panel wasn't unanimous" noise; it does not automatically capture "residents in the new city genuinely weight priorities differently." Practical mitigation: collect a small pilot-batch of pairwise data in each deployment district and warm-start / fine-tune locally, or widen ρ.
- **Heteroscedastic ρ** (different ρ per pair based on per-pair disagreement evidence) is a natural extension the paper touches on but does not fully formalise — worth implementing.
- **Expert-vs-resident channel fusion**: how to combine the small cleaner civic-design reviewer set with the larger noisier resident set is not directly addressed by DPO-PRO and is an open implementation question (simple options: use expert labels as a held-out calibration set for ρ, or as a prior via weighted loss terms).
