# Method Selection

**Session:** 0004

## Selected Algorithm

**Name:** AUGMECON2 (Augmented ε-Constraint Method for Multi-Objective Integer Programming) with Weighted Goal Programming and Chebyshev (min-max) scalarisations as configurable modes on top of a shared binary-knapsack MIP backbone
**Category:** Multi-objective Optimisation (driving layer) over Integer Programming (inner solver)
**Type:** **Exact** — optimal with respect to the formalised objectives for each Pareto point returned; the approximation is in the modelling, not the solving

**Why this algorithm:**
The weekly sub-problem — choose ~210 of ~2,100 binary calls subject to a network budget, per-campus caps, and clause-floor constraints — is a small-to-moderate binary integer program (≈ 2,100 binaries, a handful of side constraints), which commodity MIP solvers dispatch in well under a minute. Wrapping that IP in AUGMECON2 systematically sweeps the ε-bounds on each clause-satisfaction score and returns the **exact Pareto set** of call lists that trade off expected retention against each clause of the priority paragraph. This is the right algorithmic shape for Rio Valle's stated need: leadership must see — in advance of deployment — how any given call list scores on *every* clause and on unintended-side-effect slices, and must be able to pick between "balance the clauses evenly" (weighted sum), "protect the worst-served clause" (Chebyshev / max-min), and "maximise retention subject to clause floors" (ε-constraint). All three scalarisation modes share the same underlying IP formulation and the same per-clause scoring dashboard, giving a single auditable pipeline. Goal-programming terms are added to accommodate the "do not reduce adult-learner outreach relative to last semester" style of baseline-preservation clauses natively, and to produce the per-clause deviation metrics that show the board how each clause was honoured.

**Approximation guarantees:**
- For any fixed setting of (weights, ε-bounds, or goal-programming priorities), the underlying binary knapsack with side constraints is solved to **proven optimality** by branch-and-bound / branch-and-cut — no approximation in the solve.
- AUGMECON2 generates the **exact Pareto set** of integer-optimal points, not an approximation, given enough ε-grid resolution. (The ε-grid resolution trades off runtime against Pareto-set granularity.)
- The residual approximation is in *modelling*: the expected-retention term depends on estimated per-student call-effect and transition parameters learned from biased historical data. That is a statistical-estimation concern (off-policy correction, e.g. inverse-propensity weighting), not an algorithmic one.

**Computational complexity:**
- Per sub-IP (one weekly call list under a fixed scalarisation): binary knapsack with ~2,100 binaries + ~10 side constraints — solves in seconds with a commodity MIP solver.
- AUGMECON2 Pareto sweep: O(G^(K−1)) sub-IP solves, where K = number of clauses (~3–6) and G = ε-grid resolution per clause (~10–20). For K = 4, G = 10, this is ~1,000 sub-IPs per Pareto scan, minutes to an hour on a laptop.
- Full semester (12 weeks × one Pareto scan per week, or one scan per semester plus weekly re-optimisation under the chosen scalarisation): well within a standard laptop's capacity.

**Known limitations for this problem:**
- **Does not natively model sequential dynamics.** The expected-retention coefficients `r_{i,t}` must be pre-computed (e.g., as the predicted increase in end-of-semester retention probability from a call in week t given current features and engagement proxy). A fully-dynamic treatment of latent engagement state over the 12 weeks (per-student Markov transitions, shared-budget coupling) is more faithfully handled by weakly-coupled-MDP / restless-bandit methods; those sit outside the catalog and add material complexity. The chosen approach replaces that dynamic with a weekly re-optimisation loop fed with freshly updated retention coefficients — a standard, defensible simplification, but one that sacrifices lookahead.
- **Off-policy bias correction** is the user's responsibility (IPW, doubly-robust, or a counterfactual prediction model trained on historical calls). The MIP itself cannot correct for this.
- **Growing K (many clauses)** blows up the Pareto sweep cost; with >6 clauses, switch to weighted goal programming or NSGA-III for a Pareto approximation instead of a full exact sweep.
- **Side-effect detection on unnamed slices** requires a post-solve reporting layer: for any chosen call list, compute coverage on every monitored demographic slice and flag deviations from baseline. This is a data-processing step, not part of the IP.

## Why not the alternatives

| Alternative | Reason not selected |
|---|---|
| NSGA-II / NSGA-III (evolutionary multi-objective) | Produces only an *approximate* Pareto frontier and has no optimality guarantee per point; at Rio Valle's scale the IP is exactly solvable, so accepting heuristic quality trades away auditability the board explicitly demanded, with no scale benefit in return. |
| Single-objective Integer Programming (IP with a composite weighted objective) | Collapses the trade-off into a single point and hides the per-clause scores, reproducing the failure mode that dropped outreach to students-without-dependants by 30% last semester; it is the inner solver of the chosen approach, not a substitute for the multi-objective wrapper. |
| Simulation (Monte Carlo / agent-based) as primary method | Simulation can score any candidate call list but cannot itself *generate* one; it is the right tool for the side-effect dashboard and for pilot-phase validation, not for producing the Pareto set. |
| Weakly-coupled MDP / restless-bandit methods (outside catalog) | Would handle the sequential / partial-observability dynamics more faithfully, but are substantially harder to explain to the board, require more data-engineering, and do not natively support the three scalarisation modes (weighted-sum / max-min / ε-constraint) that leadership must toggle between. A possible future extension, not a current-phase choice. |

## What the organisation needs before starting

- **Data to collect:**
  - An **estimated per-student retention-effect coefficient** `r_{i,t}` for each flagged student in each week — i.e., the model-predicted increase in end-of-semester retention probability if called this week. This is a supervised learning step using the three years of weekly records and the demographic features, with off-policy correction (inverse-propensity weighting or doubly-robust estimation) to account for the fact that past coaching decisions were not random.
  - A **per-clause scoring function** `C_k(x)` for each clause of the semester's priority paragraph — a formal, auditable translation of the plain-English clause into a numerical score (e.g. coverage ratio, baseline-preservation delta, or group-weighted mean). This translation should be co-produced with the leadership who write the paragraph, and documented for each semester.
  - A **baseline coverage snapshot** from last semester (by demographic slice) so that "do not reduce outreach to group G below last-semester level" clauses have a concrete τ value, and so that unintended-side-effect monitoring has a baseline to diff against.
  - **Per-campus capacity split** (B_c values) confirmed by leadership.
  - **A defined list of monitored demographic slices** for the side-effect dashboard — including slices not named in the paragraph (e.g. commuter students, students without dependants).
- **Skills required:** (a) an analyst comfortable formulating MIPs in a modelling language (Python/Pyomo, Python/PuLP, JuMP, or GAMS) and driving a commodity MIP solver (CPLEX, Gurobi, or HiGHS for open source); (b) a data scientist who can build the off-policy-corrected retention-effect model; (c) a facilitator / programme director who can translate the semester's priority paragraph into clause specifications with leadership sign-off.
- **Estimated effort:** 6–10 weeks for a first working pipeline: ≈ 2 weeks to build the retention-effect model with off-policy correction; ≈ 2 weeks to build the MIP + AUGMECON2 wrapper and the per-clause dashboard; ≈ 2 weeks on the paragraph-to-clause translation workflow with leadership; ≈ 2–4 weeks of piloting on a single campus with historical data before going live across the network.
