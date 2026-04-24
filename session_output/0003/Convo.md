# Session 0003 — Conversation Transcript

*Evaluation-mode session on proxy paper 04 ("Scheduling Weekly Caseworker Home Visits for Newly-Arrived Refugee Families"). The "user" is the simulated Programmes Director of Riverbank Resettlement Network, voiced per `.claude/skills/simulated-innovator.md`.*

---

**Assistant:** Welcome to the Social Optimiser. I help social innovators figure out whether their problem can be mathematically optimised — and if so, which specific approach to use.

Tell me about the challenge you're facing. What outcome are you trying to improve, and what's making it difficult?

---

**User (simulated Programmes Director):** We run a resettlement programme for refugee families in their first year after arrival — about 800 families live in our programme at any time, across the metro. Our caseworkers do weekly home visits, and those visits are really the backbone: it's how we catch problems early before they become crises. The trouble is we have 40 caseworkers and each can realistically do one visit a week, so that's 40 visits against 800 families — roughly one visit per family every five weeks. Right now we use a mix of rotation and triage-by-whoever-shouts-loudest, and families that are quietly slipping get missed until they're in full crisis. We want a smarter way to pick the 40 families to visit each week.

---

**Assistant:** That's really helpful, thank you. Two things I'd like to understand to get a clearer picture. First, what does "success" look like to you at year-end — how would you know the new scheduling is working? And second, what do you already know about each family when you're deciding who to visit?

---

**User:** Success for us is total family-weeks spent in the "stable" category across the whole cohort, minus weeks spent in "crisis" — we weight crisis weeks more heavily because the damage tends to last. We see every family as being in one of three situations each week: stable, at-risk, or in crisis. Families drift between these states, and a visit materially lowers the chance that a stable family slips to at-risk, or an at-risk family slips into crisis — though the effect of a visit varies a lot by family. As for what we know: at intake we have country of origin, family composition, languages, employment and education history, trauma screening, neighbourhood, that sort of thing. Week by week, caseworkers log notes and we update the stable/at-risk/crisis assessment. And we have three years of this for about 2,400 past families.

---

**Assistant:** Very clear. Two more questions. Are you planning this week-by-week in isolation, or do you want the system to look across the full year so that today's decision credits future payoff? And do you have any modelling capacity in-house, or would this need an external partner?

---

**User:** We want it to work across the whole 52-week year — so the decision each week should look ahead, not just solve next week. A visit now to a family that's trending badly might matter more than a visit to a family that's doing fine today but will be fine regardless. In terms of capacity: we have two analysts who know SQL and Python, nobody with specialised optimisation training. Budget is modest, ideally open-source tooling, and we can commit analyst time over a six-month pilot. We'd bring on a technical partner for the heavy implementation.

---

**Assistant:** Last check on alignment: do you and your leadership agree on the success metric you described — stable-weeks minus weighted crisis-weeks — and is everyone comfortable with a model-driven weekly recommendation, given it would be a recommendation the supervisors could override rather than a black-box directive?

---

**User:** The metric is one we've discussed internally and leadership backs it — it reflects how we actually think about outcomes. On the model deciding: we'd want it as a recommendation the supervisors can override, not a black box that hands caseworkers a list. But directionally, yes, everyone agrees we need a defensible, repeatable system and our current approach isn't it.

---

**Assistant:** I have a good picture of your problem. Classification: **Technical** — the end state is clearly defined (stable-weeks minus weighted crisis-weeks) and the activities are clearly defined (weekly selection of 40 families). Sub-type: primarily Scale, with elements of Unknown/Uncertainty (stochastic family trajectories) and Resource Scarcity (40 visits / 800 families). I'll now formalise this into a precise mathematical specification — I'll be back with that shortly.

*[Stage 1 complete — Problem Profile saved to session_output/0003/01_problem_profile.md]*

---

**Assistant:** I've written up a formal specification of your problem. The core of it: a policy π that, each week t ∈ {1,…,52}, picks 40 families out of ~800 to visit (binary decision x_{i,t}), given that each family's situation (stable/at-risk/crisis) evolves stochastically week by week under a transition model we'll estimate from your three years of historical data. The objective is expected Σ (stable-weeks) − w·Σ (crisis-weeks) over the full year, with a hard weekly capacity of exactly 40 visits and a recommended soft coverage floor (no family unvisited for more than ~8 weeks). I've flagged that the historical data is observational — past caseworker priority calls confound visit-effect estimation — and that we'll need causal-inference care upstream.

Now I'll identify which family of optimisation techniques best fits this formal structure.

*[Stage 2 complete — Formal Spec saved to session_output/0003/02_formal_spec.md]*

---

**Assistant:** Classification complete. The structural backbone of your problem — pick K items from N at each of T rounds under a Markovian per-item stochastic process, observe outcomes, update, repeat — falls into the sequential-decision family. In the catalog I consulted, the closest entry is "Influence Maximisation (POMDP)", which shares the multi-round K-of-N structure and partial-observability machinery, though its network-spread framing doesn't apply to you directly (your families are independent, not connected in a network). I've flagged this fit as structural, not thematic, at Medium confidence, and I'll let the method-research stage search on the problem's formal structure rather than on any pre-committed technique name. Alternatives considered: Integer Programming (discards the sequential structure), Simulation (excellent for evaluation, not decision-making).

Now I'll research the current state-of-the-art algorithms that have been applied to problems with this structure.

*[Stage 3 complete — Classification saved to session_output/0003/03_classification.md]*

---

**Assistant:** Research complete. The structural search converged cleanly on a well-established method family from operations research and ML for social good: **Restless Multi-Armed Bandits (RMAB) solved via the Whittle Index Policy**. This is the canonical tool for exactly your pattern — N independent Markov-evolving items, a per-round cardinality budget, stochastic rewards, long horizon — and it has been deployed at scale in closely adjacent settings: notably the ARMMAN maternal-and-child-health programme in India (the SAHELI system), where a randomised field trial with ~9,000 beneficiaries showed statistically significant reductions in engagement drop-off versus round-robin baselines (Wang et al., AAAI 2023). The Whittle index reduces your otherwise-intractable joint decision (C(800,40) weekly action space, 3^800 joint state space) to 800 independent per-family priority-score calculations: compute a score for every family, visit the top 40. Recent developments worth noting: Decision-Focused Learning (Wang et al. 2023), Bayesian online variants for unknown transitions (Baek et al. 2024), and Neural Whittle Index if analytic indexability fails (Nakhleh et al. 2021).

Now I'll select the single best method for your specific situation.

*[Stage 4 complete — Research Findings saved to session_output/0003/04_research_findings.md]*

---

**Assistant:** Method selected: **Whittle Index Policy for Restless Multi-Armed Bandits**, with a learned per-family transition model (fit from your three years of data, with causal-inference adjustment for past-caseworker confounding), optionally upgraded in phase 2 to **Decision-Focused Learning** (the same technique ARMMAN uses in production). Asymptotically optimal as N→∞ with K/N fixed (your N=800, K/N=5% sits well inside the asymptotic regime). Execution is trivial — weekly scheduling runs in milliseconds on a laptop. The single highest-risk element is the causal-inference step upstream; the method itself is well-studied and the open-source implementation is straightforward for your two analysts.

Now I'll put together the full recommendation, in two documents: one formal spec for your data analysts and any external technical partner, and one plain-language summary for your leadership and board.

*[Stage 5 complete — Method Selection saved to session_output/0003/05_method_selection.md]*

---

**Assistant:** Recommendation complete. I've produced two documents:

- **06a_rec_formal_spec.md** — full formal problem formulation, algorithm specification with theoretical properties, data requirements, implementation steps, software stack (all open-source Python), validation approach, and references. Written for your analysts and external technical partner.
- **06b_rec_plain_english.md** — a plain-language summary for leadership: what the method does, how it works step by step, what data you need (you already have nearly all of it), what it will produce, how to validate it (shadow mode → split rollout → evaluate), and honest caveats. Written to be shareable at a board meeting.

The bottom line for Riverbank: your problem has a clean mathematical structure that matches a very well-studied tool — the same tool public-health NGOs are already using at larger scale for essentially the same "who gets limited caseworker attention this week?" question. The method produces a transparent priority score per family, runs in milliseconds, needs only data you already have, and can be built and piloted by your existing analyst team (two analysts, SQL/Python) within your six-month window. Phase 0–1 is data engineering and model fitting (~10 weeks); months 3–5 are shadow mode and partial rollout; month 6 is evaluation. The phase-2 Decision-Focused Learning upgrade — which ARMMAN deploys in production — can be layered on in year 2 if you bring in a partner with PyTorch experience.

Would you like me to go deeper on any section, explore an alternative algorithm, or help you think through the data collection step?

*[Stage 6 complete — Recommendation saved to session_output/0003/06a_rec_formal_spec.md and session_output/0003/06b_rec_plain_english.md]*

---

## Session close

All pipeline artefacts saved to `session_output/0003/`:
- `eval_tag.json`
- `01_problem_profile.md`
- `02_formal_spec.md`
- `03_classification.md`
- `04_research_findings.md`
- `05_method_selection.md`
- `06a_rec_formal_spec.md`
- `06b_rec_plain_english.md`
- `Convo.md` (this file)
