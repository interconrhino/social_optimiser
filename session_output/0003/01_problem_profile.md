# Problem Profile

**Session:** 0003
**Classification:** Technical
**Technical sub-type:** Scale (primary) — with strong elements of Unknown/uncertainty (stochastic family trajectories) and Resource scarcity (40 visits per week vs 800 families)

## What they are trying to improve

Riverbank Resettlement Network wants to decide, each week, which 40 of their ~800 active refugee families their 40 caseworkers should visit, so that over the full 52-week programme year, aggregate family welfare is as high as possible. "Welfare" is measured as **total family-weeks in the 'stable' category across the cohort, minus weeks in 'crisis' (weighted more heavily because crisis weeks cause lasting damage)**. They currently use a mix of a fixed rotation and squeaky-wheel triage, and they know this causes them to over-serve well-coping families while missing families that are quietly deteriorating.

## What limits what they can do

- **Capacity:** 40 caseworkers, each can realistically do exactly one meaningful home visit per week → hard cap of **40 visits per week**.
- **Population:** ~800 families active in the first-year programme at any time.
- **Horizon:** decisions must be made week-by-week for 52 weeks, but planned so that near-term decisions anticipate long-term consequences.
- **Observation limits:** family state (stable / at-risk / crisis) is only updated when a caseworker sees them — so visiting is also how they gather information.
- **Historical data is observational, not randomised** — past caseworker priority calls confound the record.
- **Team capacity:** two in-house analysts with SQL and Python, no specialised optimisation expertise. Budget is modest; open-source preferred. Six-month pilot window.
- **Governance:** output must be a recommendation that supervisors can override, not an opaque directive.

## What decisions are in their control

Each week, they choose a **subset of exactly 40 families out of ~800** to receive a home visit from a caseworker. This same decision recurs every week for 52 weeks. Caseworker-to-family assignment is a downstream logistics step they do not consider part of this question — the core decision is the 40-family selection.

## Data available

- **Historical records, 3 years (~2,400 families completed)**: intake assessments, weekly visit logs, caseworker notes, quarterly formal status reviews. The stable/at-risk/crisis trajectory can be reconstructed week-by-week for every past family.
- **Intake features on every family**: country of origin, family composition, languages, employment history, education, trauma screening score, co-arriving community, pre-existing medical conditions, neighbourhood of placement.
- **Real-time weekly caseworker notes** on currently active families.

## Scale

- 800 active families × 52 weeks = **~41,600 family-weeks per cohort-year** of decisions.
- At each week, choose 40 from ~800 → decision space per week is astronomically large (C(800,40)), and 52 such correlated decisions in sequence.
- 3 states per family (stable / at-risk / crisis) with stochastic transitions modulated by whether a visit occurred.
- ~2,400 historical family trajectories for model training.

## End state

A **repeatable, defensible weekly prioritisation system** that, given the current state of every family, outputs a recommended list of 40 families to visit this week, chosen to maximise expected `sum_{families, weeks} stable_indicator - w * crisis_indicator` over the remainder of the year. Supervisors can override. The system should also surface which intake signals most strongly predict later trajectory, so newly-arriving families can be flagged for closer early attention.

## Notes / uncertainties

- **Effect of a visit varies by family**: high for families near crisis, low for long-stable families. Estimating per-family, per-state visit effect from observational (non-randomised) data is a known concern the user flagged — causal-inference care will be needed in the upstream estimation step.
- **Partial observability**: the system only "sees" a family's state when a caseworker visits. This means visiting is simultaneously (a) an intervention that changes dynamics and (b) an information-gathering action. A reasonable model might make simplifying assumptions (e.g., state is inferable from recent-enough visits plus intake features) before we push into full partial-observability territory.
- **Fairness / coverage floor**: the user did not state one explicitly, but a programme director will almost certainly want a constraint like "no family goes more than N weeks without a visit" for equity and duty-of-care. Flag for problem-specification stage.
- **Drift correlated across families** (neighbourhood-level shocks, policy changes): probably second-order for a first-cut model.
- **End state is clearly defined** (stable-weeks − weighted crisis-weeks) and **activities are clearly defined** (weekly selection of 40 families). → Technical, proceed.
