# Problem Profile

**Session:** 0002
**Classification:** Technical
**Technical sub-type:** Resource scarcity (primary) + Information flow (secondary — which families are quietly drifting)

## What they are trying to improve

A refugee resettlement non-profit (Riverbank Resettlement Network) wants to decide, each week across a 52-week year, which 40 of their ~800 first-year families their caseworkers should do home visits with, so that by year-end more families have spent more weeks in a "stable" state and fewer have spent weeks in "crisis" (with crisis weeks weighted more heavily because of lasting damage). They have an objective scoring rule: for any two candidate weekly schedules, they can tally the aggregate stable-weeks and weighted crisis-weeks over the cohort and say which one did better.

## What limits what they can do

- Hard weekly capacity: 40 caseworkers × 1 meaningful home visit per caseworker per week = 40 visits per week.
- Soft constraints: caseworkers are loosely assigned to sub-regions of the metro area (cross-city visits eat half a day), occasional language-matching needs, and continuity of relationship (a trauma-sensitive family has often built trust with one caseworker).
- Technical capacity on their side: two analysts with SQL and Python. No specialist optimisation background. Modest tooling budget; ideally open-source.

## What decisions are in their control

For each of the 800 currently-active families, for each of the 52 weeks of the first-year programme: visit this week or not. Total decision is which 40 families to visit each week (or more precisely, which 40 family-weeks to cover, respecting the soft geography/language constraints). Decisions made weekly; outcomes realised over the year.

## Data available

- **Historical cohort data**: ~2,400 families who have completed the first-year programme over the last three years. Each has an intake assessment, weekly caseworker notes, quarterly formal reviews, and a reconstructable week-by-week stable / at-risk / crisis trajectory plus their visit history.
- **Per-family features at intake**: country of origin, family composition, languages, employment and education history, trauma screening score, co-arrival community, pre-existing medical conditions, neighbourhood of placement. Roughly 10–20 structured features per family.
- **Real-time notes** on currently-active families.
- **Important caveat raised by the director**: the historical visit record reflects caseworker judgement, not random assignment — so the historical data has selection bias baked in. The director flagged this unprompted as something "we've always wondered whether it muddies the picture".

## Scale

- N ≈ 800 active families at any given time.
- K = 40 visits per week (budget).
- T = 52 weeks per cohort-year.
- ~3 discrete observable status levels per family (stable / at-risk / crisis).
- ~10–20 intake features per family.
- Historical dataset: ~2,400 families × 52 weeks = ~125,000 family-week records.

## End state

Defined and measurable: **maximise total stable family-weeks minus weighted crisis family-weeks across the cohort over the 52-week horizon.** The director confirmed they can compare two schedules and objectively say which performed better on this metric.

## Notes / uncertainties

- The historical-data selection-bias concern is real and consequential: any method that relies on naively fitting a predictive model to "what happened under the past policy" will inherit that bias. This is a known pitfall the director senses but doesn't know how to address.
- Soft constraints (geography, language, continuity) may or may not be worth encoding formally — they matter operationally but the director treats them as "things that shape who can realistically visit whom" rather than hard rules.
- The director cares about both operational scheduling *and* getting insight on which intake signals predict trajectory — but the scheduling is described as the operational core; the predictive-insight question is framed as a "nice-to-have if the analysis also tells us this".

## Classification reasoning

**End state defined?** Yes — the director describes a concrete, measurable welfare metric (stable-weeks minus weighted crisis-weeks) and confirms two schedules can be objectively compared on it.

**Activities defined?** Yes — the action space is known and discrete: each week, pick which 40 of N families get a visit. No ambiguity about what "doing the work" means.

Both axes defined → **Technical** → proceed to `problem-specification`.

The sub-type tagging (Resource scarcity primary, Information flow secondary) reflects that this is fundamentally a capacity-constrained allocation (40 against 800) where the information problem — which families are drifting — is real but downstream of the scheduling decision. It is *not* an adaptive problem: stakeholders agree on the goal, and the steps are known.
