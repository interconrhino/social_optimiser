# Scheduling Weekly Caseworker Home Visits for Newly-Arrived Refugee Families

*Submitted by the Programmes Director, Riverbank Resettlement Network — April 2026*

## Who we are

Riverbank is a mid-sized non-profit that supports refugee families during their first year after arriving in the country. Every family we serve has been through a process that takes months or years — vetting, travel, paperwork — and lands them in a city they have never been to, often with limited English and without a social network. Our mission is to help them get from that first week of disorientation to a stable footing: housing that doesn't fall through, work that pays, kids enrolled in school, and enough community connection that they are no longer alone.

We have been running this programme for about twelve years. Caseworkers do weekly home visits during the first year post-arrival. The visits are the backbone of the programme — they're how we catch problems early (a landlord threatening eviction, a medical issue, a family member pulling away from school), how we connect families to services, and how we maintain trust.

## The problem we're trying to solve

At any given time we have around **800 families active in the first-year programme** across the metro area. We employ **40 caseworkers**, and realistically each caseworker can do one meaningful home visit per week — driving across the city, actually sitting with the family for an hour or two, following up on referrals. **That's 40 visits per week against 800 families.** Do the arithmetic and you'll see it: each family gets a visit roughly every five weeks on average.

What we've been doing is a mix of a fixed weekly rotation, caseworker intuition, and squeaky-wheel triage: whoever calls us in crisis gets moved up. We know this isn't good enough. Families that are doing well sometimes get visited anyway (because they're on the rotation), while families that are quietly slipping — not yet in crisis, but trending badly — don't get a visit for weeks, and by the time we notice, the problem is much harder to fix.

We want to be smarter about which 40 families get a visit each week, and we want the system to work over the full **52-week year**, not week-by-week. The decision we need help with is: **given everything we know about each of the 800 families right now, which 40 should a caseworker visit this week** so that the programme's overall outcomes at the end of the year are as good as possible?

## What "outcomes" means for us

Each week, every family is in one of three broad situations as our caseworkers see it:

- **Stable** — housing, income, school enrolment, health all roughly on track
- **At-risk** — one or more of those is wobbling; not yet a crisis but concerning
- **In crisis** — eviction, job loss, a child out of school, a medical emergency

Families move between these three over time. A visit from a caseworker materially reduces the chance that a family drifts from stable into at-risk, or at-risk into crisis, over the following weeks. But the effect of a visit is not the same for every family — a family near crisis benefits enormously; a family that's been stable for months benefits relatively little. And without a visit, families drift at different rates depending on their situation: a single mother with three kids and no English is much more fragile than a young couple with English and professional backgrounds.

Our "success" at year end is: total family-weeks spent in the stable category across the whole cohort, minus weeks spent in crisis (which we weight more heavily because crisis weeks have lasting damage). We'd like to plan for a full year of weekly decisions that makes this aggregate outcome as good as possible.

## What data we have

- **Historical records from the past three programme years** (~2,400 families who have completed the first year). For each of those families, we have their intake assessment, a weekly log of visits, caseworker notes on their situation each week, and formal status reviews every quarter. From those notes we can reconstruct the stable / at-risk / crisis trajectory for every family, week by week.
- **Intake data on every family**: country of origin, family composition, languages spoken, employment history, education, trauma screening score, whether they arrived with other families from the same community, pre-existing medical conditions, neighbourhood of placement.
- **Real-time caseworker notes** from weekly visits of currently-active families.

We don't have randomised control data — caseworkers in past years were also making priority calls, so the historical record reflects their judgement, not a random policy. That's a constraint we've worried about but haven't known what to do with.

## What we'd like from an analysis

A defensible, repeatable way to answer the weekly question — *"who should the 40 of us visit this week?"* — such that the answer reflects both how badly each family needs a visit right now and how much a visit now will pay off across the rest of the year. We're open to bringing on a technical partner to implement whatever makes sense. We have a small data team (two analysts, SQL and Python) but nobody with specialised optimisation training. Budget for tooling is modest — ideally open-source — and we can commit analyst time over a six-month pilot.

If the analysis also tells us something about **which intake signals most strongly predict trajectory**, that would help us flag newly-arriving families for closer early attention. But the weekly scheduling is the operational core.
