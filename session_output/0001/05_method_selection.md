# Method Selection — Session 0001

## Selected approach

**Primary method: Maximum Coverage Location Problem (MCLP) as Binary Integer Program**
- Solved exactly using spopt `MCLP.from_geodataframe()` with CBC or Gurobi solver
- Demand weights w_j derived from kernel density estimation on elephant GPS tracks
- Coverage radius r calibrated from camera hardware spec and terrain data

**Uncertainty extension: Sample Average Approximation (SAA)**
- Draw S = 30–50 scenarios by sampling different time windows from the GPS dataset (wet season, dry season, year-round)
- Solve each scenario as a deterministic MCLP
- Select the camera placement that appears most frequently across scenarios (consensus solution)
- This handles the fact that elephants move differently by season without requiring a full stochastic MIP

**Validation baseline: Lazy Greedy (submodlib)**
- Run lazy greedy submodular maximisation as a fast sanity check
- Guaranteed to return ≥ 63.2% of the optimal objective
- If MCLP exact solution and greedy solution agree closely, confidence in result is high

## Why this combination

| Criterion | Assessment |
|---|---|
| Problem scale | ≤ 20 cameras, likely ≤ 10,000 candidate sites — exact BIP is tractable (seconds) |
| Data quality | GPS tracking data is good quality — can construct reliable demand weights |
| Seasonal variation | Elephants move; SAA handles this without full stochastic MIP complexity |
| Capacity | Requires GIS skills and Python; no advanced OR software licence needed |
| Interpretability | Binary placements are explainable (camera here: yes/no) |

## Rejected alternatives

| Method | Reason rejected |
|---|---|
| Benders decomposition | Overkill — problem is small enough for direct BIP with CBC |
| Full stochastic MIP (Marín et al.) | More complex than needed; SAA achieves near-equivalent results |
| FANTOM / Repeated Greedy | Stronger guarantee than needed; Stochastic Greedy or exact BIP preferred |
| Dynamic MCLP (multi-period) | Would require re-solving seasonally; one-shot placement with SAA is simpler first step |
| Gaussian Process sensor placement (Krause et al. 2008) | Best for continuous monitoring with sensor fusion; more complex than required here |
