# Optimisation Recommendation — Formal Specification

**Session:** 0004
**Problem domain:** Education / student-success retention outreach
**Technique:** Multi-objective Integer Programming (exact-Pareto generation)
**Algorithm:** AUGMECON2 (augmented ε-constraint method) with Weighted Goal-Programming and Chebyshev (min-max) scalarisation modes, all layered on a shared binary-knapsack MIP backbone

---

## 1. Problem Formulation

### Decision Variables

- **`x_{i,t} ∈ {0, 1}`** — binary. Equals 1 if student *i* receives a coaching call in week *t*, 0 otherwise. Defined for every student *i* on campus *c(i)*'s week-*t* watch-list `W_t`.
- **`d^+_k, d^-_k ≥ 0`** — continuous, non-negative. Positive/negative deviation of clause-*k* achievement from its target `τ_k` (introduced by the goal-programming layer; used only when the goal-programming scalarisation is active).
- **`z ≥ 0`** — continuous, non-negative. Auxiliary max-min variable for the Chebyshev scalarisation mode (bounds the worst-performing clause from below).

Indexing:
- *i* indexes students; *c(i) ∈ {1,2,3,4}* is student *i*'s home campus.
- *t ∈ {1,...,T}* with *T=12* weekly decision epochs.
- *k ∈ {1,...,K}* indexes clauses of the semester's priority paragraph (typically K ≈ 3–6).

### Objective Function

Three modes, selectable by leadership, all solved by the same underlying IP:

**Mode A — Lexicographic / ε-constraint (AUGMECON2 primary):**
```
maximise   Σ_{t=1..T} Σ_{i ∈ W_t} r_{i,t} · x_{i,t}            (Retention)
subject to C_k(x) ≥ ε_k     for each clause k = 1..K            (Clause floors)
```
Sweep the ε_k grid to trace the exact Pareto set. Augmentation term `+ λ · Σ_k s_k` (with tiny λ > 0 and slacks `s_k = C_k(x) − ε_k`) guarantees returned points are Pareto-optimal.

**Mode B — Weighted goal programming:**
```
minimise   Σ_k w_k · (d^+_k + d^-_k)                            (Weighted deviations)
subject to C_k(x) + d^-_k − d^+_k = τ_k                         (Target equations)
```
Leadership sets weights `w_k` per clause, expressing relative importance. Retention enters as one of the K goals (with its own target and weight).

**Mode C — Chebyshev / max-min (protect-the-worst-served):**
```
maximise   z
subject to C_k(x) ≥ z     for each clause k = 1..K
           Σ_{i,t} r_{i,t} · x_{i,t} ≥ R_min                    (Retention floor)
```

All three modes share the same feasible-set constraints below and produce the same per-clause dashboard.

Where:
- `r_{i,t}` = estimated expected end-of-semester retention gain from calling student *i* in week *t*, given features and engagement proxy.
- `C_k(x) = f_k(x, demographics)` = clause-*k* satisfaction score (e.g. weighted coverage of group G_k, or relative-to-baseline preservation ratio).
- `τ_k` = target level for clause *k* (in goal-programming mode).
- `w_k` ≥ 0 = relative importance weight for clause *k*.
- `ε_k` = lower bound for clause *k* (swept by AUGMECON2).
- `R_min` = minimum acceptable expected retention (Mode C only).

### Constraints

**Total weekly capacity:** Network-wide calls per week cannot exceed 210 →
`Σ_{i ∈ W_t} x_{i,t} ≤ B = 210`     for all *t*

**Per-campus capacity:** Each campus has its own coach-team capacity →
`Σ_{i ∈ W_t, c(i)=c} x_{i,t} ≤ B_c`     for each campus *c*, each week *t*,    with `Σ_c B_c = 210`

**Eligibility:** Only currently-flagged students can be called →
`x_{i,t} = 0` if *i ∉ W_t*

**Binary decisions:** →
`x_{i,t} ∈ {0, 1}`

**Clause-satisfaction scoring (definitional, not a constraint):** For each clause *k*, `C_k(x)` is a pre-defined linear function of *x* and student demographics. Example clause forms:
- Group-coverage clause: `C_k(x) = (Σ_{t} Σ_{i ∈ G_k} x_{i,t}) / (Σ_t |G_k ∩ W_t|)` — fraction of flagged-in-group-G_k students called over the semester.
- Baseline-preservation clause: `C_k(x) = (Σ_{t} Σ_{i ∈ G_k} x_{i,t}) − last_semester_baseline_k` — keep outreach to G_k at or above last semester.

**Monitored-slice reporting (non-constraint, dashboard):** For each monitored demographic slice *g* not named in the paragraph, compute `coverage_g(x)` and flag if `|coverage_g(x) − baseline_g| > δ` (unintended side-effect alarm).

### Parameters

| Symbol | Meaning | Value / Source |
|---|---|---|
| `B` | Total network weekly call capacity | 210 (known) |
| `B_c` | Per-campus weekly call capacity, 4 values | Known from leadership; sums to 210 |
| `T` | Semester length in weekly epochs | 12 (known) |
| `W_t` | Week-*t* watch-list | Known each week (output of the existing flagging rule) |
| `r_{i,t}` | Expected retention gain from calling *i* in week *t* | **Estimated** from 3 years of historical records via a predictive model with off-policy correction (IPW or doubly-robust) |
| `G_k`, `τ_k`, `w_k`, `ε_k` | Clause groups, targets, weights, bounds | **Translated** from the semester's priority paragraph in a documented workflow with leadership |
| `baseline_g` | Per-slice historical coverage | Computed from last semester's call log |
| `R_min` | Minimum acceptable retention (Mode C) | Set by leadership as a fraction of the retention-only optimum |
| `λ` | AUGMECON2 augmentation weight | Small positive (e.g. 10⁻³ × typical retention gain) |

### Uncertainty

- **Latent engagement state** per student is partially observable; only a noisy 0/1 weekly proxy (LMS activity + assignment submission) plus slow demographics are seen. This is handled *upstream* of the IP — the predictive model that yields `r_{i,t}` is trained to predict end-of-semester retention gains directly from observable features and the proxy, so the IP consumes point estimates, not raw state.
- **Off-policy bias in historical data**: past calls were coach-chosen, not random. The retention-model fit must correct for this (inverse-propensity weighting, doubly-robust estimation, or a counterfactual-prediction formulation).
- **Sequential dynamics**: modelled via a weekly re-optimisation loop — the IP is re-solved each Monday with freshly estimated `r_{i,t}` using that week's engagement data. This is a myopic-with-re-planning approximation to a fully sequential Markov formulation, and is defensible because (a) the solve is cheap, (b) the state-observation cycle is weekly, and (c) leadership values auditability over marginal gains from lookahead.
- **Priority-paragraph translation uncertainty**: the mapping from plain-English clauses to `(G_k, τ_k, w_k)` is explicit, documented, and reviewed each semester with leadership sign-off.

---

## 2. Recommended Algorithm

**Algorithm:** AUGMECON2 (augmented ε-constraint method) as the Pareto-generation wrapper; Weighted Goal Programming and Chebyshev min-max as alternative scalarisation modes on the same IP; inner sub-problem solved by branch-and-bound / branch-and-cut.
**Class:** Multi-objective Integer Programming (MOIP), exact.

### Why this algorithm

The weekly sub-problem is a small, well-conditioned binary knapsack-with-side-constraints (~2,100 binaries, ~10 constraints) that commodity MIP solvers handle to proven optimality in seconds. Wrapping it in AUGMECON2 — a method specifically engineered to recover the *exact* Pareto set of multi-objective integer programs by sweeping ε-bounds on all-but-one objective — lets Rio Valle generate, visualise, and choose among Pareto-optimal call lists that honour the priority-paragraph clauses to varying degrees. The three scalarisation modes (ε-constraint for Pareto sweep, weighted goal programming for balanced-weights mode, Chebyshev for protect-the-worst-served mode) share the same IP backbone and the same per-clause scoring dashboard, giving the board an auditable, single-pipeline answer to "how was this call list derived from that paragraph?" AUGMECON2 beats evolutionary alternatives (NSGA-II/III) here because (a) the IP is exactly tractable at this scale, (b) board-level auditability demands proven optimality per Pareto point rather than a heuristic approximation, and (c) the explicit ε-grid provides an interpretable tuning knob (one ε per clause) that maps directly onto leadership's mental model.

### Theoretical properties

- **Optimality:** *Exact.* Each Pareto point is the global optimum of a scalarised IP; AUGMECON2 is proven to produce the complete Pareto set of the MOIP at grid resolution (Mavrotas & Florios 2013). Goal-programming mode yields the weighted-deviation-minimising allocation exactly; Chebyshev mode yields the max-min-optimal allocation exactly.
- **Complexity:** Each sub-IP is NP-hard in the worst case but solved routinely by modern branch-and-cut for problems of this size (≈ 2,000 binaries, few constraints). Pareto sweep cost: O(G^(K-1)) sub-IPs with K clauses and G grid points per clause — minutes to an hour on a laptop for typical K ≈ 3–6, G ≈ 10–20.
- **Key references:**
  - Mavrotas, G. & Florios, K. (2013). *An improved version of the augmented ε-constraint method (AUGMECON2) for finding the exact Pareto set in Multi-Objective Integer Programming problems.* Applied Mathematics and Computation 219(18): 9652-9669. https://mpra.ub.uni-muenchen.de/105034/
  - Jones, D. & Tamiz, M. (2010). *Practical Goal Programming.* Springer.
  - Hooker, J.N. (2022). *A guide to formulating fairness in an optimization model.* Annals of Operations Research. https://link.springer.com/article/10.1007/s10479-023-05264-y

### Known limitations

- **Myopic re-planning**: the IP is solved week-by-week with updated coefficients; it does not explicitly optimise a 12-week lookahead. For students whose trajectories benefit from a specific call-week sequence (e.g. call at week 3 conditional on week-2 proxy), this loses some gain relative to a fully sequential method. Acceptable because weekly re-planning with updated data recovers most of that gain in practice, and because full sequential treatment (weakly-coupled MDP / restless bandit) would sacrifice the auditability leadership demands.
- **Coefficient estimation is the statistical bottleneck**: the `r_{i,t}` coefficients are learned from biased history. The IP is only as good as these estimates. Plan for iterative calibration using current-semester data, and communicate confidence intervals on coefficients to leadership.
- **K grows**: with >6 clauses, the Pareto sweep cost grows exponentially. Fall back to weighted goal programming or NSGA-III for approximate Pareto generation.
- **Unmodelled peer effects**: if students influence each other's engagement (a plausible effect on a residential campus), the per-student independence assumption is violated. Flag for future work; initial deployment assumes independence.

---

## 3. Implementation Guidance

### Data Requirements

| Data item | Description | Format | Source suggestion |
|---|---|---|---|
| Watch-list `W_t` each Monday | Set of flagged students for the week | List of student IDs × 12 weeks | Existing flagging rule |
| Student features | 8–12 demographic/intake fields per student (age band, income band, first-gen, campus, programme, dependants, prior-term GPA band, distance band) | Tabular, one row per student | Existing student records |
| Weekly engagement proxy `y_{i,t}` | 0/1 engagement indicator | Long table (student × week) | LMS + assignment submission logs |
| Historical call log | 3 years of weekly call records | Long table (student × week × called 0/1) | Coaching database |
| Estimated `r_{i,t}` | Predicted end-of-semester retention gain from a week-*t* call | One scalar per flagged (student, week) pair | Fit a predictive model (gradient-boosted trees or logistic) on historical data with inverse-propensity weights derived from a propensity model over call decisions |
| Clause specification `(G_k, direction, τ_k, w_k)` | Formal translation of each paragraph clause | Small table, ≤ 6 rows | Semester-start workshop with leadership + equity committee |
| Baseline coverage `baseline_g` per monitored slice | Last-semester call-fraction for each demographic slice | Vector | Aggregate prior semester's call log |

### Key Parameters to Calibrate

- **`r_{i,t}` (retention-gain coefficients):** the heart of the objective. Start with a gradient-boosted classifier trained on historical data, with 5-fold CV and IPW for off-policy correction. Sensitivity: **high** — the solver trusts these values implicitly. Report calibration curves to leadership and re-fit mid-semester if drift is detected.
- **`ε_k` grid resolution:** number of ε values per clause in the AUGMECON2 sweep. Start at 10 per clause; increase to 20 if the Pareto front looks sparse. Sensitivity: **medium** — affects granularity of the Pareto picture, not the optimality of each point.
- **`w_k` weights (goal-programming mode):** relative importance of each clause. Start at equal weights; refine with leadership after seeing a test Pareto sweep. Sensitivity: **high** — weights materially change the recommended list; this is by design, and the point of offering the Pareto-sweep mode is to let leadership *see* that sensitivity.
- **`τ_k` targets (goal-programming mode):** e.g. "cover at least 40% of flagged first-gen students" or "match last semester's adult-learner call count." Extract literally from the priority paragraph. Sensitivity: **high** — same rationale as weights.
- **`B_c` per-campus capacity split:** confirm with leadership. Sensitivity: **low-medium** — as long as Σ B_c = 210, the network-wide Pareto shape is close to the no-per-campus-constraint Pareto shape unless campus-level clauses are active.
- **`λ` AUGMECON2 augmentation weight:** tiny positive number (e.g. 10⁻³ × typical retention gain per call). Sensitivity: **low** — picks the augmentation direction, not the set of returned points.

### Algorithmic Steps

1. **Weekly intake (each Monday morning):**
   - Ingest this week's watch-list `W_t`, refreshed engagement proxies `y_{i,t}`, and current demographic/enrolment features.
   - Score every student in `W_t` with the pre-trained retention model to get `r_{i,t}`.
2. **Clause setup (once per semester, revisited if paragraph changes):**
   - With leadership, translate the priority paragraph into clause tuples `(G_k, direction, τ_k, w_k)` and write the resulting clause-scoring functions `C_k(x)`.
   - Record baselines `baseline_g` for every monitored demographic slice (named and unnamed in the paragraph).
3. **Choose scalarisation mode with leadership:**
   - **Pareto-explore mode (AUGMECON2):** run the full ε-sweep to generate the Pareto set of candidate call lists. Visualise: one axis = retention, other axes = clause scores.
   - **Balanced mode (weighted goal programming):** solve a single IP with chosen weights `w_k`.
   - **Protect-worst mode (Chebyshev):** solve a single max-min IP with retention floor `R_min`.
4. **Solve the weekly IP (every mode):**
   - Formulate in a modelling language (Pyomo, PuLP, JuMP, or GAMS).
   - Call an MIP solver (CPLEX / Gurobi / HiGHS).
   - For Pareto mode: loop over the ε-grid, logging each Pareto point with its full (retention, clause-scores, coverage-by-monitored-slice) dashboard.
5. **Review the dashboard:**
   - For each candidate call list, display: expected retention, per-clause `C_k(x)` score vs target `τ_k`, per-monitored-slice coverage vs `baseline_g` (with side-effect-alarm flags for |Δ| > δ).
   - Leadership selects one list (or, in automated-balanced mode, the single returned list is used directly).
6. **Deploy the list**: 210 students for the week.
7. **Observe outcomes, update:** at end of each week, record who was called, engagement changes, and any late-semester retention outcomes. Use for the next round's retention-coefficient update and, at semester's end, for re-training the retention model.

### Computational Considerations

- **Per-IP solve:** seconds for ~2,000 binaries × ~10 constraints with modern branch-and-cut. HiGHS (open-source) or Gurobi/CPLEX (commercial, free academic) all work.
- **Pareto sweep:** K=4 clauses, G=10 grid points each → ≈ 1,000 sub-IPs, ≈ 15–60 minutes on a laptop. Parallelisable across the ε-grid if needed.
- **Scaling:** if watch-list grows to ~20,000 (e.g. network expansion), per-IP solve time grows mildly; still tractable to ~100k binaries for problems of this constraint sparsity.
- **Fallback for scale:** if K grows >6 or n grows >20k and Pareto sweep becomes slow, switch to NSGA-III (approximate Pareto) or to weighted-goal-programming-only (single IP per scalarisation).

---

## 4. Validation

### How to evaluate solution quality

Primary metrics:
1. **Retention rate** among flagged students who received calls vs. a matched-control (propensity-matched) pool of flagged-but-not-called students — the headline measure of programme effectiveness.
2. **Per-clause satisfaction**: for each clause of the semester's priority paragraph, the realised `C_k(x)` vs the target `τ_k`. Reported per-semester to leadership and the board.
3. **Unintended-side-effect detection rate**: count of monitored demographic slices whose coverage deviated from baseline by more than δ, flagged *before* deployment — success is catching these at the Pareto-review stage, not post-hoc.
4. **Pareto spread**: number of distinct Pareto points presented to leadership each semester — a proxy for decision transparency.

### Baseline to beat

**Naive baseline 1 (current practice):** a coach builds a simple scoring rule from the priority paragraph and ranks students (this is what caused the 30%-drop-in-students-without-dependants failure last semester). The optimised approach should beat this on (a) per-clause satisfaction for every named clause, and (b) absence of unintended-side-effect alarms on unnamed slices.

**Naive baseline 2 (retention-only, no equity):** rank all flagged students by `r_{i,t}` descending and call the top 210 each week. The optimised approach will score *lower* on retention alone (by design — equity constraints are binding) but should Pareto-dominate it on every clause the paragraph asks to protect.

**Expected improvement:** the optimised pipeline should achieve comparable retention (within a few percentage points of the retention-only baseline) while honouring all named clauses within target tolerances and raising no unintended side-effect alarms.

### Sensitivity analysis

1. **Retention coefficient perturbation**: re-solve with ±20% noise on `r_{i,t}`. How much does the chosen call list change? If it changes drastically, the solution is brittle — invest in better coefficient estimation.
2. **Clause-weight sensitivity** (goal-programming mode): vary each `w_k` by ±50% and observe Pareto-position shift. Expected to be large — this is the point of showing leadership the trade-off.
3. **Target τ_k sensitivity**: tighten or loosen each target by ±10% and observe retention cost. This answers "what does it cost us to demand 5% more coverage of group G_k?"
4. **Per-campus capacity**: shift ±10 calls between campuses. Observe impact on Pareto shape.
5. **Off-policy bias stress-test**: retrain `r_{i,t}` without IPW correction, compare chosen call lists. Magnitude of change indicates the value of the off-policy correction.

### Pilot approach

Run a **single-campus pilot for one semester** before network rollout:
1. Pick the campus with the cleanest data and the most engaged director (likely to tolerate iteration).
2. Run the pipeline alongside current practice for the first 4 weeks as a shadow system (coaches still make the final call; optimiser produces a recommended list for comparison).
3. From week 5, use the optimiser-produced list as the default, with coach override possible (log every override).
4. End-of-semester: compare retention, per-clause satisfaction, and override rate against historical single-campus baselines.
5. If the pilot campus's per-clause satisfaction is within target and retention holds or improves, roll to the other three campuses in the next semester.

---

## 5. Key References

- Mavrotas, G. & Florios, K. (2013). *An improved version of the augmented ε-constraint method (AUGMECON2) for finding the exact Pareto set in Multi-Objective Integer Programming problems.* Applied Mathematics and Computation 219(18): 9652-9669. https://mpra.ub.uni-muenchen.de/105034/
- Jones, D. & Tamiz, M. (2010). *Practical Goal Programming.* Springer.
- Hooker, J.N. (2022). *A guide to formulating fairness in an optimization model.* Annals of Operations Research. https://link.springer.com/article/10.1007/s10479-023-05264-y
- Deb, K., Pratap, A., Agarwal, S., Meyarivan, T. (2002). *A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II.* IEEE Transactions on Evolutionary Computation 6(2): 182-197.
- Kozanidis, G. (2009). *Solving the linear multiple choice knapsack problem with two objectives: profit and equity.* Computational Optimization and Applications. https://link.springer.com/article/10.1007/s10589-007-9140-y
- Romero, C. (2004). *A general structure of achievement function for a goal programming model.* European Journal of Operational Research.
- Nikas, A. et al. (2020). *A robust augmented ε-constraint method (AUGMECON-R) for finding exact solutions of multi-objective linear programming problems.* Operational Research. https://link.springer.com/article/10.1007/s12351-020-00574-6
- Nemhauser, G.L. & Wolsey, L.A. (1988). *Integer and Combinatorial Optimization.* Wiley. (Branch-and-bound foundation for the inner solver.)
