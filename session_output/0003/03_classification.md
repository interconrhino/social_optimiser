# Optimization Category Classification

**Session:** 0003

## Primary Match

**Technique:** Influence Maximisation (POMDP) — *used here as the catalog's sequential-decision / POMDP entry; the classical "influence spread on a network" framing does not apply directly, but the POMDP / sequential per-round selection backbone does.*
**Catalog ID:** influence_maximisation
**Confidence:** Medium

**Matching signals:**
- **Sequential rounds with a per-round selection budget.** The formal spec has 52 weekly rounds; each round, exactly K = 40 individuals are selected from a pool of ~800. The catalog's POMDP entry is the only one that explicitly models multi-round, fixed-K-per-round selection. (Spec §Decision Variables, Constraints #1, #3 → Catalog signal "Sequential interventions where you can observe and update after each round".)
- **Partial observability / uncertainty updated over time.** A family's trajectory through {Stable, At-risk, Crisis} is stochastic; state is fully observed only during a visit. Decisions must respect non-anticipativity. The POMDP framing natively represents this. (Spec §Uncertainty → Catalog signal "Network structure is uncertain or only partially known" — here, it is *family state*, not network structure, that is uncertain; the POMDP backbone still fits.)
- **Selection of K individuals per round, K << |F|.** 40 of ~800 per week. (Catalog signal "Selecting participants for … interventions".)
- **Estimated transition model driving dynamics.** The per-family state-transition kernel P(s_{i,t+1} | s_{i,t}, x_{i,t}, φ_i) is estimated from historical data — analogous to the catalog entry's "propagation probability per edge" but on a per-individual 3-state dynamics model.

**Why this fits:**
The structural backbone of the problem — **pick K items from N at each of T rounds under a Markovian per-item stochastic process, observe outcomes, update, repeat** — is exactly what the POMDP entry is for. The catalog's headline framing talks about *social-network influence spread*, which does **not** apply here (families are treated as independent arms, not as nodes in a contagion network). So the fit is structural, not thematic.

**Contraindications checked:**
- "No social network structure — the population is disconnected individuals." **This partially applies** — Riverbank's 800 families are effectively independent arms, not a network. However, nothing in the classical POMDP / restless-bandit formulation requires a network; the network assumption is specific to influence-maximisation problems. The underlying POMDP machinery (state, action, observation, reward, policy) works without a network and is the natural home for this problem. → *Noted; does not eliminate the match.*
- "Intervention is one-shot with no sequential rounds." **Does not apply** — we have 52 sequential weekly rounds.
- "Network is fully known with certainty." **Does not apply** — family dynamics are uncertain.

## Alternative 1

**Technique:** Integer Programming
**Catalog ID:** integer_programming
**When this would be preferred instead:** If the user were willing to collapse the problem to a static, one-shot allocation (e.g. "rank families and visit the top 40 this week, re-rank next week") with no explicit look-ahead over the 52-week horizon, the weekly decision becomes a pure combinatorial selection with a cardinality constraint and can be solved as an IP. This would be simpler but would discard the sequential-planning value — exactly the shortcoming the user has already flagged in their status-quo process.

## Alternative 2

**Technique:** Simulation (Monte Carlo / Agent-Based)
**Catalog ID:** simulation
**When this would be preferred instead:** Simulation is the right tool for **evaluating** candidate policies (including the recommended one) against thousands of synthetic cohort trajectories, testing sensitivity to the crisis-weight w, to the transition model, and to equity floors. It is not, on its own, a decision-making method — but it is a natural companion to the primary match, used to validate and stress-test the scheduler before rollout. I recommend treating it as a **validation tool** bundled with the recommendation rather than as the primary technique.

## Why alternatives were not the primary pick

Integer Programming alone ignores the sequential, stochastic structure of the problem — the user was emphatic that the schedule must work across the full 52-week year and anticipate how a visit today shapes the probability that a family is in crisis three months from now. A pure IP treats each week as an independent snapshot and cannot credit "prevent a future crisis" in the weekly ranking.

Simulation is the right tool for evaluation but cannot itself produce an optimal policy. It tells you how a given policy performs, not which policy is best.

The POMDP / sequential-decision entry — while catalog-framed as "influence maximisation" — is the only entry that captures the full structure (multi-round, K-of-N, stochastic per-individual state dynamics, estimation from history, learning policy). The downstream method-research stage should search for the specific **sub-family of sequential-decision methods for K-of-N selection with independent Markovian items under a per-round budget constraint**, which is a well-studied structure in operations research / ML and has specialised algorithms that are substantially more tractable than solving a naive POMDP on a state space of size 3^800.

### Catalog-fit caveat (self-flag)

The catalog's eight entries are somewhat biased toward static allocation and toward social-network influence specifically; none of them is a clean named match for *restless, budgeted, sequential selection over independent Markov arms* (a problem class with a well-known name in OR that I will not pre-empt here — that's the method-research stage's job). I've mapped it to the POMDP entry because that entry shares the most structural machinery, and I've flagged the caveat rather than force-fit.
