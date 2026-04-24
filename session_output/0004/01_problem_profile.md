# Problem Profile

**Session:** 0004
**Classification:** Technical
**Technical sub-type:** Resource scarcity (primary) — with strong Resource-misallocation and Unknown/uncertainty features

## What they are trying to improve

Rio Valle Community College Network wants to decide, each Monday of a 12-week semester, which ~210 students (out of ~2,100 flagged "at some risk" across four campuses) receive a proactive check-in call from a success coach. The programme already works — students who receive a well-timed call stay enrolled at meaningfully higher rates — so the question is *who* to call each week, not whether to call. Success is two-fold: (1) maximise students kept enrolled through the semester, and (2) produce a weekly call list that is a **defensible, transparent translation** of a leadership-written plain-English "priority paragraph" (which names groups that should be prioritised or protected from deprioritisation), with the ability to see, per candidate call list, how well each clause of the paragraph is honoured and to detect unintended side-effects before deployment.

## What limits what they can do

- **Hard weekly capacity**: ~210 calls/week across the network (roughly one-tenth of the flagged pool).
- **Per-campus capacity**: each of the four campuses has its own coaching team with its own share of the total capacity.
- **Time horizon**: 12 weekly decision epochs per semester.
- **Policy/equity constraints written in plain English**: a priority paragraph, rewritten each semester, that names groups to prioritise and groups whose outreach must not decline. Multiple clauses can conflict (e.g. "prioritise first-gen" vs "don't reduce adult-learner outreach"). Must be auditable to funders, an equity committee, and the board.
- **Data quality limit**: engagement is not directly observed; only a noisy 0/1 proxy (LMS activity + assignment submission) plus advisor-contact recency. Historical data is biased — past calls were not randomly assigned.
- **Explainability**: "the algorithm said so" is not acceptable to the equity committee.

## What decisions are in their control

Each week, for each campus: select which of the currently-flagged students to call, subject to the per-campus capacity and the total network capacity of ~210. Secondary operational decisions (which coach calls which student, whether to send a text nudge) are out of scope for this engagement.

## Data available

- Three years of weekly records on ~12,000 former students:
  - Weekly 0/1 engagement proxy (LMS activity + assignment submission).
  - Log of every coaching call placed (biased — coach judgement, not random assignment).
- 8–12 demographic/intake features per student: age band, income band (FAFSA), first-generation status, home campus, programme of study, dependants, prior-term GPA band, distance-from-campus band.
- Current-semester weekly engagement proxy for the ~18,000 active students.

## Scale

- 4 campuses.
- ~18,000 active students per semester; ~2,100 flagged "at risk" at any time; 500–700 per campus flagged weekly.
- ~210 calls per week capacity.
- 12-week decision horizon per semester.
- Roughly 8–12 features per student.
- Paragraph rewritten ~every semester (≈ every 4 months), occasional mid-semester tweaks.

## End state

A weekly call-list generator that:
1. Takes as input the current weekly data on flagged students and the semester's plain-English priority paragraph.
2. Produces a defensible call list of ~210 students, respecting per-campus capacities.
3. Exposes, per candidate list, a *per-clause* score showing how well each clause of the paragraph is honoured, and highlights any group that would be quietly deprioritised (unintended side-effects) before deployment.
4. Lets leadership choose how to trade off clauses — balance evenly, protect the worst-served group, or maximise aggregate impact — and see the resulting call list change.
5. Over the 12 weeks, maximises retention while honouring equity constraints and remaining auditable.

## Notes / uncertainties

- **Engagement state is latent**: only a noisy proxy is observed; the true engagement dynamics over weeks are hidden. The weekly state evolves, and a call can change future engagement trajectories.
- **Dynamics matter**: students move in and out of "at risk"; calling one now affects whether they need a call next week; leaving one alone may let them slip further. So the problem is inherently sequential / dynamic, not a one-shot ranking.
- **Historical data is biased**: off-policy — past call decisions reflect coach judgement, not random assignment. Any learned model of call-effect must account for this.
- **Priority paragraph is natural language**: translating it into quantitative weights/constraints is itself part of the problem. Multi-criteria (Pareto / fairness) framings will be needed: balance across clauses, max-min on the worst-served group, or weighted sum — selectable by leadership.
- **Side-effect detection**: need the ability to compute, for any candidate decision rule, coverage statistics across demographic slices *not named* in the paragraph (e.g. "students without dependants") to flag unintended drops.
- **Coach assignment within campus** is treated as a downstream scheduling detail, not part of this optimisation.
