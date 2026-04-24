# Method Selection

**Session:** 0006

## Selected Algorithm

**Name:** α-fair (p-mean) scalarisation sweep over a curated ladder of stance points, with CMA-ES as the inner simulation-based policy-search solver against the commissioned simulator. AUGMECON2-style ε-constraint framing is kept as a drop-in equivalent inner formulation for stances that the board prefers to express as floors (e.g. "maximise totals subject to justice-affected outcome ≥ ε").
**Category:** Multi-objective Optimisation (scalarisation family) + simulation-based policy search (inner solver)
**Type:** Approximate (inner solver is a derivative-free stochastic search; outer scalarisation preserves Pareto efficiency exactly)

### Why this algorithm

The user's formal problem has three structural features that together pick out this method uniquely. First, there are four group-level objectives that trade off against one another, and the board wants a curated menu of 3–10 stance-indexed policies rather than a dense Pareto frontier — this is exactly what α-fair / p-mean scalarisation delivers, because a small ladder of α values (α = 0 totals, α = 1 proportional, α → ∞ worst-off, plus two or three interpolating points) produces a principled, axiomatically characterised, interpretable menu that covers the stance spectrum non-redundantly. Second, the three ethical positions the board names (totals / balanced / worst-off) correspond *exactly* to well-studied points on the α-fair family, so the menu is not an arbitrary parameter sweep — each menu entry has a defensible ethical name that a board member or funder can understand without training. Third, the per-stance inner problem is a sequential, stochastic, state-dependent policy search evaluated by a black-box simulator that the board already trusts — CMA-ES is the established derivative-free solver for exactly this regime (noisy, non-convex, moderate-dimensional parameter search against a simulator), with Bayesian Optimisation as a drop-in for when simulator rollouts are expensive. Restricting the policy class to an interpretable, auditable form (e.g. share-vector + backlog-priority parameters, typically O(20–50) parameters) keeps CMA-ES well within its sweet spot and keeps the output legible to the board.

This route deliberately avoids training a black-box MORL neural policy as the first deliverable. A MORL upgrade (Option 2 in the research findings) is a natural second-phase enhancement once the organisation has a working pipeline — but for the initial 8-month engagement with a 3-person Python data team and a strong requirement that the board can *see and audit* each menu entry's policy, the scalarisation + CMA-ES route is materially lower-risk and more interpretable.

### Approximation guarantees
- **Outer (scalarisation):** For every α ≥ 0, the argmax of the α-fair welfare function W_α(y) is Pareto-efficient. The α-fair family is the unique family of social welfare functions satisfying monotonicity, symmetry, scale invariance, and the principle of transfers (axiomatic characterisation — Atkinson; Mo & Walrand). So each menu entry is *guaranteed* to be Pareto-efficient (modulo inner-solver approximation).
- **Inner (CMA-ES):** No global optimality guarantee on a non-convex simulator objective. In practice CMA-ES is a state-of-the-art derivative-free optimiser with strong empirical performance on noisy black-box problems of this scale; asymptotic local convergence under mild conditions. Solution quality is verified by restart-with-random-seeds and by comparing against a strong baseline policy (see validation plan in the final recommendation).
- **If ε-constraint (AUGMECON2) is used instead for some stances:** AUGMECON2 guarantees exact Pareto set enumeration when the inner problem is a solvable IP. Not directly applicable when the inner problem is a simulator-evaluated policy search, but applicable if a surrogate IP approximation of the annual allocation is used for sanity-checking.

### Computational complexity
- **Menu size M:** 3–10 stance points (user-specified).
- **Inner CMA-ES run:** for a policy parameterised by d ≈ 20–50 parameters, expect ~10²–10³ generations of population size ~4 + ⌊3 ln d⌋ ≈ 10–15, each requiring N ≈ 20–100 simulator rollouts to average noise → on the order of 10⁴–10⁶ simulator rollouts per stance. Fully parallelisable over population.
- **Total budget:** M × (CMA-ES inner run) → roughly 10⁵–10⁷ simulator rollouts across the full menu. For a 20-quarter simulator, this is well within range of a multi-core workstation or a small cloud cluster over hours-to-days.
- **If simulator rollouts are expensive:** swap CMA-ES for Bayesian Optimisation with a GP surrogate, which typically cuts rollouts by 1–2 orders of magnitude at the cost of more per-iteration bookkeeping.

### Known limitations for this problem
- **Policy class restriction.** CMA-ES searches over a parameterised policy family; if the true best policy lies outside that family, the search can only find the best *within* it. Mitigation: start with a simple interpretable class (share vector + a small number of backlog-priority coefficients), and only enrich if validation shows persistent gaps. If an unrestricted policy class is ever needed, upgrade to welfare-aware MORL (Option 2 in research findings).
- **Simulator fidelity is the ceiling.** Every result is conditioned on the simulator being right. The user stated the board trusts it "for scenario comparison" — this is fine for relative ranking of menu entries, which is what matters for a board-facing curated menu, but less reliable for absolute outcome forecasts. Mitigation: report relative differences between menu entries, not absolute outcome forecasts; run a historical back-test of the simulator against the nine years of operational data to calibrate confidence.
- **Per-capita vs raw group outcomes.** The "balanced/proportional" stance requires a normalisation choice (per-capita within each group vs raw placements). This is a modelling decision that must be surfaced to the board, not hidden inside the optimiser.
- **Stance-menu redundancy risk.** Two α values may produce policies with nearly identical outcome trajectories, which wastes a menu slot. Mitigation: after generating the full ladder, apply a redundancy filter (drop any menu entry whose group-outcome trajectory is within ε of a neighbour's), and re-run with a tighter ladder if needed — this is standard practice in representative-subset-of-Pareto-front literature.
- **Stochastic evaluation noise.** Simulator noise can mislead CMA-ES if N (rollouts per evaluation) is too small. Mitigation: use common random numbers across candidates within a generation to reduce variance, and tune N with a preliminary noise-calibration run.

## Why not the alternatives

| Alternative | Reason not selected |
|---|---|
| Welfare-aware MORL (end-to-end, e.g. p-mean Q-learning or Pareto Set Learning) | Trains a black-box neural policy, which is harder for a 3-person data team to set up in 8 months and harder for the board to audit; the scalarisation + CMA-ES route gives the same structural output (a stance-indexed menu of near-Pareto policies) with an interpretable policy class. MORL becomes the right upgrade once the interpretable class is shown to be binding. |
| NSGA-III (reference-direction evolutionary multi-objective) | Well-matched to "small curated menu" because it uses reference directions, and can wrap the simulator directly. But it is sample-hungrier than α-fair-scalarisation + CMA-ES, offers no theoretical guarantee of Pareto efficiency, and produces menu entries that map less cleanly to the three named ethical stances — each NSGA-III output is a Pareto point that must be *interpreted* into a stance post-hoc, rather than *selected* by an explicit stance a priori. A reasonable Plan B if the α-fair mapping is ever contested. |
| Pure ε-constraint without scalarisation (AUGMECON2 inside the simulator loop) | AUGMECON2 is designed for MOIP, not for simulator-evaluated policy search. It can be used for sanity-check runs on a simplified IP approximation of a single-year allocation, but cannot serve as the primary method for the 20-quarter state-dependent policy problem. |
| Plain weighted-sum linear scalarisation | Cannot reach the non-convex parts of the Pareto frontier; cannot express max-min (Rawlsian) preferences. The user explicitly has a Rawlsian stance on the menu, so linear weights would miss exactly the menu entry the board most cares about. α-fair is the minimum viable scalarisation family here. |
| Simulation alone (Monte Carlo evaluation of a handful of hand-crafted strategies) | Does not *search* for near-optimal strategies — it only scores the strategies you feed it. The user explicitly wants "the best possible strategy *if* a particular balance is the one the board chooses," which is an optimisation problem, not a pure evaluation problem. |

## What the organisation needs before starting

- **Data to collect (most likely already available but to confirm):**
  - Per-group caseworker-hour cost per placement (h_g).
  - Per-group, per-sub-programme historical placement success rate (for simulator calibration).
  - A documented interface to the simulator: input = policy object / decision rule; output = trajectory of group-level outcomes over 20 quarters; ideally supporting seeded Monte-Carlo rollouts.
  - Statutory or policy floors on any group's allocation, if any — these become hard constraints imposed on every policy in the menu independent of stance.
  - Per-capita denominators for each group (intake volume, waitlist size) if the "balanced" stance is to be per-capita rather than raw.
- **Skills required:**
  - Python at the level of the existing data team: numpy, pandas, a black-box optimiser package (e.g. `cma`, `pymoo`, or `scikit-optimize`).
  - Familiarity with the commissioned simulator's API (already in-house).
  - Basic grasp of multi-objective concepts (Pareto efficiency, scalarisation) — one week of internal study with the references in section 04 is sufficient for a team with some simulation experience.
  - No need for deep-RL engineering, GPU infrastructure, or neural-network training expertise at this stage.
- **Estimated effort:**
  - Problem formulation and policy class design: 3–4 weeks.
  - Simulator-API integration and smoke tests: 2–3 weeks.
  - Inner-loop solver setup (CMA-ES) and noise calibration: 2–3 weeks.
  - Full-menu generation runs and tuning: 3–4 weeks.
  - Validation, back-testing, and redundancy-filter tuning: 3–4 weeks.
  - Board-facing visualisation and documentation: 3–4 weeks.
  - **Total:** comfortable within the 8-month engagement window, with a working end-to-end prototype by month 3–4 and a polished board-ready menu by month 6–8.
