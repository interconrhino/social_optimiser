# Session 0006 — Conversation Transcript

*Eval mode: proxy_paper_03 (Tri-Valley Workforce Partnership — multi-year apprenticeship placement policy).*
*The "User" is the simulated-innovator role-playing the Head of Strategy of Tri-Valley Workforce Partnership, drawing only on paper_03's content.*

---

**Assistant:** Welcome to the Social Optimiser. I help social innovators figure out whether their problem can be mathematically optimised — and if so, which specific approach to use. Tell me about the challenge you're facing. What outcome are you trying to improve, and what's making it difficult?

---

**User:** We run a regional vocational training and apprenticeship programme across a cluster of towns. Every quarter we decide which of our training slots and apprenticeship openings go to which kind of participant — we serve four groups: school-leavers, mid-career displaced workers, returners, and justice-affected adults. What we really want is a five-year placement strategy, not just a one-off decision, because this quarter's choices change what's available next quarter and which employers keep coming back to us. The hard part is that our board is split — some want to help as many people as possible in total, some want to protect the worst-off group, and some want everyone served roughly proportionally. All three are defensible, and they lead to very different strategies.

**Assistant:** That's helpful. When you say the board is split between those stances, is that a disagreement they need to resolve before we can do useful analysis, or are they actually asking you to help them see the trade-offs so they can choose?

---

**User:** It's the second. They're not asking us to settle it — that's a political and ethical question, not an analyst's call. What they want from us is a small menu — maybe three to ten candidate five-year strategies — where each one is the best possible strategy if a particular balance between "help the worst-off", "balance across groups", and "maximise totals" is the one they end up choosing. Then they pick. If the board chair changes, or the government changes, we re-run it and give them a fresh menu.

**Assistant:** Good. And what decisions are actually in your control each quarter? What do you get to set?

---

**User:** Each quarter we allocate 400–600 training and apprenticeship slots across the four participant groups, and within each group we choose which sub-programme — green energy, advanced manufacturing, allied health, logistics — to route people into. That's the lever. Our horizon is 20 quarters — five years. Total slot capacity is set by employer commitments and funding, and there's a staff-hour budget too, because justice-affected placements eat more caseworker time per head.

**Assistant:** What data do you have to work with, and do you have any way of projecting how a given strategy would play out over the five years?

---

**User:** We have nine years of quarterly operational records — slot allocations by group and sub-programme, placement outcomes at 6- and 12-month follow-up, retention, employer feedback. Participant-level intake data for about 14,000 past participants. Employer-side data on who takes placements from which group. And we commissioned a simulator two years ago — it takes a placement strategy (a decision rule for each quarter given the current state of backlogs and pipelines) and simulates 20 quarters of outcomes group by group. It's imperfect but the board trusts it for scenario comparison.

**Assistant:** Last one — would you and the board all recognise, looking at a given strategy's simulated outcomes for the four groups, whether it's "good" under each of the three stances? I.e. is there agreement on how to read the numbers, even if not on which stance is right?

---

**User:** Yes, that's clear. For any given strategy we can look at the four group-level outcome curves over 20 quarters and say concretely what each group gets. The disagreement is purely about how to weigh those four curves against each other — not about what the curves mean.

---

**Assistant:** I have a good picture of your problem — it is clearly Technical, not Adaptive. The end state is well-defined (a curated menu of candidate five-year strategies each tied to a named ethical stance), the activities are defined (quarterly allocation decisions, evaluated by a simulator the board already trusts), and the disagreement is entirely about *preference weighting*, not about what the problem is. I'm saving a Problem Profile and moving to the formal specification stage.

*(Saved: `session_output/0006/01_problem_profile.md` — Classification: Technical; sub-type: resource misallocation with explicit multi-stakeholder trade-off structure.)*

---

**Assistant:** I've formalised your problem into a mathematical specification. The decision variable is a *policy* (a state-dependent quarterly allocation rule) over a 20-quarter horizon; the objective is to maximise a stance-indexed social welfare function of four group-level outcomes produced by your simulator; the constraints are slot capacity, caseworker-hour budget, pipeline dynamics, eligibility, and employer-side availability. The menu deliverable introduces a second-level choice: a small set of stance points on a one-parameter family of social welfare functions covering utilitarian, proportional, and Rawlsian positions.

*(Saved: `session_output/0006/02_formal_spec.md`.)*

Now I'll identify which optimisation technique is the best match.

---

**Assistant:** I've identified the technique category. The structural features that pick it out are: multiple conflicting objectives (four group outcomes), an explicit deliverable of a small curated menu of near-Pareto-optimal options each tied to a named ethical stance, and a stochastic sequential-decision inner problem evaluated by a trusted black-box simulator. Primary match: **Multi-objective Optimisation**, with Simulation and Integer Programming as alternatives. Confidence: High. Now I'll research the current state-of-the-art algorithms that have been applied to problems like yours.

*(Saved: `session_output/0006/03_classification.md`.)*

---

**Assistant:** I've completed the research. The strongest algorithmic family combines an **outer α-fair / p-mean social welfare scalarisation** — which maps cleanly to your three named stances (totals / proportional / worst-off) and produces a curated menu rather than a dense Pareto frontier — with an **inner simulation-based policy search** (CMA-ES, or Bayesian Optimisation when rollouts are expensive) against your commissioned simulator. AUGMECON2 is an interchangeable ε-constraint alternative for stances expressed as floors. Welfare-aware Multi-Objective Reinforcement Learning (Fan et al. 2023; Pareto Set Learning 2025) is a natural later upgrade. NSGA-III is a reasonable Plan B.

*(Saved: `session_output/0006/04_research_findings.md`.)*

Now I'll select the best method for your specific situation.

---

**Assistant:** I've selected the best method: **α-fair (p-mean) scalarisation sweep over a small ladder of stance points, with CMA-ES as the inner simulation-based policy-search solver against your commissioned simulator**. This gives you (a) a principled, axiomatically characterised menu where each entry has a board-legible ethical name, (b) an interpretable, auditable policy class (~20–50 knobs) that your 3-person Python data team can ship in 8 months, and (c) a clean upgrade path to welfare-aware MORL if the policy class ever proves limiting. I've written out why this beats the alternatives — MORL (harder to audit for a first deployment), NSGA-III (sample-hungrier, menu entries harder to name), linear weighting (misses the Rawlsian stance), and plain simulation (doesn't search). Now I'll put together the full recommendation.

*(Saved: `session_output/0006/05_method_selection.md`.)*

---

**Assistant:** Here is the full recommendation, delivered in two files per the Social Optimiser's depth standard.

**Technical recommendation (`06a_rec_formal_spec.md`):** Formal problem formulation with decision variables (policy θ ∈ ℝ^{20–50}, induced integer allocations x_{g,p,t}), objective (max W_α over the four group-outcome vector from simulator rollouts), constraints (capacity, caseworker budget, pipeline dynamics, employer caps, optional statutory floors, post-hoc menu diversity), parameters, the recommended algorithm (α-fair scalarisation + CMA-ES with AUGMECON2 as interchangeable inner formulation), theoretical properties (α-fair axiomatic characterisation; Pareto efficiency guaranteed at every α; CMA-ES derivative-free with strong empirical performance), implementation guidance (data requirements, parameter calibration, algorithmic steps, open-source software: `cma`, `pymoo`, `scikit-optimize`), and validation (back-testing, baselines, sensitivity analyses, phased pilot).

**Plain-language summary (`06b_rec_plain_english.md`):** A principled menu builder for five-year placement strategies — for each ethical stance on a short ladder, search for the best state-dependent placement rule against your trusted simulator, then hand the board a curated set of 3–10 strategies each with its four group-outcome trajectories and a named ethical label. Data checklist (nothing new to collect; two internal confirmations needed), what the deliverable looks like, confidence and validation, an 8-month plan, and honest caveats (simulator ceiling; policy-language limits; stance is still a board choice; statutory floors).

*(Saved: `session_output/0006/06a_rec_formal_spec.md`, `session_output/0006/06b_rec_plain_english.md`.)*

Would you like me to go deeper on any section, explore the MORL upgrade path, or help you think through the month-1 confirmations (statutory floors, per-capita vs raw, α-ladder design)?

---

*End of transcript. Session closed.*
