# Session 0005 — Conversation Transcript

*Evaluation-mode run. The "User" turns are the simulated-innovator role-playing the Director of Civic Technology from the Northside Participatory Budgeting Coalition (proxy paper_02). The "Assistant" turns are the social_optimiser.*

---

**Assistant:** Welcome to the Social Optimiser. I help social innovators figure out whether their problem can be mathematically optimised — and if so, which specific approach to use. Tell me about the challenge you're facing. What outcome are you trying to improve, and what's making it difficult?

---

**User:** We run participatory budgeting cycles with mid-sized cities — the thing where residents directly decide how to spend a slice of the capital budget in their own district. The bottleneck we keep hitting is the bundling step. Volunteers — our "budget delegates" — sit through weeks of evening meetings trying to package hundreds of raw ideas into twenty or thirty project bundles for the neighbourhood to vote on. They burn out, the bundles drift toward whoever speaks loudest in the room, and smaller cities can't afford to run PB at all because the volunteer hours are just too much. We want to give each panel a software assistant that pre-ranks candidate bundles so delegates refine a short list instead of building bundles from scratch.

**Assistant:** That's helpful. When you say "pre-ranks candidate bundles" — what does a good ranking actually need to reflect? Is there a clear definition of what makes one bundle better than another, and would residents, delegates, and your coalition all agree on that definition?

---

**User:** Yes, that's actually pretty well-defined for us, though it took us a while to get there. A "better" bundle is one that residents in that specific neighbourhood would pick if you showed them the two side by side and asked which would do more for the district over the next five years. We don't define it ourselves from head office — we let the residents in each district define it through pairwise comparisons. So "good" is grounded: it's whatever the residents of that neighbourhood would collectively prefer. Everyone on the coalition signs off on that framing.

**Assistant:** Got it. And concretely — what's in your control here? What exactly does the assistant need to produce, and what are you deciding when you train it?

---

**User:** What we're deciding is the parameters of a medium-sized open-weights language model — something in the 3–8 billion parameter range that will fit on a single GPU inside a partner city's own infrastructure. We fine-tune it on our accumulated pairwise data so that, at deployment, given a district's context and a prompt, it scores any candidate bundle. The score produces a ranking. That ranking is what the volunteer panel sees on day one of their meetings. We don't get to pick the bundles themselves — the delegates still do that, and residents still vote at the end. We pick the training recipe.

**Assistant:** And tell me about your data. How much do you have, what's its shape, and what are the constraints on how it can be used?

---

**User:** Over about three years across fourteen cities we've collected roughly 9,000 pairwise judgement records across about 180 distinct district-prompts. Each record is: here's a district's context, here's a prompt like "prioritise safety for elderly residents", here are two candidate bundles — which does more for the neighbourhood? A panel of 60–90 residents per district, stratified on age, income, tenure, and sub-area, does those comparisons. We also have a smaller set of trained civic-design reviewers who do the same pairs and are more consistent, but they don't always reflect what residents actually feel. The key thing is: for any given pair, what we get isn't a clean "A beats B" — it's something like "residents preferred A with probability about 0.7, and even that 0.7 is fuzzy." Panellists flip on themselves three weeks later, they disagree with each other, attention varies. Plus, at deployment we'll be in new cities that don't look exactly like the training ones — new demographics, new priorities, climate resilience didn't used to matter as much. So the preference pattern at deployment drifts from training.

**Assistant:** Two more things. First — the compute and deployment side: you mentioned on-premises inference, but what about training? And second — what does success actually look like at the end of six months?

---

**User:** Training is on our side. We've got a handful of A100-class GPUs and a six-month runway — that's the budget. Inference has to run inside each partner city's own infrastructure on modest hardware, no paid external model at inference time, because several cities have data-residency rules that rule out sending deliberation content off-site. Success at six months: three new partner cities we didn't train on, and the delegates on the first meeting say "yes, this short list reflects our neighbourhood." Volunteer hours per cycle cut by about a third, without the final neighbourhood vote turnout or approval margin dropping. And a story we can tell city councils about why the rankings are trustworthy, including how it handles the fact that the resident panel wasn't unanimous.

**Assistant:** One more — you mentioned you've tried earlier prototypes that behaved badly: picked up a superficial pattern like "always prefer bundles mentioning youth." What did you learn from that, and what kind of cautiousness do you want the new training recipe to have?

---

**User:** Yes. The earlier prototype over-committed to whatever pattern was loudest in training and then generalised badly — recommended bundles a new neighbourhood would clearly reject. We've also read work that tries to protect against all kinds of training-time noise at once, but that tends to produce an assistant that's timid across the board and not very useful. What we want is something more surgical: cautious specifically on pairs where the resident panel was split or inconsistent, and graceful when the deployment neighbourhood is a bit different from training ones — but not artificially pessimistic everywhere else. The robustness has to be aimed at the right thing: the fact that the preference judgements themselves are noisy and will shift.

**Assistant:** I have a good picture of your problem. The end state is clearly defined (the ranking a representative resident panel would give) and the activities are clearly defined (fine-tune a specific model on your pairwise data) — this is a Technical problem and we can proceed. Let me now formalise it into a precise mathematical specification, then identify the best-fit technique category. I'll be back with the full recommendation shortly.

---

*[Assistant runs stages 2–5 of the pipeline internally: problem-specification → optimization-matcher → method-research → method-selection. Intermediate outputs saved to `session_output/0005/` as `02_formal_spec.md`, `03_classification.md`, `04_research_findings.md`, `05_method_selection.md`. The stage announcements made to the user in chat were:]*

**Assistant:** I've formalised your problem into a mathematical specification. Now I'll identify which optimisation technique is the best match.

**Assistant:** I've identified the technique category — it sits outside the classic operations-research catalog, in the robust statistical-learning family (specifically distributionally robust preference learning). Now I'll research the current state-of-the-art algorithms applied to problems like yours.

**Assistant:** I've completed the research. There's an almost-exact match: a 2025 method by a team at Harvard/CMU called DPO-PRO, demonstrated on a social-sector (maternal-health) fine-tuning task on a single A100 — it's built for exactly your "surgical robustness" ask. Now I'll select the best method for your specific situation.

**Assistant:** I've selected the method. Now I'll put together the full recommendation.

---

**Assistant (final recommendation — summary delivered in chat; full files saved to `session_output/0005/06a_rec_formal_spec.md` and `06b_rec_plain_english.md`):**

Here's the recommendation.

**Technique:** Distributionally Robust Preference Learning, applied to LLM fine-tuning on your pairwise data.
**Algorithm:** **DPO-PRO** (Kim, Verma, Tec & Tambe, 2025 — *Preference Robustness for DPO with Applications to Public Health*, arXiv:2509.02709).

The short version: DPO-PRO is a drop-in modification of the standard pairwise-preference training recipe (DPO) that adds exactly the "surgical cautiousness" you asked for. On each training pair, instead of treating the panel's vote as gospel, it treats the true preference as sitting inside an uncertainty bubble around what the panel reported. It then trains the model to do well *even in the worst case inside that bubble*. Crucially, the bubble's size adapts per pair: on pairs where your panel was unanimous (95/5), the bubble is tiny and training behaves like normal DPO; on pairs where the panel was split (55/45), the bubble is large and the model is explicitly rewarded for *not* becoming too confident. That's the difference between "cautious where the signal was ambiguous" and the "timid across the board" behaviour you've read about and rejected.

Mechanically it collapses into a closed-form regularised DPO loss — ordinary DPO plus one extra term that any engineer who has written a DPO training loop can add in about ten lines. It has an unbiased gradient (so it trains with ordinary SGD), adds essentially no compute overhead, runs on a single A100 40 GB at batch size 2, and has already been demonstrated on a closely analogous social-sector task (ARMMAN maternal-health). The key hyperparameter is a single number ρ controlling the bubble size; you sweep it on held-out *cities* (not just held-out pairs).

I've written two files in your session folder:
- `06a_rec_formal_spec.md` — the full mathematical formulation, algorithmic steps, validation plan, and references, targeted at your two-person ML team.
- `06b_rec_plain_english.md` — a plain-language version suitable for a city-council or board conversation.

The most important caveat: DPO-PRO gives you strong robustness to "the training panel was split" and moderate robustness to "the new city's preferences are somewhat different." It does NOT by itself fix a genuinely large shift — for that, budget a small per-city pilot batch (say 300–500 fresh pairwise judgements) before the first PB cycle in each new partner city, and do a short per-city fine-tune on top. I've put a six-month timeline and a three-criterion pilot protocol in the plain-language file.

Would you like me to go deeper on any section — the ρ-tuning protocol, the district-level split design, the calibration-curve story for city councils, or the per-city pilot-batch plan?

---

*[Session end.]*
