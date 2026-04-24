# Session 0002 — Conversation Transcript

*This session was run in evaluation mode. The "User" is a simulated-innovator subagent (see `.claude/skills/simulated-innovator.md`) role-playing the Programmes Director of Riverbank Resettlement Network, with knowledge bounded by `eval/proxy_papers/paper_04.md`.*

---

**Assistant:** Welcome to the Social Optimiser. I help social innovators figure out whether their problem can be mathematically optimised — and if so, which specific approach to use.

Tell me about the challenge you're facing. What outcome are you trying to improve, and what's making it difficult?

---

**User:** Honestly, it's a staffing-versus-need problem that we can't solve just by working harder. We've got around 800 refugee families in their first year with us, and only 40 caseworkers who can realistically each do one proper home visit a week — so on average a family sees us once every five weeks, which isn't enough. Right now we pick who gets a visit through a mix of a fixed rotation and whoever's shouting loudest, and we keep getting caught out by families who were quietly drifting until suddenly they're in crisis — eviction, a kid out of school, a job gone. What I want is a smarter way to decide, each week, which 40 families our caseworkers should actually go see, so that by the end of the year more families are stable and fewer have hit crisis. We've got three years of historical case notes and intake data to work from, but nobody on our team with the technical background to know what to do with it. That's really why I'm here.

---

**Assistant:** Thanks — that's really useful. A couple of follow-up questions so I can understand the problem properly. First: when you say "more stable and fewer in crisis" at the end of the year, is that something you measure concretely — like, could you look at two different ways of scheduling visits and say objectively which one did better? Second: what specifically is in your data from those three years — are you able to tell, week by week, which families were in stable/at-risk/crisis and when they were visited? And third: is there anything beyond the 40-visits-a-week limit that constrains which families you can visit — geographic restrictions, specialist caseworker matching, anything like that?

---

**User:** Yes, we can measure it — at the end of every year we tally up, for each family, how many weeks they spent stable versus at-risk versus in crisis, and we weight the crisis weeks more heavily because those tend to leave lasting damage. So if you gave me two different visit schedules run over the same cohort, I could tell you which one produced more stable-weeks and fewer crisis-weeks across the 800 families — that's genuinely how we think about success. On the data side, yes, for the last three years we've got roughly 2,400 completed families with weekly caseworker notes and quarterly formal reviews, and from those we can reconstruct each family's stable/at-risk/crisis status week by week alongside when they were actually visited; the one honest caveat is that the visits in that history weren't random, they reflect the caseworkers' own judgement calls at the time, which we've always wondered whether it muddies the picture. As for other constraints — it's mostly the 40-a-week ceiling, but there is some geography to it because caseworkers are loosely assigned to parts of the metro area and a visit across the city eats half a day, and occasionally we need to match on language or on a caseworker who's built trust with a particular family, especially around trauma. Those aren't hard walls but they do shape who can realistically visit whom in a given week.

---

**Assistant:** That's a well-scoped problem — concrete success metric, rich data, and clear constraints. I have everything I need from the intake. Two notes before I move on:

First, this is a *technical* problem in our classification — you have a defined end state (your aggregate welfare metric) and a defined action space (visit / don't visit each family each week). We can proceed to the full optimisation pipeline.

Second, I'm flagging the caseworker-judgement-in-the-historical-data concern as something the method selection will need to address explicitly. You're right to worry about it — it's not a made-up concern, it's a well-known issue in this kind of data. Whatever we recommend will have to correct for it, not ignore it.

Let me now formalise your problem into a precise mathematical specification — I'll be back with that shortly.

*[The assistant then ran `problem-specification` → wrote `02_formal_spec.md`, `optimization-matcher` → wrote `03_classification.md`, `method-research` (with web-search subagent) → wrote `04_research_findings.md`, `method-selection` → wrote `05_method_selection.md`, and `recommender` → wrote `06a_rec_formal_spec.md` and `06b_rec_plain_english.md`.]*

---

**Assistant:** I've put the full recommendation together. Two files:

- **`06a_rec_formal_spec.md`** — the formal version, for a data scientist or analyst who will implement the method. It covers the mathematical formulation, the specific algorithm (Decision-Focused Learning applied to a restless-bandit structure, with a correction for the historical-judgement selection bias), implementation steps, validation approach, and references.
- **`06b_rec_plain_english.md`** — a plain-language version you can share with your board, the two caseworker team leads, or a funder. It covers what the method does, what you need to run it, what it will produce, what to watch out for, and a six-month sequencing from here to a go/no-go decision.

The short version: your problem has a well-studied mathematical structure, and the method we recommend has a published track record in a closely-related social-sector context (large maternal-health programme reaching ~250,000 beneficiaries). The central risk is the selection-bias concern you flagged yourself — we've included a specific correction for it and a validation path (a 13-week shadow deployment) before you change anyone's workflow.

Would you like me to go deeper on any section, explore an alternative algorithm, or help you think through the data-collection step?

---

*[End of in-session exchanges. The director would now review the two recommendation files and decide whether to commission the work. For evaluation purposes this session ends here and is handed to the `recommendation-judge` skill.]*
