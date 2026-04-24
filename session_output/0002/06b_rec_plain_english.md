# Recommendation: Plain English Summary — Session 0002
## Smarter Weekly Visit Scheduling for Riverbank's Caseworkers

---

## The problem in plain terms

Every week your 40 caseworkers have 40 meaningful home visits to give across 800 families. You want to give those 40 visits to the 40 families whose year-end outcome will benefit most — not just the ones in crisis today, and not just the ones on a fixed rotation, but the ones where a visit this week will pay off most over the rest of the year.

This is a genuinely hard decision to make by hand every week across 800 families. It is also a decision where three years of your own historical records contain almost everything needed to make it systematically. The method we recommend turns those records into a decision rule that, each week, ranks every family by how much a visit would matter *for them right now, considering their whole trajectory forward* — and you visit the top 40.

The method has two important features that match your situation specifically:

1. **It values future stability, not just current crisis.** A family quietly drifting toward crisis can be worth visiting even if they're technically still "at risk" today — because your data will show that families in their position, if not visited, often slip into crisis within weeks.
2. **It corrects for your caseworkers' past judgement calls.** Your historical records don't show what would have happened under a random schedule — they show what happened under caseworker intuition. That creates a subtle bias in naive analyses. The recommended approach explicitly corrects for it.

---

## How the method works, step by step

1. **We turn your three years of case records into a training dataset.** For each past family, for each week, we record: what state they were in (stable / at-risk / crisis), whether they were visited, and what state they moved to the following week. From 2,400 past families this gives us roughly 125,000 such weekly records.
2. **We learn a model that predicts how a family's state changes week-to-week**, given who they are (intake features) and whether they were visited. Crucially, we train this model not to be maximally accurate in general, but to be accurate *in ways that make the resulting visit schedule work well*. That's a technical choice that matters: the errors that matter most are the ones that would change who gets visited.
3. **We correct for the caseworker-judgement bias** by first modelling what drove caseworkers' past visit choices, then using that model to re-weight the training data so the final model reflects what *would* have happened under different schedules — not just what did happen under the one that was actually used.
4. **Each week, the system ranks all 800 active families** by a priority score that factors in both their current state and how visits are expected to shift their trajectory. Your caseworkers visit the top 40.
5. **The ranking is recomputed every week.** As families change state and new families arrive, the priorities update. It is not a one-off schedule — it is a live decision rule.

---

## What you need to run it

| Input | Do you have it? |
|---|---|
| Three years of caseworker notes + quarterly reviews | Yes |
| Weekly visit logs for those three years | Yes |
| Per-family intake features (10–20 structured fields) | Yes |
| Agreed state-labelling rules (stable / at-risk / crisis definitions) | Mostly — worth formalising |
| A number for how much more a crisis-week costs than a stable-week | To decide with the director and senior caseworkers |
| One data scientist (Python, PyTorch), one analyst (SQL, pandas) | Yes — your existing team |
| Specialist optimisation expertise | Not required — this uses publicly-available code |
| Commercial software / licences | None required |

---

## What the system will produce

- A **weekly priority list** of 800 families, with the top 40 marked for visits.
- A **second-stage assignment** that matches the 40 chosen families to available caseworkers, respecting region, language, and continuity considerations.
- A **monthly comparison** between the system's recommended schedule and what caseworkers would have picked without it, showing where they differ and which approach predicted better outcomes.
- An **interpretability layer**: for each recommended visit, a short explanation — "this family is flagged because [history of language-isolation], [recent quarterly review noted financial stress], and [time since last visit is 5 weeks and increasing]".
- A **model-update cadence** — once per year after each cohort completes, the model is retrained on the latest data.

---

## How confident can you be in the result?

Medium-to-high, for three reasons:

1. **The problem type is well-studied.** Sequential prioritisation of a limited resource across many entities with evolving hidden states is one of the most-studied structures in applied research. There is a mature body of deployed social-sector work — notably a large maternal-health programme in India reaching hundreds of thousands of beneficiaries — using methods in the same family.
2. **You can validate it on your own data before anyone changes their workflow.** A 13-week shadow deployment (system runs silently, caseworkers keep doing what they do, we compare) gives you empirical confidence before committing. If the shadow comparison doesn't show a meaningful improvement, you have lost nothing and learned that your caseworkers' current judgement is roughly right.
3. **You retain override authority.** The system outputs a ranked priority list with reasons, not a mandatory roster. Caseworkers can and should override when they know something the data doesn't.

Caveats worth naming:
- **Refugee resettlement is not a domain where this method has been deployed specifically.** The underlying mathematics is domain-neutral, but expect the first cycle to surface data-quality issues (e.g., inconsistent state labelling in historical notes) that need cleaning up.
- **Your historical caseworker-judgement bias is a real concern.** The correction we recommend handles it under standard assumptions, but if those assumptions are violated (i.e., if caseworkers were responding to something about families that isn't captured in the intake features), some residual bias will remain. The shadow deployment and ablation tests will surface this if it matters.

---

## Suggested next steps

1. **This week:** A 30-minute conversation with the director and two senior caseworkers to agree on (a) the exact definitions of stable / at-risk / crisis and (b) a rough number for how much more a crisis-week costs than a stable-week (e.g., 3×? 5×? 10×?).
2. **Month 1:** Your analyst reconstructs the per-family weekly trajectory dataset from existing caseworker notes. This is the main lift of the first month — roughly 3–4 weeks of ETL work.
3. **Month 2:** Your data scientist implements the recommended method (starting from the publicly-available code from the Wang et al. 2023 paper) and trains it on the historical cohort.
4. **Month 3:** Off-policy validation — test the learned policy against historical data using statistical methods designed to handle the selection bias issue. If results look good, begin shadow deployment.
5. **Months 4–6:** Shadow deployment on the current 800-family cohort. System runs silently; caseworkers continue as normal; agreement and outcome comparisons are tracked.
6. **Month 7:** Review with the director. Decide whether to promote to advisory mode (caseworkers see the system's recommendations), A/B deployment, or back-to-drawing-board.

Total timeline to a go/no-go decision based on real shadow-deployment evidence: **approximately six months**.

---

## One thing to watch out for

**The crisis-weight parameter — the number that says how much more a crisis-week costs than a stable-week — is a values choice disguised as a technical parameter.** Different numbers produce materially different visit schedules. A higher number pulls caseworker visits toward already-in-crisis families (reactive); a lower number spreads visits more evenly toward early-warning prevention (preventive). Neither is "right" — it depends on what Riverbank's mission prioritises. This parameter should be chosen deliberately, documented, and revisited annually with the director and board. The method will not tell you the right answer; it will tell you the consequences of each answer.
