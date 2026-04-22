# Research Findings — Session 0001

## 1. State-of-the-art MCLP algorithms

### Exact methods
- **Branch-and-Benders-Cut** — Cordeau, Furini & Ljubic (2019), EJOR. Solves instances up to 200,000 demand points; achieves proven optimality on 95.93% of benchmarks. Current gold standard for exact MCLP.
- **Accelerated Benders Decomposition + Local Branching** — Janssens et al. (2023), EJOR. First exact method proven to handle large-scale multi-period (dynamic) MCLP. arXiv:2309.00702.
- **Dynamic Programming with Coverage Dominance Pruning** — arXiv:2509.23334 (2025). On a real-world case (1,247 demand points, 312 candidates), solved in 127 seconds vs CPLEX at 1,847 seconds. Achieves 2.6–5.4% better solutions than greedy.

### Heuristic / approximation methods
| Algorithm | Guarantee | Complexity | Reference |
|---|---|---|---|
| Greedy | 1 − 1/e ≈ 0.632 | O(nk) oracle calls | Nemhauser, Wolsey & Fisher (1978), Math. Programming |
| Lazy Greedy | 1 − 1/e (same) | Much faster in practice | Minoux (1978); Leskovec et al. KDD 2007 |
| Stochastic Greedy | 1 − 1/e − ε (expected) | O(n log(1/ε)) — linear in n | Mirzasoleiman et al., AAAI 2015 |
| FANTOM / Repeated Greedy | (1 + O(1/√k))^k | O(nr√k) | Feldman, Naor & Schwartz, COLT 2017 |

The MCLP coverage objective is a canonical monotone submodular function — all (1 − 1/e) guarantees apply directly.

---

## 2. Wildlife camera trap placement literature

- **Jimenez et al. (2021)**, Scientific Reports: feature-targeted vs. systematic random grid camera placement. Two-stage design recommended: first optimise spatial coverage (MCLP-like), then target habitat features.
- **Wilton et al. (2025)**, Journal of Applied Ecology: hierarchical coverage optimisation in practice for multi-species surveys in South Africa — first stage structurally equivalent to MCLP.
- **Moeller et al. (2023)**, Environmental Monitoring and Assessment: framework for detection probability as a function of distance, height, and camera model — usable to calibrate the coverage radius r in the MCLP.
- **Krause, Singh & Guestrin (2008)**, JMLR Vol. 9: Near-Optimal Sensor Placements in Gaussian Processes. **Most technically sophisticated framing for this exact problem** — proves mutual information maximisation is NP-complete, gives (1 − 1/e) lazy greedy approximation. Directly applicable when elephant GPS tracks are modelled as a spatial Gaussian process.

---

## 3. Probabilistic / stochastic coverage extensions

- **Stochastic MCLP with Two-Stage Recourse** — Marín et al. (2024), arXiv:2403.07785. Lagrangian relaxation + subgradient for scenarios with uncertain elephant locations.
- **Sample Average Approximation (SAA)** — Kleywegt, Shapiro & Homem-de-Mello (2002), SIAM. Draw 30–100 scenarios from GPS data, solve each as deterministic MCLP, aggregate. Near-optimal with standard MIP solvers.
- **Minimax Regret Robust MCLP** — Caserta et al. (2022), Computational Optimization and Applications. Minimises worst-case regret — suitable if elephant movement scenarios cannot be probabilistically weighted.
- **Dynamic MCLP with Simulated Annealing** — for seasonal re-optimisation. Handles time-varying demand up to 2,500 demand nodes and 200 candidate facilities.

---

## 4. Software

| Tool | Language | Role | Cost |
|---|---|---|---|
| **spopt** (PySAL) | Python | Native MCLP.from_geodataframe(); GeoPandas integration | Free |
| **PuLP** | Python | MIP modelling layer; calls CBC/Gurobi/HiGHS | Free |
| **Google OR-Tools** | Python | CP-SAT solver; very fast for binary IPs at scale | Free |
| **Gurobi** | Python/R | Fastest commercial MIP solver | Free academic licence |
| **submodlib** | Python | Greedy/Lazy Greedy/Stochastic Greedy for coverage | Free |
| **maxcovr** | R | Exact MCLP/LSCP in spatial workflow | Free (CRAN) |

**For this problem (20 cameras, ≤ 10,000 candidate sites):** CBC (free) via spopt is sufficient — seconds to low minutes. Gurobi needed only if candidate sites exceed 100,000.
