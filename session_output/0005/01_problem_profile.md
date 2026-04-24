# Problem Profile

**Session:** 0005
**Classification:** Technical
**Technical sub-type:** Unknown / uncertainty (noisy preference labels + covariate shift at deployment); secondary: Technical incentives (learning a quantitative scoring function)

## What they are trying to improve

The Northside Participatory Budgeting Coalition wants to give each volunteer "budget delegate" panel a software assistant that, given a district's context and a framing prompt, pre-ranks candidate project bundles so delegates refine a short list instead of hand-crafting every bundle from scratch. "Better" is defined precisely as: the bundle a representative panel of residents in that specific district would collectively prefer in a pairwise comparison over a five-year horizon. They want this to cut volunteer meeting time by roughly a third and extend PB to smaller cities that currently can't afford the volunteer labour.

## What limits what they can do

- **Inference environment:** must run on-premises inside each partner city's own infrastructure on modest hardware; no reliance on paid external LLM APIs at inference (data-residency rules in several cities forbid sending deliberation content off-site).
- **Model size:** 3–8B parameter open-weights LLM (fits on a single GPU).
- **Training compute:** a handful of A100-class GPUs.
- **Team:** two-person ML team.
- **Timeline:** six-month runway to pilot for autumn 2026 PB cycles.
- **Data scale:** ~9,000 pairwise judgement records over ~180 distinct district-prompts.
- **Data quality:** pairwise labels are noisy, non-deterministic, and the degree of noise varies by pair (some pairs are near-ties with genuine pluralism, others are cleaner).
- **Deployment drift:** deployment districts will not match training districts in demographics or priorities, and priorities shift over time (e.g., climate resilience).

## What decisions are in their control

The fine-tuning recipe for a 3–8B open-weights LLM: the loss function, how soft/noisy pairwise preferences are incorporated, how robustness to label noise and distribution shift is handled, and any calibration / conservatism mechanism for pairs where the panel was split. They do NOT pick candidate bundles (delegates still do that) and they do NOT vote (residents still do that). What they pick is the training recipe that turns their pairwise dataset into a reliable bundle-scoring function.

## Data available

- ~9,000 pairwise preference records across ~180 district-prompt combinations.
- Each record: (district context, framing prompt, bundle A text, bundle B text, outcome in {A, B, too-close}).
- Panellists: 60–90 residents per district, stratified by age, income, tenure, sub-area.
- Supplementary: a smaller set of trained civic-design reviewer judgements on the same pairs (cleaner but systematically biased vs. residents).
- Meta-signals: per-record indicators of annotator inconsistency (same panellist flipping on retest), inter-annotator agreement rate per pair (e.g., 60/40 vs. 95/5), and context flags (mobile vs. desktop, time of day / fatigue).

## Scale

- Training set: ~9,000 pairs.
- District-prompts: ~180.
- Target deployment: three new partner cities within six months, then broader roll-out.
- Per deployment run: tens of bundles to score per district panel per cycle.
- Model: 3–8B parameters; single-GPU inference.

## End state

A fine-tuned on-premises LLM whose bundle rankings, in three new unseen partner cities, are judged by delegates in their first panel meeting as reflective of their neighbourhood; volunteer hours per PB cycle down ~1/3; no drop in final neighbourhood vote turnout or approval margin; and an explanation story for city councils about how the system handles non-unanimous training signal.

## Notes / uncertainties

- The coalition is explicit that they do NOT want a generic robust-to-all-training-noise approach (which produces timid assistants). They want surgical robustness aimed specifically at (a) noisy pairwise preference labels, where uncertainty should translate into deserved cautiousness on ambiguous pairs and (b) graceful degradation under deployment distribution shift.
- Prior prototype failure mode: picked up superficial training artefacts (e.g., always prefer "youth"-tagged bundles) and generalised poorly.
- Label noise is heteroscedastic: they have per-pair evidence about how split the panel was, not just a single label.
- Two distinct label sources (residents vs. civic-design reviewers) with different noise/bias profiles — potential for using expert labels as a secondary signal without letting them dominate.
- Both "end state" and "activities" are defined, so the problem is clearly Technical. The open questions are all about HOW to train, not WHETHER to train.
