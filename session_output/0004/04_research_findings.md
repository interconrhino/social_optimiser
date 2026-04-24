# Method Research Findings

**Session:** 0004
**Technique category:** Multi-objective Optimisation (with Integer Programming as inner solver; Simulation as complementary validation layer)

## State-of-the-Art Algorithms

### 1. AUGMECON2 (Augmented ε-Constraint Method) ⭐ Recommended starting point

**How it works:** AUGMECON2 casts a multi-objective integer program as a family of single-objective integer programs: one objective (the "primary" one, typically the main efficiency objective — in this case expected retention) is maximised while the remaining objectives (the clause-satisfaction scores from the priority paragraph) are moved into the constraints as ε-bounds. By systematically varying the ε-bounds and solving the resulting IPs with an off-the-shelf MIP solver (CPLEX, Gurobi, HiGHS), the method recovers the *exact* Pareto set for a multi-objective integer program. The "augmented" variant adds a small term to the objective that rewards any remaining slack in the constrained objectives, ensuring each returned point is truly Pareto-optimal, not just feasible. AUGMECON2 additionally exploits the slack values at each iteration to skip redundant ε combinations, substantially reducing runtime on combinatorial problems such as knapsack / set-packing structures.

**Key reference:** Mavrotas, G. & Florios, K. (2013). *An improved version of the augmented ε-constraint method (AUGMECON2) for finding the exact Pareto set in Multi-Objective Integer Programming problems.* Applied Mathematics and Computation. https://mpra.ub.uni-muenchen.de/105034/ and https://www.sciencedirect.com/science/article/abs/pii/S0096300313002166

**Theoretical properties:**
- Produces the **exact Pareto set** for multi-objective integer programs (given solver-level optimality for each sub-IP).
- Complexity: dominated by the cost of solving each sub-IP; total cost = (number of ε grid points) × (cost of a single IP solve). Runtime scales well when the per-weight IP is compact (binary knapsack with a small number of side constraints — exactly Rio Valle's weekly sub-problem).
- Avoids redundant iterations via slack-based early termination — a major practical speedup for binary-variable problems.
- Works naturally with auditable solver output (per-run optimality certificate, explicit ε-values).

**Social sector use:** The ε-constraint family (AUGMECON / AUGMECON2 / AUGMECON-R) is standard in humanitarian logistics, healthcare resource allocation, and multi-criteria public-sector planning (facility location, budget allocation with equity targets). It is the default "exact-Pareto" method cited in applied OR literature when decisions are discrete.

---

### 2. Weighted / Preemptive Goal Programming

**How it works:** Each clause of a priority paragraph is encoded as a numerical *target* (e.g. "coverage of first-gen students ≥ 40% of calls" or "coverage of adult learners ≥ last semester's 18%"). Positive and negative *deviation variables* are introduced for each goal, measuring how much the achieved value falls short of or exceeds its target. The objective is a (possibly weighted) sum of *unwanted* deviations, minimised subject to the original decision constraints (weekly budget, per-campus caps, binary variables). Two major flavours:
- **Weighted goal programming**: all unwanted deviations are weighted and summed — natural for "balance all clauses."
- **Preemptive / lexicographic goal programming**: clauses are organised in priority tiers; lower-priority deviations are minimised only after higher-priority ones are fixed at their optimal — natural for "first protect adult learners, then maximise first-gen reach."

Weighted goal programming handles the *weighted-sum* scalarisation mode in Rio Valle's formal spec; lexicographic handles the *lexicographic* mode; a MINIMAX / Chebyshev variant handles the *max-min / protect-the-worst-served* mode. All three fit within the same modelling framework and call the same underlying MIP solver.

**Key reference:** Jones, D. & Tamiz, M. (2010). *Practical Goal Programming.* Springer. See also https://en.wikipedia.org/wiki/Goal_programming and Romero, C. (2004) *Extended goal programming methodology* (https://www.sciencedirect.com/science/article/abs/pii/S0377221716303691).

**Theoretical properties:**
- Reduces a multi-objective problem to a single-objective LP or MIP — tractable and solver-friendly.
- Lexicographic variant provides a strict priority ordering with no inter-clause substitution.
- MINIMAX variant gives *fair* solutions in the Rawlsian sense — it optimises the worst-performing clause.
- Well-studied in multi-stakeholder settings (transport planning, public-health allocation, SDG planning).
- Shares the IP solver backend with AUGMECON2 — they are complementary, not competing, tools.

**Social sector use:** Widely applied in sustainable development, transport policy, healthcare resource allocation, and corporate social responsibility decisions where stakeholder-written targets must be translated into auditable decisions.

---

### 3. NSGA-II (Non-Dominated Sorting Genetic Algorithm II)

**How it works:** An evolutionary / population-based heuristic that maintains a population of candidate solutions (here: candidate weekly call lists) and evolves them using genetic operators (selection, crossover, mutation) while using a *non-dominated sort* to rank candidates by Pareto dominance across all objectives simultaneously. A *crowding-distance* metric preserves diversity across the approximate Pareto frontier. NSGA-II returns an approximate Pareto set in a single run, without needing to pre-specify weights or ε-bounds.

**Key reference:** Deb, K., Pratap, A., Agarwal, S., Meyarivan, T. (2002). *A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II.* IEEE Transactions on Evolutionary Computation 6(2):182-197. See also the Python `pymoo` implementation (https://pymoo.org/).

**Theoretical properties:**
- **Approximate** Pareto set — no optimality guarantee; quality depends on population size, generations, operator tuning.
- Scales to many objectives (NSGA-III for >3 objectives) and large decision spaces where exact methods time out.
- No convexity assumption — handles non-convex, non-linear, and black-box objectives (e.g. a simulator-evaluated "expected retention" objective).
- Runtime is controllable by stopping criterion but has no monotonic improvement guarantee.

**Social sector use:** Very common when objectives must be evaluated via simulation (e.g. agent-based retention models with off-policy corrections) — the exact-solver stack cannot natively call a simulator inside a MIP. Used in engineering, epidemiology, and energy-system planning. Useful here as a *validation / exploration* tool or if the objective functions grow to include simulated retention curves.

---

## Relevant Supporting Literature for This Problem

- **Fairness in multi-objective optimisation**: Hooker, J. (2022). *A Guide to Formulating Fairness in an Optimization Model.* Annals of Operations Research. https://link.springer.com/article/10.1007/s10479-023-05264-y — explicit treatment of how to formalise fairness criteria (max-min, Nash, α-fairness, proportional) as constraints or objectives in MIPs. Directly applicable to translating "protect the worst-served clause" into a solver-ready term.
- **Multi-objective knapsack with equity**: Kozanidis, G. (2009). *Solving the linear multiple choice knapsack problem with two objectives: profit and equity.* Computational Optimization and Applications. https://link.springer.com/article/10.1007/s10589-007-9140-y — the structural template for the weekly call-selection sub-problem (pick K of N binary items, maximise expected benefit subject to budget, with an equity objective).
- **Group-fair allocation under capacity**: the "Group Fairness and Multi-criteria Optimization in School Assignment" line (https://arxiv.org/html/2403.15623) treats exactly the combined-capacity-plus-demographic-coverage structure Rio Valle faces.

## Recent Developments

- **AUGMECON-R** (Nikas et al., 2020, https://link.springer.com/article/10.1007/s12351-020-00574-6) extends AUGMECON to handle floating-point pathologies more robustly — worth using over AUGMECON2 if numerical stability becomes an issue in large problem instances.
- **Fairness-aware evolutionary optimisation** (2024, https://link.springer.com/article/10.1007/s40747-024-01668-w) explicitly treats fairness as a first-class axis in multi-objective evolutionary search — a useful reference if Rio Valle later wants a single-run Pareto approximation plus explicit fairness metrics, rather than an exhaustive AUGMECON2 sweep.
- **Online allocation with group fairness** (2025, https://arxiv.org/abs/2501.15782) — bears on the *sequential* nature of the weekly decision; useful if future work incorporates arrivals/departures of students into the Pareto analysis.

## Research Gaps

- **Translating plain-English priority paragraphs into clauses** (G_k, direction, τ_k, β_k) is not a pure-OR problem — it sits upstream of the optimiser and is under-served by the mathematical literature. This will be a manual-but-auditable translation step in deployment.
- **Off-policy bias in historical call logs**: the reward/transition estimates that feed the objective's expected-retention term must be corrected for the fact that historical calls reflect coach judgement, not randomisation. Inverse-probability-weighting or doubly-robust estimators are standard but not native to the multi-objective literature.
- **Sequential / restless dynamics**: the 12-week horizon with latent engagement state is acknowledged in the formal spec but is not the primary driver of the chosen framework. A fully sequential treatment (per-student Markov models, shared-budget coupling) lies in the restless-bandit / weakly-coupled-MDP literature; whether to pull that in is a capacity question for method-selection.

## Sources

- [Mavrotas & Florios 2013 — AUGMECON2](https://mpra.ub.uni-muenchen.de/105034/)
- [AUGMECON2 on ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0377221722006142)
- [ε-constraint handling in pymoo](https://pymoo.org/constraints/eps.html)
- [Hooker 2022 — A Guide to Formulating Fairness](https://link.springer.com/article/10.1007/s10479-023-05264-y)
- [Goal Programming — Wikipedia](https://en.wikipedia.org/wiki/Goal_programming)
- [Extended goal programming with multiple stakeholders](https://www.sciencedirect.com/science/article/abs/pii/S0377221716303691)
- [Deb et al. 2002 — NSGA-II (PDF)](https://eng.auburn.edu/~aesmith/files/Multi-objective%20optimization%20using%20genetic%20algorithms.pdf)
- [Multi-objective knapsack JuMP tutorial](https://jump.dev/JuMP.jl/stable/tutorials/linear/multi_objective_knapsack/)
- [Kozanidis 2009 — Multiple-choice knapsack with equity](https://link.springer.com/article/10.1007/s10589-007-9140-y)
- [Group Fairness and Multi-criteria Optimization in School Assignment (arXiv 2403.15623)](https://arxiv.org/html/2403.15623)
- [Fairness-aware multi-objective optimization (2024)](https://link.springer.com/article/10.1007/s40747-024-01668-w)
- [Online Allocation with Multi-Class Arrivals (arXiv 2501.15782)](https://arxiv.org/abs/2501.15782)
- [AUGMECON-R (Nikas et al. 2020)](https://link.springer.com/article/10.1007/s12351-020-00574-6)
