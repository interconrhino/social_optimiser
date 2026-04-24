# Choosing a Multi-Year Placement Policy for a Regional Workforce & Apprenticeship Programme

*Submitted by the Head of Strategy, Tri-Valley Workforce Partnership — April 2026*

## Who we are

Tri-Valley Workforce Partnership is a regional agency that runs a publicly-funded vocational training and apprenticeship programme across a cluster of mid-sized towns and their rural hinterland. We place people into paid apprenticeships, short-course certifications, and employer-sponsored on-the-job training in trades like renewable-energy installation, advanced manufacturing, allied health support, and logistics. We've been running some version of this for eleven years.

Our participants are not a homogeneous crowd. Broadly, they fall into four groups that our board, our funders, and our local politicians all care about:

- **School-leavers** (16–19), often without a clear post-school plan, from households with limited family experience of higher education
- **Mid-career displaced workers** who were in industries that have contracted — people in their 30s, 40s, 50s who need to retrain into growth sectors
- **Returners** — mostly women coming back to paid work after years of caregiving, plus some returning from long-term illness
- **Justice-affected adults** — people coming out of custody or off community sentences who have a right to training support and a much harder time getting an employer to take a chance on them

Our board keeps asking us a version of the same question, and we genuinely don't know how to answer it cleanly.

## The problem we're trying to solve

Each **quarter** (so four times a year) we make placement decisions: which of the incoming training slots, employer-sponsored apprenticeship openings, and certification cohorts go to which kind of participant. A quarter's decisions set the mix for that period — how many school-leavers we push into green-energy apprenticeships vs how many displaced workers we retrain in advanced manufacturing vs how many returners we route through flexible-hours allied-health courses. These decisions are not one-off: what we do this quarter changes the pipeline of candidates available next quarter (a person who starts a two-year apprenticeship this quarter is still in it next year), changes which employers keep offering us slots (an employer who gets unreliable first placements stops calling us back), and changes which groups have a backlog of waiting candidates.

So over our planning horizon — roughly a **five-year strategic cycle, 20 quarters** — we are effectively committing to a *placement strategy*, not just a one-time sort. And different strategies genuinely lead to different outcomes for the four groups.

We've run scenarios, and here's the crux. We can push the total number of people we place into sustained employment very high — but the strategy that does that tends to lean heavily on school-leavers and returners, because they're the cheapest to place successfully. That same strategy leaves justice-affected adults with very thin support, because each placement in that group takes more caseworker time per head and has a lower success rate. On the other hand, if we prioritise the group with the worst employment outcomes — currently justice-affected adults — we have to take slots away from school-leavers and mid-career displaced workers, and our total placements drop noticeably, which our funders definitely notice.

There is no single "right answer" here. Our board has three factions:

- One wants the strategy that **maximises total placements** across all four groups — "help as many people as possible, full stop"
- One wants the strategy that **protects the worst-off group** — "it's morally unacceptable for justice-affected adults to be left behind even if we help more people overall"
- One wants a **balanced** strategy that treats the four groups roughly proportionally — "we shouldn't maximise one metric at the expense of any group being badly served"

All three are defensible. All three lead to materially different placement strategies. And the implicit weighting between these three stances changes when we get a new board chair or a new state government.

## What we actually want from an analysis

We don't want an analyst to tell us which of those three philosophies is correct — that's a political and ethical question and it's not theirs to settle. What we want is a **small menu of candidate five-year placement strategies**, each one being the best possible strategy *if* a particular balance between "help the worst-off group", "balance across groups", and "maximise totals" is the one the board chooses. Something like three to ten strategies, each clearly tied to a point on that spectrum, so our board can see concretely: "strategy A gives you these outcomes for each group, strategy B gives you these, strategy C gives you these — now pick."

Crucially, we don't want to show them a thousand Pareto-optimal options and ask them to pick. We want a *small, curated* menu that meaningfully covers the spectrum of reasonable ethical stances, so that whichever stance the board ends up endorsing, one of the strategies we hand them is close to the best achievable under that stance.

## What decisions and dynamics are in play

- **Decisions each quarter**: how to allocate incoming apprenticeship and training slots (typically 400–600 slots per quarter across all programmes) across the four participant groups, and within each group, which sub-programmes (green energy, manufacturing, health, logistics) to route them into
- **Who the beneficiaries are**: the four groups above; our planning unit is the group, not the individual (individuals come and go, groups persist across years)
- **How outcomes evolve**: for each group, the relevant outcome each quarter is something like "successful sustained placements achieved this quarter," and it depends on the current backlog of candidates, prior investment in employer relationships for that group, and what we chose to do last quarter. It's not memoryless; decisions have multi-quarter consequences
- **Horizon**: a 20-quarter (five-year) strategic plan, refreshed each strategy cycle
- **Capacity / budget**: total slot capacity per quarter is determined by employer commitments and funding; there's also a staff-hour budget, since justice-affected placements cost more caseworker time per head

## What data we have

- **Nine years of operational records** at the quarterly level: slot allocations by group and sub-programme, placement outcomes at 6-month and 12-month follow-up, retention, employer feedback
- **Participant-level intake data** for the past ~14,000 participants across the four groups
- **Employer-side data**: which employers have taken placements from each group historically, retention and satisfaction by group
- **A reasonably good simulator** that we commissioned two years ago — it takes a placement strategy (a decision rule for each quarter, given the current state of backlogs and pipelines) and simulates 20 quarters of outcomes group-by-group. It's imperfect but the board trusts it for scenario comparison

## What "done" looks like

A written methodology and a working tool that produces, for our next strategy cycle, a small set of candidate five-year placement strategies — each one the best strategy for a specific stance on how to balance the four groups' outcomes — along with a clear chart or table showing what each strategy delivers for each group. Our board then chooses. If the board's stance shifts, we re-run and produce a new small set for the new cycle.

We have an internal data team of three (Python, some simulation experience), a modest external consultancy budget, and we can devote staff time across an eight-month engagement. Open-source tooling strongly preferred.
