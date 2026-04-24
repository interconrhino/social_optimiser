# Problem Profile

**Session:** 0007
**Classification:** Technical
**Technical sub-type:** Resource scarcity (with strong elements of Unknown/uncertainty — engagement state is partially observed and evolves over time)

## What they are trying to improve
GreenFurrow Cooperative Trust wants to maximise the cumulative number of enrolled smallholder farmers who remain actively engaged with its monthly voice-advisory service over a 6-to-8 month pilot window. "Actively engaged" means the farmer actually listens to the monthly automated voice message (rather than picking up and hanging up, or not picking up at all). The organisation believes sustained engagement translates into better yields, less pesticide waste, and higher income stability — but for this decision, the target outcome is engagement itself.

## What limits what they can do
- **Call budget:** 12 farmer-support advisors can realistically place only ~400 personal follow-up calls per month, against a base of ~28,000 enrolled farmers.
- **Explainability:** The field director must be able to explain why any given farmer was (or was not) selected to an advisor or district auditor — no opaque black boxes.
- **Technical capacity:** Two in-house data analysts comfortable with Python and SQL, no in-house optimisation expertise.
- **Fairness / coverage:** Any replacement rule must not systematically under-serve specific villages or language groups.
- **Helpline overflow:** Farmers who call the helpline still get a follow-up call on top of the quota — so the 400 are the *proactive* calls only.

## What decisions are in their control
Each month, which specific subset of ~400 farmers (from the ~28,000 enrolled) should the advisors proactively call? The selection is repeated monthly for the pilot window.

## Data available
- Five years of monthly engagement logs per farmer: listened / did not listen, listen duration in seconds, whether an advisor follow-up call was placed that month. ~28,000 farmers × up to 60 months (many farmers enrolled partway through).
- Advisor call logs: timestamp, advisor ID, duration, structured note on whether the call reached the farmer and tone of the conversation.
- Farmer attributes: district, village, language, age band, farm size category, crop mix, education, phone type (smartphone vs basic), distance to nearest district office, membership in a local farmer collective.
- Seasonal context: monthly district-level rainfall and market prices.

Important data caveat the user flagged themselves: historical call assignment was driven by the current rotation rule plus ad-hoc helpline-triggered calls — i.e., it is not a randomised experiment. The user explicitly wants the approach to be honest about what can and cannot be learned from this observational history.

## Scale
- ~28,000 candidate farmers per month.
- Select 400 of them each month.
- 6–8 month pilot; the planning question repeats 6–8 times, with new engagement observations arriving each month.
- Three districts.

## End state
At the end of the pilot, the organisation can state with statistical backing: "Under the new monthly selection approach, cumulative farmer engagement over the pilot window was meaningfully higher than under the rotation, at the same 400-calls/month budget." A side-by-side pilot (part of the farmer base on the new rule, part on rotation) is already board-approved.

## Notes / uncertainties
- Each farmer's "true" engagement propensity drifts over time and is only partially observed (we see the monthly listening outcome, but not the underlying willingness / life-circumstance state).
- The causal effect of a personal call on next-month engagement is known qualitatively ("noticeably more likely to listen next month") but has not been quantified under a clean identification strategy — a pilot with a control arm is part of what is being asked for.
- Equity constraint is explicit: villages and language groups must not be systematically cut off.
- The current rotation rule gives every farmer the same long-run call rate regardless of engagement signal — this is the baseline to beat.
- The user wants a rule that is field-explainable, not just field-deployable.
