# 06b — Recommendation: Plain-Language Summary

**Session:** 0007
**For:** GreenFurrow Cooperative Trust — Director of Farmer Services and board

---

## 1. Your problem in plain terms

Every month you can have your advisors personally call about 400 farmers out of roughly 28,000 enrolled. You want those 400 calls to go to the farmers where a call will do the most good — the ones drifting away from the monthly voice advisory, who can plausibly be brought back. At the same time, you want the rule to be explainable to auditors, to be fair to every village and language group, and to be validated against your current rotation in a real pilot rather than only in a simulation.

**The method we recommend is this: every month, compute a simple per-farmer "call-now" score for all 28,000 farmers, then phone the 400 highest-scoring ones — with a guaranteed minimum call rate for every village and language group, and a cooldown so no one gets called two months in a row.** The score is learned from your own five years of listen history and tells you, for each farmer, how much future engagement we expect to gain if an advisor calls them this month instead of leaving them alone.

It is the same family of method that a maternal-health NGO in India (ARMMAN) uses to decide which pregnant mothers their advisors should call about their weekly voice advisory — which is essentially your problem in a different domain. They have evidence from a randomised trial that it meaningfully outperforms a rotation rule.

## 2. Step-by-step explanation — how the method works

1. **Learn from your history.** Using the five years of "did this farmer listen this month, yes/no" records — combined with farmer attributes (village, language, farm size, phone type, etc.) and which months they were previously called — we fit a small statistical model of how each farmer's engagement drifts over time, and how a personal call nudges it.

2. **Track each farmer's current "engagement mood".** Every month, the model updates a small summary of where each farmer sits — Highly engaged, Engaged, Drifting, Disengaged, or Lost — based on their recent listening pattern. This is not a label stuck on a farmer for life; it is a running signal that can change every month.

3. **Score every farmer for "would a call help this month?"** For every farmer, the model computes a number that says: *if we spend one of our 400 calls on this person now, how many extra farmer-months of engagement do we expect over the rest of the pilot?* This number is the call-priority score. A farmer who has been listening fine gets a low score (they don't need a call). A farmer who just stopped after eight months of steady listening gets a high score (they are at the moment where a call is most likely to pull them back).

4. **Guarantee fairness first.** Before picking the top 400, we check each subgroup (each village × language combination). Every subgroup is guaranteed a minimum share of calls — at least half of what they would get under fair proportional allocation. This stops the method from ever systematically cutting off a subgroup.

5. **Pick the top 400 remaining.** After the fairness floor is honoured, the rest of the 400 slots go to the farmers with the highest scores, excluding anyone called last month.

6. **Write the list with a reason.** Each farmer on the 400-list comes with a short plain-English reason an advisor or auditor can read: "Listened for 6 months, then stopped for 2 — our data says calls usually recover farmers in this situation about 40% of the time." This turns the score into something field-auditable.

7. **Next month, update and repeat.** The new listen observations from this month feed back in, moods update, new 400 are selected.

## 3. Data checklist — what you'll need

| You already have this? | Data item |
|---|---|
| **Yes** | Monthly listen records per farmer (five years, listen yes/no + duration) |
| **Yes** | Monthly call records per farmer (which advisor, when, duration, outcome note) |
| **Yes** | Farmer attributes (district, village, language, farm size, crops, phone type, distance to office, collective membership) |
| **Yes** | District-level monthly rainfall and market prices |
| **To be designed** | Agreed definition of "engagement state" — which listening patterns count as Highly engaged vs. Drifting vs. Lost. Your analysts will propose this from the data; you sign off on it. |
| **To be designed** | The fairness floor — what is the minimum share of calls every village × language subgroup is guaranteed? Starting suggestion: half of the fair proportional share. |
| **To be collected going forward** | Pilot randomisation records — who is in the treatment arm, who is in the rotation control arm — so that the end-of-pilot comparison is clean. |

## 4. What the method will produce

Each month, a **call list of 400 farmer names** for the advisors, with:
- Farmer ID, name, village, language, advisor owner, last call date;
- A priority score;
- A short English rationale for each selection ("drifting from engaged state — a call this month is historically high-leverage");
- A summary count showing how the 400 break down across districts, villages, and language groups, so the field director can eyeball equity at a glance.

Plus a **monthly dashboard** tracking:
- Engagement rate in the treatment arm vs. the rotation control arm, month over month;
- Per-subgroup engagement rates (to confirm fairness is holding);
- Calls-to-reactivation ratio (among farmers who were drifting and got a call, what fraction came back next month).

And at the **end of the pilot (month 6–8)**, a clean side-by-side comparison: *"Our new approach delivered X% more cumulative engagement than the rotation at the same call budget, with confidence interval [Y, Z], and with equity held within the agreed floor across all villages and language groups."*

## 5. Confidence and validation

**How to know the result is trustworthy:**

1. **It's being tested head-to-head with the current rotation on real farmers**, not just simulated. That is the point of the pilot design your board approved.
2. **The analytical method has been used in the wild** on a structurally identical problem (ARMMAN's maternal-health programme), with RCT-grade evidence of improvement over a rotation rule.
3. **The fairness floor is enforced every month**, monitored in the dashboard, and breaks are pre-committed to trigger a pause.
4. **Every selection has a plain-English reason**, so field audits can spot-check that the reasoning makes sense case-by-case.
5. **A sensitivity analysis is run before launch**: your analysts vary the key modelling choices (how many engagement states, where to set the fairness floor, what cooldown to use) and report which choices actually matter to the selection. This lets you lock in defensible defaults.

**Where the method can still go wrong — and how we catch it:**

- *If the listen signal is noisier than the model assumes* (e.g., a farmer's phone was broken for a month and looked "disengaged"), the score will mis-rank them. The cooldown and the post-call notes from advisors will surface these cases.
- *If the pilot period is too short to separate signal from seasonal noise*, the end-of-pilot lift estimate will have wide confidence bands. Pre-registering the primary metric and running both arms for the full 8 months mitigates this.
- *If a shock hits during the pilot* (drought, policy change), both arms feel it and the comparison is still valid — but the absolute engagement numbers become hard to read without domain caveats.

## 6. Next steps — the actual sequence

**Months 1–2 (build):**
- Analysts pull and clean the five-year listen + call history.
- Define and validate the engagement-state representation with the field director.
- Fit the per-farmer engagement model.

**Months 2–3 (verify):**
- Run the scoring pipeline on historical months (not for live decisions, just to check it gives sensible rankings).
- Finalise fairness floor, cooldown, and subgroup definitions with the field director.
- Design the pilot randomisation with a statistician (can be external, 2–3 weeks of consulting).

**Month 3 (pilot launch):**
- Board sign-off on the treatment/control split and equity commitments.
- Advisors briefed; first monthly 400-list issued; dashboard live.

**Months 3–11 (run and monitor):**
- One monthly 400-list per month for the treatment half.
- Rotation continues on the control half.
- Monthly equity check.

**Month 11 (analyse and decide):**
- End-of-pilot analysis.
- Report to board: lift, confidence interval, per-subgroup breakdown.
- Decision: roll out, iterate, or stop.

**In-house skills needed:**
- Both your analysts have the Python and SQL needed for the pipeline.
- One of them will need to skill up on the modelling — about two weeks of reading plus adapting a public reference implementation from the Harvard Teamcore RMAB codebase.
- No in-house optimisation expertise is required to run the method, once built. A statistician should be consulted (externally is fine) for the pilot-randomisation design and end-of-pilot analysis.

**Cost / time:** Roughly 3–4 months of part-time analyst work to build, then minutes per month to run during the pilot.

## 7. Caveats

- **The first version of the model will be imperfect.** Five years of data is plenty, but your historical calls were not random — so some of what the model will "learn" is partly the effect of the rotation rule itself. This is why the pilot's control arm is non-negotiable: it is the clean comparison that rescues the analysis from that imperfection.
- **The method cannot protect against farmers whose phone situation genuinely changes** (lost, shared, broken). Those will show up as engagement drops the model misinterprets as intent. Advisor notes will catch the worst of these; over time the model can incorporate phone-status signals.
- **"Engagement" is a proxy for the outcomes you actually care about** (yields, pesticide use, income). If at any point engagement and outcomes start decoupling — e.g., farmers listen but don't act — the optimisation target needs to be revisited.
- **Don't let the model lock you out of judgement.** The field director should retain an override for must-call exceptions (e.g., a farmer in an acute crisis who should be contacted regardless of score). That override should be logged and reviewed.
- **This replaces the rotation only for the proactive 400 calls.** Helpline-triggered calls continue as before, on top of the 400.

---

*Recommended technique: **Restless Multi-Armed Bandit with a Whittle-index policy**, fit via decision-focused learning, with a ProbFair equity floor — or, in plain language, a monthly per-farmer call-priority score with a guaranteed minimum call rate per subgroup, validated in a side-by-side pilot against the current rotation.*
