# Problem Profile

**Session:** 0006
**Classification:** Technical
**Technical sub-type:** Resource misallocation (with explicit multi-stakeholder trade-off structure over a sequential horizon)

## What they are trying to improve
Tri-Valley Workforce Partnership wants to choose a five-year (20-quarter) placement strategy for their vocational training and apprenticeship programme. Each quarter they route 400–600 incoming slots across four participant groups (school-leavers; mid-career displaced workers; returners; justice-affected adults) and four sub-programmes (green energy, advanced manufacturing, allied health, logistics). "Better" is measured at the group level: successful sustained placements per group per quarter over the 20-quarter horizon.

They explicitly do **not** want a single "best" strategy. They want a **small curated menu (roughly 3–10)** of candidate five-year strategies, where each strategy is the best possible strategy *conditional on a specific ethical stance* about how the four groups' outcomes should be weighed against one another. The three stances the board surfaces are: (a) maximise total placements across all groups, (b) protect the worst-off group (currently justice-affected adults), (c) balance all four groups roughly proportionally. The menu must cover the spectrum between these stances meaningfully, so that whichever stance the board ends up endorsing, one of the offered strategies is close-to-best under it.

## What limits what they can do
- **Slot capacity per quarter**: 400–600 slots, set by employer commitments and funding.
- **Staff-hour budget per quarter**: caseworker time per head varies by group (justice-affected placements cost more per head).
- **Carry-over pipeline dynamics**: a person starting a two-year apprenticeship this quarter is still in it next year, so quarterly choices constrain next quarter's available slots and backlogs.
- **Employer relationship dynamics**: employers who get unreliable first placements stop calling back, so current allocation choices change future slot availability.
- **Per-group backlogs**: each group has a waiting list that grows or shrinks based on prior decisions.
- **Programme mix within each group**: slots must be routed across green energy / advanced manufacturing / allied health / logistics.
- **Horizon**: 20 quarters (5 years), then re-plan.
- **Data team capacity**: 3 internal data-team staff (Python, some simulation experience), modest external consultancy, eight-month engagement window, open-source tooling preferred.

## What decisions are in their control
Each quarter, for each of the four participant groups and each of the four sub-programmes, the agency decides how many of the quarter's slots to allocate. The decisions are not one-shot: the agency is choosing a **policy** — a decision rule that, given the current state of backlogs, pipelines, and employer relationships, produces a quarterly allocation. The policy must be executable over 20 quarters with evolving state.

## Data available
- Nine years of quarterly operational records: slot allocations by group × sub-programme, 6- and 12-month follow-up outcomes, retention, employer feedback.
- Participant-level intake data for ~14,000 past participants.
- Employer-side data: which employers took placements from each group historically; retention and satisfaction by group.
- **A commissioned simulator** that takes a quarterly decision rule and simulates 20 quarters of group-level outcomes. The board trusts it for scenario comparison. This is a key asset: the problem can be treated as policy search against a trusted simulator.

## Scale
- **Decision dimension per quarter:** 4 participant groups × 4 sub-programmes = 16 allocation variables per quarter (with group/sub-programme totals constrained by capacity and caseworker budget).
- **Time horizon:** 20 quarters.
- **Raw flat policy space:** 16 × 20 = 320 allocation variables if policies were open-loop; in practice the agency wants **state-dependent decision rules**, so the search is over a space of policies, not a flat vector.
- **Objective evaluation:** each candidate policy is evaluated by running the simulator over 20 quarters and reading off four group-level outcome trajectories.
- **Menu size deliverable:** 3–10 curated candidate strategies.

## End state
A working methodology and tool that, for each strategy cycle, produces a small curated menu of candidate five-year placement strategies, each tied to a specific point on the fairness–totals spectrum, plus a chart or table showing, for each strategy, the four group-level outcome trajectories over 20 quarters. The board then picks. The menu must (i) each member be near-best under some explicit stance on how to balance the four groups' outcomes, and (ii) collectively span the space of defensible stances meaningfully rather than redundantly.

## Notes / uncertainties
- The simulator is "imperfect but trusted." Uncertainty is therefore present but has been encapsulated in the simulator — the agent does not need to solve the uncertainty, it needs to plan against the simulator as an oracle.
- The organisation explicitly rejects dumping a large Pareto frontier on the board — they want a *curated* menu where each option is clearly tied to an interpretable stance. This is a strong design constraint: the output is not just "all non-dominated policies" but a small set of policies each matched to a named ethical stance.
- The three named stances (utilitarian totals, Rawlsian worst-off, proportional/egalitarian across groups) are a hint that the fairness axis is structured, not arbitrary.
- Decisions have multi-quarter consequences — the problem is non-memoryless; state (backlogs, active apprentices, employer-relationship state) persists and evolves.
- The board re-chairs and government changes drive re-runs with different stance weightings, so the methodology must be re-runnable, not a one-off.
