# Optimization Category Classification

**Session:** 0002

## Primary Match

**Technique:** Integer Programming
**Catalog ID:** `integer_programming`
**Confidence:** **Medium — see important caveat below**

**Matching signals (from the formal spec):**
- Decision variables are **binary** (visit / don't visit) — matches the catalog's "Binary or integer quantity decisions" signal.
- The core weekly decision is **selecting which subset of entities** (which 40 of 800 families) to act on — matches "Choosing which subset of locations, projects, or programmes to fund or open".
- Hard capacity constraint (40 visits per week) is a canonical budget constraint on a binary selection — matches "Fixed budget or capacity constraint".
- Social example in the catalog is a close analogue: "A microfinance institution selecting which 20 of 80 loan applicants to fund" — identical structure at a per-week slice.

**Why this fits:**
At any single week, the organisation's decision problem is a classic binary selection under a budget constraint: pick 40 out of 800 families, each with an estimated value-of-visit, to maximise expected weekly welfare. Integer Programming is the correct framework for that per-week slice.

**Contraindications checked:**
- *"All decisions are continuous proportions — use Linear Programming instead"* → does not apply; decisions are genuinely binary.
- *"The number of possible combinations is astronomically large without clear structure"* → partially applies in the naive formulation (choose 40 of 800 has ~10⁵⁶ combinations per week, and 52 sequential weeks explodes this), but the structure is clean enough that standard IP solvers or decomposition methods handle the per-week subproblem trivially.

---

## Important caveat: structural gap in the catalog

The formal spec has a feature that **no catalog entry directly represents**: the weekly decision is not independent — it is **sequential across a 52-week horizon**, and each family's status evolves as a **Markov process whose transition probabilities are unknown a priori and must be estimated from historical trajectory data collected under a non-random past policy**.

Of the 8 catalog entries:
- Integer Programming (the primary pick) handles the per-week selection but treats each week independently, missing the temporal coupling.
- Influence Maximisation (POMDP) is the only entry whose methodology explicitly handles sequential decisions with partial observability — but it is contraindicated for this problem (no social-network structure among the families; no information-cascade dynamic).
- Simulation can model the uncertainty but is not itself a decision procedure.

The closest complete framework — **resource-allocation Markov Decision Processes / restless bandits** — is not represented in the catalog. The pipeline's downstream skills (`method-research`, `method-selection`, `recommender`) will need to search beyond the catalog to reach the right algorithmic family.

I am flagging this rather than forcing a worse match because the honest classification is: "the per-week structure is Integer Programming, but the full temporal structure requires a sequential-decision framework the catalog does not enumerate".

---

## Alternative 1

**Technique:** Simulation (Monte Carlo / Agent-Based)
**Catalog ID:** `simulation`
**When this would be preferred instead:**
If the organisation's goal were *stress-testing* a proposed weekly policy against the uncertainty in transition dynamics — rather than *computing* a policy — Simulation would be primary. In the actual pipeline, Simulation will likely appear as a **complementary** tool (importance-sampling-based policy evaluation against historical trajectories) rather than as the decision procedure itself.

## Alternative 2

**Technique:** Constraint Satisfaction / Scheduling
**Catalog ID:** `constraint_satisfaction`
**When this would be preferred instead:**
If the soft operational constraints (caseworker-to-region assignment, language matching, relationship continuity) were promoted to hard rules, a scheduling formulation would be needed to make feasible weekly visit sets. In practice this is a second-stage problem (CSP on top of IP), not the primary one.

---

## Why alternatives were not the primary pick

- **Simulation** is a scenario-exploration framework, not a decision procedure. It cannot by itself answer "who should the 40 of us visit this week?" — it can only tell us "if we follow policy π, here is what might happen". The primary problem is prescriptive, not descriptive.
- **Constraint Satisfaction** captures the secondary scheduling sub-problem (matching available caseworkers to the chosen families, respecting language/geography) but is not the primary decision that determines welfare — the selection of which 40 families matters far more than which caseworker visits them.
- **Matching** and **Network/Routing** do not fit: no pairing-with-preferences structure and no routing between locations as the primary decision.
- **Linear Programming** is contraindicated by the binary decision variables.
- **Multi-objective Optimisation** does not apply: the director gave a single scalar welfare metric.
- **Influence Maximisation (POMDP)** is contraindicated by the absence of a social-network structure among families.

---

## Note for downstream skills (method-research, method-selection)

The downstream stages should be directed to search specifically for:
- **Restless Multi-Armed Bandits (RMAB)** and approximate index policies (Whittle index)
- **Sequential resource allocation under unknown Markov dynamics**
- **Off-policy evaluation and learning from observational trajectories with behavioural-policy selection bias**
- **Decision-focused / end-to-end learning** approaches that train predictive models against downstream decision quality rather than predictive accuracy

These are NOT in the catalog, but they are the correct algorithmic family for the formal spec produced by skill 2. The classification gap documented above is the reason this guidance is explicit here rather than being inferred from the catalog match.
