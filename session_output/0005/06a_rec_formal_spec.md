# Optimisation Recommendation — Formal Specification

**Session:** 0005
**Problem domain:** Participatory budgeting / civic technology (preference-aligned ranking assistant)
**Technique:** Distributionally Robust Preference Learning (χ²-DRO localised to the preference-label conditional)
**Algorithm:** DPO-PRO (Direct Preference Optimization with Preference Robustness), Kim, Verma, Tec & Tambe (2025)

---

## 1. Problem Formulation

### Decision Variables

- **θ ∈ ℝ^d** — parameters of a pre-trained open-weights language model (Llama-3 8B, Mistral 7B, or similar 3–8B checkpoint), fine-tuned either in full or via a parameter-efficient adapter (LoRA with rank r ≈ 16–64). Continuous; in practice constrained by the initialisation and (for LoRA) by the adapter rank r.

Induced objects (not decision variables — functions of θ):
- `s_θ(c, q, b) ∈ ℝ` — the scalar bundle score output by the model for district context `c`, framing prompt `q`, candidate bundle description `b`.
- `P̂(b₁ ≻ b₂ | c, q; θ) = σ( s_θ(c,q,b₁) − s_θ(c,q,b₂) )` — the induced Bradley–Terry pairwise preference probability.

### Objective Function

**Minimise** the worst-case pairwise preference loss over a χ² ball around the empirical soft-preference label for each pair:

```
min_θ   E_{(c,q,b₁,b₂) ~ D_train}  sup_{p ∈ Q(c,q,b₁,b₂, ρ)}   BCE( P̂(b₁ ≻ b₂ | c,q;θ) , p )
```

where the per-pair ambiguity set is

```
Q(c,q,b₁,b₂, ρ) = { p ∈ [0,1] : χ²(p ∥ q_i) ≤ ρ }
```

and `q_i` is the empirical soft preference (fraction of panellists preferring bundle 1 on record i).

**Equivalent closed-form loss** (Kim et al. 2025):

```
ℒ_DPO-PRO(θ) = ℒ_DPO(θ) + ∑_i min{ 1-q_i, √(ρ · q_i · (1-q_i)) } · ( ℓ₁(θ; i) − ℓ₋₁(θ; i) )
```

where `ℓ₁` and `ℓ₋₁` are the two branches of the standard DPO log-ratio loss (bundle 1 preferred vs. bundle 2 preferred).

**Interpretation:** the regulariser is largest when `q_i ≈ 0.5` (ambiguous pair) and vanishes when `q_i ∈ {0, 1}` (unanimous pair). This gives exactly the "surgical" behaviour the user asked for.

### Constraints

**C1 — On-premises inference:** The deployed artefact is a local weight file (or LoRA delta) loadable by the partner city's own inference stack. No external API call at inference time. → `θ ∈` (weights shippable as a local file, quantisable to 4/8-bit)

**C2 — Single-GPU inference:** Model size ≤ 8B parameters; compatible with 4-/8-bit quantisation for deployment on modest hardware.

**C3 — Antisymmetry of pairwise prediction:** `P̂(b₁ ≻ b₂ | c,q;θ) + P̂(b₂ ≻ b₁ | c,q;θ) = 1`, enforced by construction via `σ(score-difference)`.

**C4 — Surgical robustness:** The ambiguity set acts only on the label conditional `P(y | c,q,b₁,b₂)`, not the marginal `P(c,q,b₁,b₂)`. Satisfied by construction of `Q(·, ρ)`.

**C5 — Training compute budget:** A handful of A100-class GPUs × ≤ 6 months; per-run wall-clock ≤ ~2 weeks to allow hyperparameter sweeps.

### Parameters

| Symbol | Meaning | Value / Source |
|---|---|---|
| N | # training pairs | ≈ 9,000 (collected) |
| K | # distinct district-prompts | ≈ 180 |
| q_i | Empirical soft preference for pair i | Computed from per-pair panel votes (fraction preferring bundle 1) |
| n_i | # panellists who judged pair i | ~60–90 per district (known) |
| ρ | χ² ambiguity radius (single hyperparameter) | To tune via district-held-out cross-validation; paper's regime ρ ∈ [0.01, 1.0] |
| θ₀ | Pre-trained open-weights checkpoint | Llama-3 8B / Mistral 7B / similar |
| r | LoRA rank (if used) | 16–64 (standard) |
| η | Learning rate | ~1e-5 to 5e-5 for LoRA adapters |
| β | Standard DPO regularisation strength | Default 0.1 (DPO convention) |

### Uncertainty

Two sources, both captured by DPO-PRO's χ² ball over the label conditional:

1. **Aleatoric label noise** (residents disagree on pair i; `q_i` near 0.5). Handled by design: the regulariser grows with `q(1-q)`.
2. **Covariate / preference-function shift** between training districts and deployment districts. Partially handled: the ambiguity set permits the conditional `P(y|x)` to shift within a χ² ball of radius ρ, which generalises to plausible shifts at deployment. Not fully handled: large structural shifts (e.g., a new deployment city that weights climate resilience very differently) may require widening ρ at deployment or a small per-city pilot-data fine-tune.

Uncertainty is explicitly NOT placed over `P(c,q,b₁,b₂)` — this is the "surgical" constraint C4.

---

## 2. Recommended Algorithm

**Algorithm:** DPO-PRO (Kim, Verma, Tec, Tambe — 2025, arXiv:2509.02709)
**Class:** Distributionally robust statistical learning / robust preference optimisation for LLM fine-tuning.

### Why this algorithm

DPO-PRO matches every structural feature of the formal specification: (i) its loss is the pairwise-preference loss that the user's data-collection pipeline produces; (ii) it consumes per-pair soft scores `q_i` directly, which is exactly the evidence the user's 60–90-panellist pairwise studies yield; (iii) its χ² ambiguity set is localised to the preference conditional, giving "timid on ambiguous pairs, confident on clean pairs" rather than the across-the-board timidity of joint-DRO methods like Dr-DPO; (iv) it has a closed-form worst-case, so training is ordinary SGD with an unbiased gradient (Proposition 4.1 of the paper, via Danskin's theorem) and adds negligible compute over vanilla DPO; and (v) it has already been validated by its authors on a closely analogous social-sector task (ARMMAN maternal-health LLM fine-tuning with RMAB-driven evaluation) on a single A100 40 GB, which mirrors the user's hardware and deployment constraints.

### Theoretical properties

- **Optimality:** the DRO loss is exact (closed-form worst-case inside the χ² ball). The optimum of the resulting non-convex deep-network loss is approximated by SGD, as with any LLM fine-tuning.
- **Gradient estimator:** unbiased (Proposition 4.1, Kim et al. 2025).
- **Conservatism control:** single hyperparameter ρ; `ρ = 0` recovers vanilla DPO.
- **Complexity:** same asymptotic complexity as DPO per step. For a 3–8B model with LoRA adapters, ~days to ~1–2 weeks of A100 time for a full training run on 9,000 pairs with hyperparameter sweep.
- **Key reference:** Kim, C.W., Verma, S., Tec, M. & Tambe, M. (2025). *Preference Robustness for DPO with Applications to Public Health.* arXiv:2509.02709.

### Known limitations

1. The χ² ball is calibrated from training-time annotator disagreement. It captures "the training panel was split" robustness but only partially captures "deployment residents have genuinely different priorities." Mitigate with a pilot fine-tune in each new city or by widening ρ.
2. Does not natively fuse two label channels (residents + civic-design reviewers). Recommended practice: reserve the reviewer labels for ρ-calibration on a district-held-out split (see §4).
3. Produces no native per-pair inference-time uncertainty score. Acceptable because the user's assistant is a short-list generator reviewed by delegates, not an autonomous decision-maker.
4. Standard LLM-fine-tune caveats apply: non-convex, sensitive to random seed, LoRA rank, and learning-rate schedule. Pre-register at least three seeds per configuration.

---

## 3. Implementation Guidance

### Data requirements

| Data item | Description | Format | Source suggestion |
|---|---|---|---|
| Pairwise records | (c, q, b₁, b₂) text + `q_i` | JSONL with 4 text fields + float | Already collected (~9,000) |
| Per-pair soft score `q_i` | Fraction of panellists preferring bundle 1 | float in [0,1] | Compute from raw panel votes |
| Per-pair panel size `n_i` | # panellists who judged pair i | int | From panel metadata |
| District-level split | Assign each district to train / val / "pretend-deploy" test | list of district IDs | Random but stratified by city size and demographic profile |
| Reviewer channel (optional) | Civic-design reviewer pairwise labels on a subset | JSONL | Already collected |
| Base model | 3–8B open-weights checkpoint | HuggingFace repo | Llama-3 8B Instruct or Mistral 7B v0.3 |

### Key parameters to calibrate

- **ρ (χ² radius):** the defining DPO-PRO hyperparameter. Sweep on a log grid (e.g., {0.01, 0.05, 0.1, 0.3, 1.0}). Select on district-level held-out pairwise accuracy + calibration (ECE). Sensitivity: **HIGH** — this is the whole point of the method.
- **LoRA rank r:** 16 → 64. Sensitivity: medium. Larger rank helps if training data were cleaner; smaller rank is safer here.
- **β (DPO regularisation):** default 0.1; sensitivity: low–medium.
- **Learning rate η:** 1e-5 → 5e-5 for LoRA; sensitivity: medium.
- **# epochs:** 2 SFT + 1 DPO-PRO (paper's recipe) is a good starting point. Sensitivity: medium.

### Algorithmic steps

1. **Data prep.** For each pair i, compute `q_i = (# panellists preferring bundle 1) / n_i`. Flag pairs with `n_i < 30` for exclusion or higher ρ. Construct district-level train / val / test splits.
2. **SFT warm-up.** Two epochs of supervised fine-tuning of θ₀ on concatenated (c, q, b) → brief pro/con commentary, to adapt the base model to the civic-tech domain and to the bundle-description format.
3. **DPO-PRO fine-tune.** One epoch of DPO-PRO on the 9,000 pairs. Loss is vanilla DPO loss plus the closed-form regulariser `min{1-q_i, √(ρ·q_i·(1-q_i))} · (ℓ₁ − ℓ₋₁)`. Implementation is ~10 lines on top of a standard HuggingFace TRL `DPOTrainer`.
4. **ρ selection.** Evaluate each trained model on the held-out districts. Select ρ that maximises a composite of (a) pairwise accuracy on held-out districts and (b) calibration (predicted probability vs. empirical `q`).
5. **Deployment artefact.** Export merged LoRA weights, quantise to 4- or 8-bit, ship as a local weight file to each partner city.
6. **Inference.** For each candidate bundle `b` in a new district with context `c` and prompt `q`: compute `s_θ(c, q, b)`; sort bundles descending by score; return top-k as the pre-ranked short list for the delegate panel.

### Computational considerations

- **Training.** A 7B-class model with LoRA (r=32), batch 2, 2 epochs SFT + 1 epoch DPO-PRO on 9,000 pairs: ≤ 48 hours on a single A100 40 GB per run. A "handful" of A100s in parallel comfortably supports a full ρ sweep plus seed replicates within a month.
- **Scaling.** Dataset scale is modest (~9,000 pairs). DPO-PRO itself scales linearly in N; the LLM forward/backward is the dominant cost and is independent of the DRO layer. If the dataset grows to 10× (new cities contributing pairs), training time scales linearly.
- **Inference.** A 7B model in 4-bit quantisation runs on a consumer-class GPU; a delegate panel of 40 bundles per district scored in well under a minute. Suitable for on-premises deployment on modest hardware.

---

## 4. Validation

### How to evaluate solution quality

Three metrics, reported together:

1. **Held-out-district pairwise accuracy.** On pairs from districts the model did not see during training, how often does the model's predicted majority (`P̂ > 0.5`) agree with the actual panel majority? Primary metric.
2. **Calibration (Expected Calibration Error, ECE).** Plot `P̂` against empirical `q` on held-out pairs. A well-calibrated model that is appropriately cautious on ambiguous pairs should track the diagonal and not be systematically over-confident on `q ≈ 0.5` pairs. Secondary metric; this is how you demonstrate the "surgical robustness" story to a city council.
3. **Top-k ranking quality (NDCG@10 or Kendall τ) against a held-out district's residents.** The deployed artefact produces a ranking, not a label, so rank-correlation metrics are needed to check that the delegate-visible short list is ordered correctly.

### Baseline to beat

- **Primary baseline: vanilla DPO on the same data.** Same model, same SFT warm-up, same hyperparameters — only `ρ = 0`. DPO-PRO should match or beat on held-out pairwise accuracy AND show strictly better calibration on ambiguous pairs (this is its whole selling point).
- **Secondary baseline: Dr-DPO (Wu et al. 2024).** Report to demonstrate that the surgical form beats the joint-DRO form on held-out districts without paying a timidity tax.
- **Naive baseline: the coalition's current bundle-ordering heuristic (e.g., sort by estimated cost, or by delegate-proposed order).** The assistant should visibly beat this on both accuracy and delegate-reported "reflects our neighbourhood" ratings.

### Sensitivity analysis

1. **ρ sensitivity.** Sweep ρ ∈ {0, 0.01, 0.05, 0.1, 0.3, 1.0}; report the accuracy/calibration frontier. Expected: a sweet spot around ρ ≈ 0.05–0.3.
2. **Training-district leave-out.** Retrain with each city held out once; measure drop in held-out accuracy. High variance across cities ⇒ distribution shift is large and a per-city pilot-batch fine-tune is needed at deployment.
3. **Panel-size robustness.** Truncate `n_i` (e.g., use only the first 30 panellists per pair) and retrain; fragile accuracy at lower `n_i` suggests per-pair `q` is under-sampled.
4. **Reviewer-channel ablation.** Train with reviewer labels used for ρ-calibration only, vs. mixed into the training loss with various weights. Report whether reviewer infusion helps or hurts held-out-district accuracy.

### Pilot approach

1. **Retrospective pilot (Weeks 15–18).** Apply the trained model to a historical PB cycle in a city whose data was held out from training. Compare its short list against the delegates' actual bundle short list; score against the final neighbourhood vote turnout and approval margin.
2. **Prospective pilot (Weeks 19–24).** Deploy to ONE of the three new partner cities for the autumn 2026 cycle. Pre-register: (a) delegates' first-meeting agreement score with the pre-ranked short list (target: ≥ 70% agreement on at least 7 of 10 short-listed bundles); (b) total volunteer meeting hours vs. that city's pre-PB-assistant norm (target: ≥ 30% reduction); (c) final neighbourhood vote turnout and approval margin (target: no reduction vs. the coalition's historical norms for cities of similar size).
3. **Full roll-out** to the other two new cities only if the pilot hits 2 of 3 pre-registered criteria.

---

## 5. Key references

- Kim, C.W., Verma, S., Tec, M. & Tambe, M. (2025). *Preference Robustness for DPO with Applications to Public Health.* arXiv:2509.02709. https://arxiv.org/abs/2509.02709
- Kim, C.W., Verma, S., Tec, M. & Tambe, M. (2025). *Lightweight Robust Direct Preference Optimization.* arXiv:2510.23590. https://arxiv.org/abs/2510.23590  *(same method as above — arXiv-flagged text overlap)*
- Rafailov, R. et al. (2023). *Direct Preference Optimization: Your Language Model is Secretly a Reward Model.* arXiv:2305.18290.
- Wu, J. et al. (2024). *Towards Robust Alignment of Language Models: Distributionally Robustifying Direct Preference Optimization.* arXiv:2407.07880. (Dr-DPO; secondary baseline.)
- Bradley, R.A. & Terry, M.E. (1952). *Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons.* Biometrika 39(3/4): 324–345. (Pairwise-preference foundation.)
- Ben-Tal, A., El Ghaoui, L. & Nemirovski, A. (2009). *Robust Optimization.* Princeton University Press. (DRO foundations.)
- "On Symmetric Losses for Robust Policy Optimization with Noisy Preferences." (2025). arXiv:2505.24709. (Alternative family, not selected.)
