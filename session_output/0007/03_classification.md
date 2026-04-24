# Optimization Category Classification

**Session:** 0007

## Primary Match
**Technique:** Influence Maximisation (POMDP) — used here in its *non-network*, partially-observable sequential resource-allocation sense.
**Catalog ID:** `influence_maximisation`
**Confidence:** Medium

**Matching signals:**
- **Sequential rounds with observation between rounds** → catalog signal: *"Sequential interventions where you can observe and update after each round"*. The organisation runs 6–8 monthly rounds; after each month they see who listened and re-plan.
- **Partial observability of the decision target** → catalog signal: *"Network structure is uncertain or only partially known"* — structurally analogous here, because each farmer has a **latent engagement state** that is only indirectly observed through monthly listen events.
- **Budget-constrained selection from a population each round** → the POMDP framing explicitly plans across T rounds with K selections per round. This is an exact fit to "pick 400 of 28,000 each month for 8 months".
- **Goal of maximising cumulative engagement across the window**, not a one-shot decision → aligns with sequential POMDP planning horizons.

**Why this fits:**
The problem is fundamentally a sequential decision under partial observability: each month the planner selects a budgeted subset of units (farmers), observes stochastic outcomes, and must trade off *exploration* (calling farmers whose state is uncertain) against *exploitation* (calling farmers most likely to benefit right now). A one-shot integer-programming framing would ignore the fact that information arrives between months and that the value of a call depends on the farmer's evolving state. The sequential-decision framing is what makes the method category match.

**Contraindications checked:**
- *"No social network structure — the population is disconnected individuals"* → **APPLIES partially.** The original catalog entry is motivated by peer-influence spread, which this problem does **not** have: calls do not propagate through a social network. **This is the reason confidence is Medium, not High, and the reason we flag Integer Programming as a credible alternative framing.** The sequential/partial-observability *structure* of the catalog entry still fits, but the *network* rationale does not; the research step must therefore look at restless / partially observable sequential selection methods that target *independent* units rather than networked influence spread.
- *"Intervention is one-shot with no sequential rounds"* → **Does not apply.** We have 6–8 rounds.
- *"Network is fully known with certainty — simpler greedy methods may suffice"* → **Does not apply** (and is the wrong failure mode for this problem).

## Alternative 1
**Technique:** Integer Programming
**Catalog ID:** `integer_programming`
**When this would be preferred instead:** If the organisation is willing to treat each month as an independent one-shot selection problem — e.g., score each farmer this month, pick the top-400 subject to equity floors — and accept that the model is not reasoning about information arriving between rounds. This is the natural "scoring rule + knapsack" framing and gives the organisation a fully explainable monthly artefact at the cost of not planning ahead.

## Alternative 2
**Technique:** Simulation (Monte Carlo / Agent-Based)
**Catalog ID:** `simulation`
**When this would be preferred instead:** To stress-test a proposed monthly-selection rule under different assumptions about engagement-state dynamics and call-effect sizes **before** committing to the pilot. Simulation is a validation companion here, not a replacement — it does not produce the monthly 400-farmer list itself, but it is strongly suggested for evaluating candidate policies on historical data via off-policy evaluation (given the observational-data caveat the user raised).

## Why alternatives were not the primary pick
Integer Programming alone does not capture the sequential-information structure or the latent engagement state — both of which the user described as central (farmers "drift away", early warning signs, month-to-month dynamics). Simulation is a validation tool, not a planning tool: it answers "how well does rule X perform under these assumptions?" but does not itself produce the rule. The sequential-under-partial-observability framing captured by the POMDP entry — minus the network-spread rationale — is the one that matches all the user's structural signals (budget-per-round, 6–8 rounds, latent state, observation between rounds, cumulative-over-window objective). The method-research step will refine this into a concrete algorithm class suited to *independent-unit*, restless-state sequential allocation.
