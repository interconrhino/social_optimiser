# Optimization Category Classification

**Session:** 0006

## Primary Match
**Technique:** Multi-objective Optimisation
**Catalog ID:** `multiobjective_optimisation`
**Confidence:** High

**Matching signals:**
- **Two or more objectives that cannot all be maximised simultaneously** → the board explicitly surfaces three stances (totals / worst-off / balanced) that lead to materially different strategies. This is a textbook multi-objective structure.
- **Need to explicitly explore the trade-off between cost and impact** → here the trade-off is between total placements, worst-off-group outcome, and inter-group balance. Four group-level outcome trajectories are the axes.
- **Equity or fairness is a stated goal alongside efficiency** → "protect the worst-off group" vs "maximise totals" is exactly an equity-vs-efficiency axis.
- **Stakeholders disagree on which objective matters most** → the board has three factions, and the implicit weighting shifts with a new board chair or government.
- **Decision-makers want to see a range of options, not just one answer** → the explicit deliverable is a *small curated menu* of 3–10 candidate strategies, each tied to a specific stance. The user explicitly distinguished this from dumping a full Pareto frontier — they want a curated sparse cover.

**Why this fits:**
The user has already done the structural diagnosis for us: they are not asking "what is the single best five-year strategy?" — they are asking "for each defensible ethical stance on balancing four group outcomes, what is the best strategy, and can we present a small menu of them?" That is precisely the problem that multi-objective optimisation is designed to solve. The three named stances (utilitarian totals, Rawlsian worst-off, egalitarian balance) map cleanly onto well-studied scalarisation families (α-fair / CES social welfare functions), which means the menu axis is low-dimensional and principled. The deliverable format — small curated menu each tied to an interpretable stance — also matches the "preference-articulated" / scalarisation flavour of multi-objective methods rather than pure a-posteriori Pareto-frontier dumping.

**Contraindications checked:**
- *"Only one objective matters — use LP or IP instead"* → Does NOT apply. The user explicitly has multiple conflicting objectives (four group-level outcomes, three stances for weighting them).
- *"Objectives can be combined into a single weighted score with agreed weights — use LP with a composite objective"* → Does NOT apply. The user explicitly states there is no agreed weighting; the weighting changes with political leadership and is itself the variable the board wants to explore.

## Alternative 1
**Technique:** Simulation (Monte Carlo / Agent-Based)
**Catalog ID:** `simulation`
**When this would be preferred instead:** If the user only wanted to evaluate a handful of pre-proposed strategies rather than search for optimal ones — i.e. if they already had the menu and just needed group-level outcome projections. Here they want *optimal strategies per stance*, not just evaluation of given strategies, so simulation is a component (the evaluator inside the optimisation loop) rather than the headline method.

## Alternative 2
**Technique:** Integer Programming
**Catalog ID:** `integer_programming`
**When this would be preferred instead:** If the problem were a single-stance, single-quarter (or open-loop multi-quarter) allocation with a single scalar objective and closed-form constraint structure — no stochastic state dynamics, no simulator, no stance menu. A stance-scalarised version of the present problem has an IP-like inner skeleton, but the overall structure is dominated by (a) the multi-stance menu requirement and (b) the simulator-in-the-loop sequential dynamics, both of which push past plain IP.

## Why alternatives were not the primary pick

Simulation is the right tool for *evaluating* a policy's group-level outcome trajectory over 20 quarters given stochastic intake, employer dynamics, and pipeline carry-over — and indeed the commissioned simulator will play exactly that role inside the pipeline. But simulation alone does not produce a curated menu of near-optimal strategies across a stance spectrum; it only scores strategies you give it. The user's deliverable is explicitly a *menu of best-per-stance strategies*, which requires a search/optimisation layer on top of the simulator.

Integer programming would be the right primary match if the problem were a single-quarter or open-loop multi-quarter allocation with one scalar objective. Here the dominant structural features are (i) multiple conflicting group-level objectives and an explicit request for a stance-indexed menu, and (ii) stochastic, state-dependent sequential dynamics evaluated by a black-box simulator. Both push beyond plain IP: the first calls for multi-objective / scalarisation methods, and the second calls for policy search against a simulator rather than closed-form solve. Multi-objective optimisation — specifically a scalarisation-based variant aligned to a principled family of social welfare functions — is the right frame, with the inner per-stance solve handled by simulation-based policy search (and if the policy class is made simple enough, possibly as an IP or stochastic program inside each scalarisation).
