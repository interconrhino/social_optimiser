# Session 0004 — Conversation Transcript

*(Evaluation-mode session. "User" is a simulated innovator role-playing Maria Alcantara, Director of Student Success at Rio Valle Community College Network, from proxy paper paper_01.md. The advisor ran the full 6-skill social_optimiser pipeline.)*

---

**Assistant:** Welcome to the Social Optimiser. I help social innovators figure out whether their problem can be mathematically optimised — and if so, which specific approach to use. Tell me about the challenge you're facing. What outcome are you trying to improve, and what's making it difficult?

---

**User (Maria):** We run a weekly outreach programme at Rio Valle — four community colleges, about 18,000 students a semester. Each week our success coaches call students who look like they're drifting, to nudge them back into engagement. The programme works: students who get a well-timed call stay enrolled at meaningfully higher rates. But we can only make about 210 calls a week across the whole network, and at any given time about 2,100 students are flagged as "at some risk." So the real question we're stuck on is: which 210 students do we actually call each Monday? And that decision has to be made every week for the 12 weeks of the semester.

---

**Assistant:** Thank you — that's a clear picture of the decision. A couple of follow-ups. First, what makes picking those 210 so hard — is it mainly about predicting who's about to slip, or is it more about who to prioritise among a crowded list of deserving students? Second, what are the main things limiting you beyond the 210-call ceiling — staff mix, how students are distributed across campuses, rules about who you can or can't call?

---

**User (Maria):** Honestly it's both, but the harder part is the priority one. The slipping-prediction side is fuzzy — we don't directly see how engaged a student is; we infer it from late assignments, login patterns, when their advisor last heard from them — and the picture is noisy. But we've lived with that fuzziness for years. The newer, thornier issue is that our three funders and our internal equity committee don't want the same thing. Every semester leadership writes a one-paragraph priority statement — something like "give extra priority to first-generation students and to low-income zip codes, while not reducing outreach to adult learners relative to last semester." That sounds fine, but those three clauses pull in different directions: first-gen skews younger, low-income correlates with certain campuses, and protecting adult learners shrinks capacity for the others. Last semester a coach turned the paragraph into a scoring rule and we accidentally dropped outreach to students without dependants by 30% — nobody wanted that. As for limits: the 210 calls a week is the hard ceiling, each campus has its own coaching team with its own capacity, and we have to be able to explain to the board how the paragraph turned into the call list. "The algorithm said so" will not fly with our equity committee.

---

**Assistant:** That's really helpful. Two more things. What decisions are actually in your hands each week — is it purely "which students get a call," or do you also decide things like which coach calls whom, or whether it's a call versus another kind of contact? And when you look at the end of a semester, what would make you say "this worked" — is there a single number you'd point to, or is it more about honoring the priority paragraph without the kind of side-effect you described?

---

**User (Maria):** The decision we're really wrestling with is the call list — who gets called this week out of the watch-list. Within a campus the coach assignment is more of a scheduling detail our team handles; and we use calls as the main contact channel, occasionally a text nudge, but the scarce thing is a coach's time on a call. So for this conversation, think of it as: which ~210 students, out of ~2,100 flagged, get a call this week. On what "worked" means — I'd say it's two things, not one. Yes, we care about total students kept enrolled, that's the headline. But just as much, we need to be able to show that the call list honoured each clause of the priority paragraph — and that we didn't quietly starve some group we never meant to deprioritise. We actually want to be able to see, for a given recipe, how well it honours each clause, and choose whether to balance evenly across clauses, protect the worst-served group, or go for maximum impact. And we want to catch unintended side-effects before we deploy, not after.

---

**Assistant:** Last couple of questions on the practical side. What data do you have to work with — both for the students currently in the system and historically? And how often does the priority paragraph change — every semester, or more often than that?

---

**User (Maria):** Data-wise, we have three years of weekly records for about 12,000 former students: a 0/1 engagement proxy each week derived from LMS activity and assignment submission, and a log of every coaching call that was placed. For each student — past and current — we have 8 to 12 features: age band, income band from FAFSA, first-gen status, home campus, programme of study, dependants, prior-term GPA band, distance-from-campus band. And we have current-week data streaming in for the ~18,000 students this semester. One caveat: the historical call logs reflect the judgement of past coaches, not random assignment, so the data is informative but biased. On the paragraph — it's rewritten at the start of each semester, so roughly every four months. Occasionally leadership tweaks it mid-semester if a funder raises a concern, but that's rare.

---

**Assistant:** Thank you — I have enough to classify and frame your problem. One last check so I'm certain I understood: would it be fair to say that the *end state* is clear (a ranked weekly call list that honours a written priority paragraph and maximises retention), and the *activities* (making calls, recording outcomes, feeding the engagement proxy back in) are already defined and running — the help you want is specifically on the decision rule that turns the paragraph plus the data into the list?

---

**User (Maria):** Yes, that's exactly right. The calls are happening, the data is being collected, coaches know what to do on a call. What we don't have is a defensible, transparent way to turn the priority paragraph plus the weekly data into a specific call list — and a way to see the trade-offs before we deploy. If you can help us with that piece, we'd be very happy.

---

**Assistant (stage announcement):** Thanks, that's enough for me to classify. Your problem is **Technical** on both axes — the end state is defined and the activities are defined; the help you need is on the decision rule itself. I'll write up a Problem Profile and then formalise the mathematical structure. Back shortly.

*(Writes `01_problem_profile.md` — Technical, primary sub-type Resource scarcity with strong Resource-misallocation and Unknown/uncertainty features.)*

*(Writes `02_formal_spec.md` — weekly binary call decisions x_{i,t} ∈ {0,1}; objective is expected retention plus clause-satisfaction scores from the priority paragraph, with three selectable scalarisation modes; hard weekly budget of 210 and per-campus caps; clause floors as soft/hard constraints; uncertainty structure is sequential with partially observed engagement and off-policy historical bias.)*

---

**Assistant (stage announcement):** I've formalised the problem. The structural fingerprint — binary weekly decisions, a weekly budget, conflicting clauses from a priority paragraph that stakeholders disagree about, a need to *see* trade-offs and not hide them behind a composite score — points to **multi-objective optimisation** as the primary technique family, with integer programming as the inner solver and simulation as a useful validation wrapper. Let me search for the best current algorithms in this family.

*(Writes `03_classification.md` — primary match: Multi-objective Optimisation, Medium-High confidence; alternatives: Integer Programming, Simulation.)*

*(Runs web searches on multi-objective integer programming, fair allocation, ε-constraint methods, goal programming; writes `04_research_findings.md` — top algorithms: **AUGMECON2** (augmented ε-constraint, exact Pareto set for MOIP), **Weighted / Preemptive Goal Programming**, **NSGA-II** as heuristic alternative. Supporting literature on fairness formulations, multi-objective knapsack-with-equity, and group-fair allocation.)*

*(Writes `05_method_selection.md` — selected: AUGMECON2 with goal-programming and Chebyshev scalarisations over a shared binary-knapsack MIP backbone; exact per Pareto point; tractable at Rio Valle's scale (~2,100 binaries per weekly IP, K ≈ 3–6 clauses); rejects NSGA-II on auditability grounds, rejects single-objective IP on "collapses the trade-off" grounds, keeps simulation as a validation layer.)*

*(Writes `06a_rec_formal_spec.md` — full formal formulation with decision variables, objective in three modes, constraints, parameters, uncertainty treatment, algorithm rationale, implementation guidance including data table, calibration parameters, algorithmic steps, computational considerations, validation approach with baselines and sensitivity analysis, pilot plan, references.)*

*(Writes `06b_rec_plain_english.md` — plain-language recommendation for Maria and the Student Success team: what the system does, step-by-step explanation, data checklist, what the deliverables are, confidence and validation, a 6–10-week pragmatic roadmap, and honest caveats including predictive-model risk, paragraph-as-political-artefact, no explicit 12-week lookahead, unmodelled peer effects, clause-growth risk, and coach buy-in.)*

---

**Assistant (final):** The recommendation is ready. Short version: we'd build a **trade-off calculator** on top of multi-objective integer programming — specifically the **AUGMECON2** method, which sweeps trade-offs between the priority-paragraph clauses and returns, for each, the *provably optimal* weekly call list of 210 students. You get a menu of call lists, each with a scorecard showing per-clause satisfaction and per-demographic-slice coverage (including slices *not* named in the paragraph, so the 30%-drop-in-students-without-dependants type of surprise gets caught before deployment, not after). Three modes are built in: balance all clauses, protect the worst-served clause, or maximise retention subject to clause floors — leadership picks. The details, including the data you already have vs. the small gaps to fill, the 6–10-week roadmap, and honest caveats, are in `06a_rec_formal_spec.md` (for your data scientists) and `06b_rec_plain_english.md` (for leadership and the board).

Happy to go deeper on any piece — the paragraph-to-clause workshop, the off-policy statistics for the retention model, the Pareto visualisation, or the pilot plan.
