# Formal Problem Specification

**Session:** 0005
**Domain:** civic technology / participatory democracy (preference learning for a ranking / scoring assistant)

## Decision Variables

- **θ ∈ ℝ^d** — the parameters of a pre-trained open-weights language model of size 3–8B, to be fine-tuned. Continuous, unbounded (in practice: bounded by the pre-trained initialisation and any regularisation / adapter parameterisation used, e.g. LoRA-style low-rank updates of dimension d' ≪ d).
- **s_θ(c, q, b) ∈ ℝ** — the induced bundle score implied by θ: given district context c, framing prompt q, and candidate bundle b, the model outputs a scalar preference score. (This is not itself a decision variable — it is a function of θ. The actual decision space is θ.)

The final deployed object is the score function; the decision variables are the LLM weights that parameterise it.

## Objective Function

**Direction:** Minimise expected deployment ranking error under a worst-case preference distribution in a bounded neighbourhood of the empirical pairwise distribution, where the "neighbourhood" is calibrated to label-noise uncertainty.

**What:** Fit θ so that at deployment, in new districts whose preference distribution may have shifted from the training distribution, the induced pairwise preference predictions P̂(b₁ ≻ b₂ | c, q; θ) match the true latent resident preference — while remaining cautious (closer to 0.5) specifically on (c, q, b₁, b₂) tuples where the training panel's evidence itself was noisy or split.

**Form (sketch):**

```
min_θ  sup_{P ∈ U(P̂_train)}  E_{(c,q,b₁,b₂,y) ~ P}  [ ℓ( g_θ(c,q,b₁,b₂) , y ) ]
```

Where:
- `y ∈ {0,1}` is the binary outcome of a pairwise comparison (1 if b₁ preferred, 0 if b₂ preferred);
- `g_θ(c,q,b₁,b₂) = σ( s_θ(c,q,b₁) − s_θ(c,q,b₂) )` is the induced Bradley–Terry-style pairwise probability;
- `ℓ(·,·)` is a proper pairwise loss (e.g., binary cross-entropy);
- `P̂_train` is the empirical distribution over pairwise training records;
- `U(P̂_train)` is an uncertainty set around `P̂_train` — a ball of plausible deployment / label-true distributions. The key modelling choice is that `U` is localised to the *preference-label* component of the joint distribution, not every source of training noise.

Equivalently, the objective can be viewed as: maximise pairwise ranking accuracy on a worst-case perturbation of the training preference distribution within a bounded uncertainty set.

## Constraints

| # | Constraint | Type | Form |
|---|---|---|---|
| 1 | Score consistency: preference prediction is antisymmetric in the two bundles | Hard | `P̂(b₁ ≻ b₂ | c,q;θ) = 1 − P̂(b₂ ≻ b₁ | c,q;θ)`, enforced by construction via score-difference parameterisation |
| 2 | Model fits on a single GPU at inference | Hard | parameter count of θ ≤ ~8B; quantisation-compatible |
| 3 | On-premises inference only (no calls to external APIs) | Hard | deployment artefact is a local weight file, not an API dependency |
| 4 | Pair-level cautiousness: on pairs whose training label was uncertain, predicted probability must stay near 0.5 in expectation | Soft (induced by objective) | calibration: when empirical split was 60/40, model's predicted probability should not confidently exceed ~0.6 |
| 5 | Training budget | Hard | fits on "handful of A100-class GPUs" × ≤ 6 months calendar; implies limited hyperparameter sweep budget |
| 6 | No-privacy-leak: deployment content stays local | Hard | architectural, satisfied by constraint 3 |
| 7 | Uncertainty set U is "surgical" — it restricts perturbations to the preference-label / reward component, not to the entire training distribution | Hard (design requirement stated by user) | U acts on P(y | c,q,b₁,b₂), not on P(c,q,b₁,b₂) |

## Parameters (Known Inputs)

| Parameter | Description | Certainty |
|---|---|---|
| D_train = {(c_i, q_i, b_{i,1}, b_{i,2}, y_i, w_i)}_{i=1..N} | Pairwise dataset of ~9,000 records; `w_i` summarises per-pair annotator-agreement / consistency evidence | Known (collected) |
| N | Number of training pairs | ≈ 9,000 |
| K | Number of distinct district-prompts | ≈ 180 |
| p_split_i | Empirical agreement rate for pair i (fraction of annotators who chose the majority side) | Estimated per pair |
| Expert annotations | Separate pairwise labels from trained civic-design reviewers on a subset of pairs | Known, biased proxy |
| θ₀ | Pre-trained open-weights LLM checkpoint (3–8B) | Known (public checkpoint) |
| Compute budget | Several A100-class GPUs × six months | Known |
| Deployment districts | Three new partner cities | Known as a target; their context distributions are not yet observed |
| ε (uncertainty-set radius) | Size of the label-distribution ball U that robustness hedges against | To be tuned (not known a priori) |

## Uncertainty Structure

This is the defining feature of the problem. There are two distinct layers of uncertainty, and the user has explicitly asked that robustness target one of them without penalising the other:

1. **Aleatoric label noise on the preference signal `y`.** For any given (c, q, b₁, b₂), the "true" underlying resident preference is a probability in [0,1], not a binary label, and the observed majority vote is a noisy sample from it. Per-pair annotator agreement `w_i` gives direct evidence about how sharp this probability is.
2. **Covariate / preference-function shift between training and deployment districts.** At deployment, (c, q) distributions differ from training, and the conditional preference function `P(y|c,q,b₁,b₂)` itself may shift (priorities like climate resilience weigh differently).

The uncertainty set `U(P̂_train)` is required to be **localised to the conditional preference component** — i.e. it captures both (1) label noise and (2) drift in the preference function — but is explicitly NOT a worst-case set over the full joint distribution (which the user reports produces timid, globally-pessimistic models). This is the "surgical robustness" requirement.

The problem is therefore a **distributionally robust preference learning problem** with a structured, label-side uncertainty set, not a generic DRO on all inputs.

The decision process is **one-shot** at training time in the sense that the training recipe is chosen and the model is then deployed; but the statistical structure (learning a decision rule that must generalise to an unseen shifted distribution) is the defining feature.

## Scale

- Decision variables: depends on parameter-efficient adaptation choice — full 3–8B weights if full fine-tune, or ~10M–100M effective trainable parameters if LoRA/adapter.
- Training pairs: ~9,000
- District-prompt cells: ~180
- Constraints: small and mostly architectural; the core "constraint" is the shape of the uncertainty set.
- Time horizon: training is one-shot; deployment is recurring over PB cycles.

## Assumptions Made

1. The user's description of "better" as "the bundle residents of this district would pick in a pairwise comparison" licenses a Bradley–Terry-style pairwise-preference model with a learned latent score. They did not use this vocabulary but described exactly this structure (pairwise comparisons → collective preference → ranking).
2. The per-pair annotator-agreement information (which is collected — they know which pairs split 60/40 vs. 95/5) can be reduced to a sufficient statistic `w_i` and fed to the loss.
3. The expert reviewer labels are a secondary, biased-but-lower-variance signal; they do not need their own decision variables in the core formulation but affect how the loss is constructed.
4. "Surgical robustness" is interpreted formally as: the adversary in the min-max only perturbs the conditional label distribution `P(y|c,q,b₁,b₂)`, not the marginal `P(c,q,b₁,b₂)`.

## Open Questions

- What metric to use for the uncertainty set's radius: KL, χ², total variation, or f-divergence? (Affects which robust-learning formulation applies.)
- How precisely to operationalise per-pair agreement `w_i`: as a soft label, as a weight on the loss, or as a per-pair uncertainty-set radius?
- Whether the expert-reviewer channel is used as a regulariser, a pre-training signal, or a calibration set.
- Whether partial observability / sequential learning at deployment (active queries to local panels) is in scope — the user did not mention this, so the formal spec treats training as one-shot.
