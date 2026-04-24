# Recommendation — Plain-Language Summary

**Session:** 0005
**For:** Director of Civic Technology, Northside Participatory Budgeting Coalition

---

## 1. Problem in plain terms

You're building a software assistant that pre-ranks project bundles for volunteer delegate panels, so that instead of hand-building every bundle from scratch the delegates refine a short list the assistant has already proposed. To rank bundles the way residents in a specific neighbourhood would rank them, you want to fine-tune a medium-sized open-weights language model on the roughly nine thousand pairwise comparisons you've collected from resident panels across fourteen cities.

The hard part isn't the fine-tuning itself. It's that your training signal is noisy in specific, known ways: residents disagree with each other, they disagree with themselves on retest, and — crucially — the neighbourhoods you'll *deploy* in aren't going to look exactly like the neighbourhoods you *trained* on. You've tried "be cautious about everything" approaches and found they produce an assistant that's timid across the board and not useful. What you want is the opposite: cautious exactly where the training signal was ambiguous, confident where it was clear, and gracefully flexible when the new neighbourhood's priorities differ from the training ones. That's a very specific ask, and as it happens there is a very specific training recipe that matches it.

## 2. What the recommended method does, in plain language

The method is called **DPO-PRO** — "Preference Robustness for DPO." Here's the picture.

The standard recipe for teaching a language model from pairwise preferences (called DPO — Direct Preference Optimization) takes each pair of bundles, looks at which one the panel preferred, and nudges the model to agree. It treats every pair the same whether the panel was 95/5 or 60/40.

DPO-PRO adds one small but surgical modification. On each pair, instead of treating the panel's vote as gospel, it treats the true preference as *somewhere inside an uncertainty bubble* around what the panel actually reported. It then trains the model to do well *even in the worst case inside that bubble*. Crucially, the size of the bubble is set per pair: when the panel was unanimous (say 95/5), the bubble is tiny and the training behaves just like normal DPO. When the panel was split (say 55/45), the bubble is large, and the training explicitly rewards the model for *not* becoming too confident about which bundle is better.

That's it. No inner min-max solver, no heavy machinery — mathematically the whole thing collapses into normal DPO plus one extra regularisation term that anyone who has written a DPO training loop can add in about ten lines of code. It runs on the same A100 you're already using. It adds essentially no extra compute. And it gives you exactly the behaviour you asked for: "timid only where the training panel was split, confident where it wasn't."

The other important property is that the uncertainty bubble is placed *only around the preference labels* — not around every feature of the training distribution. That is the opposite of generic robust-to-everything approaches, and it's precisely why DPO-PRO won't make your assistant timid across the board.

A recent paper by the authors demonstrates this exact method on a public-health application (maternal-health programme calls with ARMMAN) and shows it outperforms both vanilla DPO and the more generic "robust against everything" variants — on the same single-A100 budget you have available.

## 3. Data checklist — what you need

You already have most of it:

- ✅ **Roughly 9,000 pairwise comparisons** across ~180 district-prompts. — You have this.
- ✅ **The raw panel votes per pair** (not just the majority label) so we can compute how split the panel was on each pair. — You have this, because you record all 60–90 panellists' responses.
- ✅ **A smaller set of civic-design reviewer labels** on the same pairs. — Useful, but we'll use it mostly for cross-checking and calibration rather than as training data.
- ✅ **District-level context and prompt data** (demographics, existing infrastructure, recent service requests, framing prompts). — You have this.
- ⚠️ **A district-level train / validation / test split.** — You need to design this deliberately: keep at least 2–3 entire cities out of training, so we can honestly measure how the assistant behaves on a city it has never seen before.
- ⚠️ **A base open-weights model checkpoint.** — Llama-3 8B Instruct or Mistral 7B v0.3 are both strong starting points; both run on a single A100 and quantise down for on-premises partner-city inference.

## 4. What it will produce

- A fine-tuned open-weights language model (3–8B parameters, single-GPU inference, quantisable to 4 or 8 bits for modest hardware) that scores a candidate bundle for a given district and prompt.
- For any new district: a pre-ranked short list of bundles, ordered from "residents of this district are most likely to prefer it" to least.
- A **calibration curve** — a picture you can put in front of a city council that shows, on held-out pairs, that when the model says "60/40" it is right about 60% of the time, and when it says "95/5" it is right about 95% of the time. That is your trust story.
- An ablation table showing that the method beats both (a) a vanilla DPO baseline and (b) a generic "robust-against-everything" baseline (Dr-DPO) on held-out cities.

## 5. Confidence and validation — how to know the result is trustworthy

Three layers of validation:

1. **Held-out-city test.** Reserve 2–3 whole cities from training and measure pairwise-accuracy and calibration there. This is the test that mirrors your actual deployment concern.
2. **Retrospective pilot.** Apply the trained assistant to a historical PB cycle in a held-out city and compare its short list against what the delegates ended up proposing and what residents actually voted for.
3. **Prospective pilot.** In one of the three new partner cities, deploy the assistant for the autumn 2026 cycle. Pre-register three success criteria before you start:
   - Delegates agree the short list reflects their neighbourhood on ≥ 70% of bundles at first-meeting.
   - Volunteer meeting hours per cycle drop by ≥ 30%.
   - Final neighbourhood vote turnout and approval margin do not drop vs. your historical norms for similar-sized cities.

Report the calibration curve and the ablation table alongside the pilot results. That is the package you can show to a city council.

## 6. Next steps — moving from recommendation to deployment

| Weeks | What |
|---|---|
| 1–2 | Compute per-pair soft scores from raw panel votes. Design the district-level train/val/test split (hold out 2–3 whole cities + 1 "pretend-deployment" city). Pick base model (Llama-3 8B recommended). |
| 3–6 | Implement DPO-PRO on top of HuggingFace TRL's `DPOTrainer`. The change is ~10 lines — add the closed-form regulariser term. Run vanilla DPO and Dr-DPO baselines in parallel. |
| 7–10 | Sweep the uncertainty-radius hyperparameter ρ (log grid, ~5 values, ~3 seeds each). Select on held-out-city accuracy and calibration. |
| 11–14 | Full ablations: reviewer-channel treatment, panel-size sensitivity, per-city leave-out. Write up the trust-story calibration curve. |
| 15–18 | Retrospective pilot against a historical held-out-city PB cycle. |
| 19–24 | Prospective pilot in one new partner city for the autumn cycle; then roll out to the other two. |

This fits comfortably inside your six-month runway for a two-person ML team with a handful of A100s.

## 7. Caveats — what to watch out for

- **Deployment-district drift isn't fully solved by any training recipe.** DPO-PRO's uncertainty bubble is calibrated from training-time panel disagreement, so it handles "the training panel itself was split" well, and it handles "residents' priorities are moderately different in the new city" reasonably. It doesn't automatically handle "residents in the new city have radically different priorities." Mitigation: in each new city, collect a small pilot batch of, say, 300–500 fresh pairwise judgements before the first PB cycle, and do a short per-city fine-tune on top of the base model. Budget for this in your partner-city onboarding.
- **The assistant should remain a pre-ranker, not a decision-maker.** Delegates still pick, residents still vote. Keep this framing in your city-council narrative — it's both true and legally safer.
- **Two label channels (residents + civic-design reviewers) aren't fused for you by DPO-PRO out of the box.** The clean starting point is: train on residents only; use reviewer labels for a held-out calibration check on pairs where reviewers and residents disagree most. That tells you whether residents are noisy or reviewers are systematically wrong — both useful signals.
- **Priorities genuinely shifting over time** (climate resilience, for example) is handled partially by the ambiguity set and more fully by a light annual retraining pass as new pairwise data comes in. Plan for this: a yearly "preference drift review" is a clean institutional habit.
- **ρ has to be tuned.** Don't ship with ρ = 0 (that's just vanilla DPO). Don't ship with ρ = 1 (that's over-cautious). The sweet spot for your data scale is likely ρ ∈ [0.05, 0.3]; the sweep will tell you.

---

If any of this lands differently than you expected, or if you want me to go deeper on the ρ-tuning protocol, on the district-split design, or on the calibration-curve story for city councils, I'm happy to.
