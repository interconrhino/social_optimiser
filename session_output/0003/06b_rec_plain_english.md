# Optimisation Recommendation — Plain-Language Summary (for the Programmes Director and leadership)

**Session:** 0003
**For:** Riverbank Resettlement Network
**Problem in one sentence:** Choose which 40 of your ~800 active families each caseworker should visit this week, so that the programme's overall outcomes over the whole year come out as strong as possible.

---

## 1. Problem in plain terms

You have 800 families in the first-year programme at any time and 40 caseworkers who can each do about one meaningful home visit a week. That is 40 visits chasing 800 families, and your current mix of a fixed rotation plus squeaky-wheel triage is missing families that are quietly slipping before they reach crisis. You want a **defensible, repeatable weekly scheduling rule** that answers, every Monday morning, the question *"who are the 40 families a caseworker should visit this week?"* — such that the answer reflects both how badly each family needs a visit right now and how much that visit will pay off across the rest of the year.

We are recommending an approach that is already running, at scale, in a very similar setting: maternal-and-child-health programmes in India (the ARMMAN / SAHELI system) use exactly this method to decide which of tens of thousands of mothers to call each week, and it has been shown in a randomised field trial to reduce drop-off meaningfully compared to a round-robin baseline.

---

## 2. How the method works — step by step

Imagine a simple version of the problem first. Pretend you had only one family. You'd watch them each week, and a *priority score* would tell you "how much do we gain by visiting them this week, given where they are right now and what's likely to happen next?" A family that is stable and coping well gets a low score. A family that is at-risk and trending worse gets a high score. A family deep in crisis where a visit can't realistically undo the damage this week might — perhaps surprisingly — get a mid-range score, because the marginal value of one more visit is lower than for the family you can catch *before* crisis.

The mathematical trick is: **even when you have 800 families competing for 40 slots, you can compute that same priority score for each family independently**, and then simply visit the 40 with the highest scores. That's the whole decision rule. The index (called a *Whittle index* in the literature) captures, for each family in each state, the full long-horizon value of a visit — not just how bad this week looks, but how much the visit shifts the trajectory over the coming weeks and months.

The priority score for each family depends on:
- **Their current situation** (stable, at-risk, or in crisis).
- **Their intake features** (family composition, languages, trauma-screening, neighbourhood, etc.) — these shape how fragile a family is without support, and how much a visit helps them.
- **Your learned understanding of how families typically move between stable, at-risk, and crisis**, with and without a caseworker visit — estimated from the three years of historical data you already have.

The scores are computed once (and periodically refreshed), and running the weekly schedule takes milliseconds on a laptop.

**Every week, the pipeline is:**
1. Read each active family's most recent situation (from caseworker notes).
2. Look up their priority score.
3. **Force-visit anyone who has gone too long without a visit** (a coverage-floor safety rule — we suggest "no family unvisited for more than 8 weeks").
4. Fill the remaining slots up to 40 by taking the families with the highest priority scores.
5. Hand the list to supervisors with the scores shown, so they can review and override individual cases.

---

## 3. Data checklist — what we need from you

You already have nearly everything.

| What we need | Do you have it? |
|---|---|
| Weekly stable / at-risk / crisis history for past families | **Yes** — reconstructable from three years of weekly visit logs, notes, and quarterly reviews |
| Intake features for every family (country, family composition, language, employment, trauma score, neighbourhood, medical history, etc.) | **Yes** — in your intake database |
| Records of which families were visited in which weeks historically | **Yes** — in your weekly visit logs |
| A current-state feed (most recent situation for each active family, refreshed weekly) | **Partially** — this is in caseworker notes; will need a light ETL step to turn free-text notes into {stable, at-risk, crisis} labels consistently. Your two analysts can do this |
| A value for the crisis weight *w* (how much worse is a week in crisis compared to a week stable?) | **Needs a programme decision** — we recommend starting at 3 and doing a sensitivity check at 1, 2, and 5 |
| A value for the max-gap rule (longest a family should ever go without a visit) | **Needs a programme decision** — we recommend 8 weeks |

The one thing worth flagging is that your historical data is **not randomised** — past visits reflected caseworker judgement. This means a naive "learn what visits do from the data" would overstate visit impact for the families caseworkers already prioritised and understate it elsewhere. The standard fix (inverse-propensity weighting or doubly-robust estimation) is well-known and adds maybe a week of analyst work; your team can handle it. A small partial-randomisation element in the pilot (a few borderline cases visited on the toss of a coin) would make the signal much cleaner but is optional.

---

## 4. What it will produce

- A **weekly priority list** of the 40 families a caseworker should visit this week, ranked with a transparent score per family, with the data signals behind each score shown so supervisors can audit.
- A **force-visit list** of any family hitting the max-gap floor, so nobody is silently forgotten.
- A **yearly evaluation** showing expected improvement in total stable-weeks and reduction in crisis-weeks compared to your current practice.
- **Which intake signals most strongly predict bad trajectories** — your secondary ask. The transition model that drives the policy directly tells you this; you get it as a byproduct. This lets you flag high-risk newly-arriving families for closer early attention, without waiting for the first problem to surface.
- A **reproducible open-source codebase** (Python, numpy, scikit-learn) that your in-house analysts can maintain and extend.

---

## 5. Confidence and validation

Before anything goes live, we recommend:

1. **Shadow mode for two months.** The system makes weekly recommendations; caseworkers continue with your current process. We compare what the model would have prioritised against what actually happened, and surface any weird edge cases.
2. **A split rollout for one month.** Random half of the metro uses the model's recommendations (with override); the other half continues current practice. This gives you an honest apples-to-apples comparison.
3. **Sensitivity checks.** Does the ranking move wildly if we change the crisis weight from 3 to 2? Does it change if we drop a less-confident feature? If the ranking is robust to reasonable perturbations, that's a sign the method is genuinely finding signal; if it swings around wildly, we diagnose before deploying.

Evidence this approach works: the most directly comparable deployment is ARMMAN's maternal-health programme in India, which uses this same method at much larger scale (tens of thousands of beneficiaries), and was shown in a peer-reviewed randomised field trial (AAAI 2023) to cut engagement drop-off significantly versus round-robin baselines. The research community has spent the last decade refining this specific tool for social-sector problems, and it is open-source throughout.

---

## 6. Next steps

**Month 1:** Data engineering — turn three years of weekly logs and notes into a clean trajectory table; your two analysts lead this with light guidance from an external optimisation partner.

**Month 2:** Fit the transition model (with the confounding adjustment) and verify the priority-score machinery works on your data. Decide crisis-weight *w* and max-gap *K_max*.

**Month 3:** Validate on historical data — does the model's would-have-done-differently compare favourably to your actual history? Iterate.

**Month 4–5:** Shadow mode. Model runs weekly; supervisors see recommendations; no live change to operations.

**Month 5–6:** Split rollout as described above. Evaluate.

**Beyond month 6:** If the pilot succeeds, extend to the full programme. A research-grade upgrade called "decision-focused learning" (the exact technique ARMMAN uses in production) can be layered on in year 2 for additional gains, if you bring on a technical partner with machine-learning expertise.

**Budget and people:** Everything we've described runs on open-source Python on a laptop. Your two analysts are enough in-house; a part-time external optimisation advisor (a few days a month) is strongly recommended for the modelling phase. No Gurobi licence or GPU needed.

---

## 7. Caveats — what to watch out for

- **Do not treat the ranking as absolute.** The model is a decision aid, not a replacement for caseworker judgement. Supervisors override freely; the system logs overrides so you can learn from them.
- **Historical-data confounding** is the highest-risk technical element. If we skip the propensity-adjustment step, the model will overconfidently recommend visits to the kinds of families your current caseworkers were already visiting — and the improvement over baseline will be overstated. This is fixable but it needs the step to be done, not skipped.
- **A few families will look low-priority for long stretches** because their trajectory is genuinely stable. The max-gap coverage floor exists specifically to ensure this never becomes "we forgot about them" — but programme leadership should decide the floor value based on duty of care, not just efficiency.
- **New arrivals** who lack any observed trajectory start with only their intake features. The model will generalise from past families with similar features, but the first few weeks of any new family are the most uncertain. Your current practice of prioritising new arrivals for early check-ins is wise and should continue as a programme rule on top of the model.
- **Policy drift.** If a neighbourhood-wide shock happens (a large employer layoff, a housing-market change), the transition model will not instantly catch up. Re-fit monthly, watch for spikes in crisis rates, and keep a human in the loop.

---

**Bottom line:** Your problem has a clean mathematical structure that matches a very well-studied tool — the same tool public-health NGOs are already using at larger scale to solve the essentially identical problem of "who gets the limited caseworker attention this week?" The method produces a transparent priority score per family, runs in milliseconds, needs only data you already have, and can be built and piloted by your existing analyst team in six months. It should materially reduce the rate at which families slip from at-risk into crisis before you notice.
