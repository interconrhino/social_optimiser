# Full Recommendation — Session 0001
## Optimal Camera Trap Placement for Elephant Movement Detection

---

## 1. Plain-language summary

You have 20 cameras and a national park full of elephants. The challenge is that elephants don't spread evenly across the park — they have favourite corridors, watering holes, and seasonal routes. Placing cameras without this knowledge risks wasting most of them in areas elephants rarely visit. This recommendation uses a mathematical method called **Maximum Coverage Location** to analyse your elephant GPS data and park terrain together, and calculate exactly which 20 locations would put cameras in front of the most elephant activity. The method guarantees you are getting the best possible 20-camera coverage, not just a reasonable guess — and it accounts for the fact that elephants move differently in different seasons.

---

## 2. Formal problem formulation

### Sets
| Symbol | Definition |
|---|---|
| L | Set of candidate camera locations i (all physically accessible grid cells in the park) |
| J | Set of spatial demand units j (grid cells covering the park, e.g., 500 m × 500 m) |
| K = 20 | Camera budget (hard constraint) |

### Parameters
| Symbol | Type | Bounds | Definition | Data source |
|---|---|---|---|---|
| w_j | Continuous | ≥ 0 | Elephant presence weight at unit j (GPS visit frequency or kernel density estimate) | Elephant GPS tracking data — kernel density estimated at each grid centroid |
| a_ij | Binary | {0,1} | Coverage indicator: 1 if a camera at location i can detect events at unit j | Defined by detection radius r and line-of-sight derived from terrain/canopy data |
| r | Continuous | > 0 (metres) | Camera detection radius | Camera hardware specification; calibrated with Moeller et al. (2023) framework |

### Decision variables
| Symbol | Type | Bounds | Definition |
|---|---|---|---|
| x_i | Binary | {0,1} | 1 if a camera is placed at candidate location i ∈ L |
| y_j | Binary | {0,1} | 1 if spatial unit j ∈ J is covered by at least one placed camera |

### Objective function

**Maximise** total weighted elephant coverage:

```
maximise  Σ_{j ∈ J}  w_j · y_j
```

### Constraints

```
(1)  y_j  ≤  Σ_{i ∈ L}  a_ij · x_i        ∀ j ∈ J   [coverage requires a camera to cover the unit]
(2)  Σ_{i ∈ L}  x_i  ≤  K = 20                       [budget: at most 20 cameras]
(3)  x_i  ∈  {0,1}                          ∀ i ∈ L   [binary placement]
(4)  y_j  ∈  {0,1}                          ∀ j ∈ J   [binary coverage]
```

**Note on coverage model:** Constraint (1) is the standard set-covering linkage. The a_ij matrix encodes physical detectability — a camera at i covers unit j if and only if the distance d(i,j) ≤ r AND no major terrain obstruction breaks line-of-sight between i and j.

---

## 3. Algorithm specification

### Primary algorithm: Binary Integer Programming (BIP) — exact solver

**Algorithm class:** Mixed-Integer Linear Programming (MILP) / Binary Integer Program
**Problem class:** Maximum Coverage Location Problem (MCLP)
**Foundational reference:** Church, R. & ReVelle, C. (1974). *The maximal covering location problem.* Papers in Regional Science, 32(1), 101–118.
**Solver algorithm:** Branch-and-Bound with LP relaxation (CBC / Gurobi)

**Theoretical properties:**
- The MCLP is NP-hard in general; however, at the scale of this problem (≤ 20 cameras, ≤ 10,000 candidate sites) the BIP is routinely solved to **proven optimality** in seconds to low minutes by modern solvers
- The LP relaxation (treating x_i and y_j as continuous) is typically tight for MCLP instances, meaning branch-and-bound trees are shallow
- The solution returned by CBC or Gurobi is **provably optimal** — not an approximation

**Complexity:** NP-hard in the worst case; practically tractable at this scale due to strong LP relaxation bounds

---

### Uncertainty extension: Sample Average Approximation (SAA)

**Reference:** Kleywegt, A.J., Shapiro, A. & Homem-de-Mello, T. (2002). *The Sample Average Approximation Method for Stochastic Discrete Optimization.* SIAM Journal on Optimization, 12(2), 479–502.

**Purpose:** Elephant locations are not static — animals move seasonally. SAA treats this as a stochastic problem by sampling multiple plausible elephant movement scenarios from the GPS dataset and finding the camera placement that performs best across all of them.

**Procedure:**
1. Partition the GPS dataset into S = 30–50 scenario samples (e.g., by month, by season, or by random subsampling of 70% of GPS points per sample)
2. Compute a separate w_j demand vector for each scenario s: w_j^s = kernel density of GPS points in scenario s at grid cell j
3. Solve the deterministic MCLP for each scenario s → obtain S solutions {x^1, x^2, ..., x^S}
4. Compute the **consensus placement**: for each candidate site i, count how many scenarios include it (vote_i = Σ_s x_i^s). Select the K=20 sites with highest vote counts
5. Evaluate the consensus placement on each scenario to compute expected coverage

**Why SAA instead of full stochastic MIP:** For this problem scale, SAA achieves near-optimal expected coverage without requiring the full two-stage stochastic MIP formulation (Marín et al. 2024). The computational cost is simply S independent MCLP solves — trivially parallelisable.

---

### Validation baseline: Lazy Greedy Submodular Maximisation

**Reference:** Minoux, M. (1978). Accelerated greedy algorithms for maximizing submodular set functions. *Optimisation Techniques, Lecture Notes in Control and Information Sciences*, 7, 234–243. Implemented and popularised by Leskovec, J. et al. (2007). *Cost-effective Outbreak Detection in Networks.* KDD 2007.

**Theoretical guarantee:** Returns a solution with objective value ≥ (1 − 1/e) ≈ 63.2% of optimal. This bound is tight — no polynomial algorithm can do better unless P = NP (Feige, 1998).

**Purpose:** Run as a fast sanity check. If the BIP optimal solution and the lazy greedy solution agree on ≥ 15 of 20 camera sites, this provides high confidence the BIP solution is correct. If they diverge significantly, investigate whether the a_ij matrix is correctly constructed.

---

## 4. Implementation guidance

### Step 1: Data preparation

| Data input | Required format | Processing step |
|---|---|---|
| Park boundary | Shapefile / GeoJSON (polygon) | Use as spatial extent for grid generation |
| Elephant GPS tracks | CSV with columns: timestamp, latitude, longitude, animal_id | Compute kernel density estimate (KDE) over all points → raster of w_j values |
| Terrain / elevation | DEM raster (e.g., SRTM 30m) | Compute viewshed for each candidate site → line-of-sight constraints for a_ij |
| Vegetation / canopy | Land cover raster or canopy height model | Threshold dense canopy areas: set a_ij = 0 if canopy height > threshold between i and j |
| Past poaching incidents | CSV with latitude, longitude | Optional: construct a secondary threat weight layer to blend with w_j |
| Camera hardware spec | Datasheet | Extract maximum detection range r (metres) at target animal size |

**Key derived inputs:**
- **Demand grid:** Divide park into 500 m × 500 m grid cells. Each cell centroid is a demand unit j ∈ J. w_j = kernel density of GPS points in that cell (use scipy.stats.gaussian_kde or R's spatstat::density.ppp).
- **Candidate sites:** Initially use all accessible grid cells as candidate sites (L = J). Optionally pre-filter: remove cells with slope > 30° (inaccessible), inside water bodies, or with no feasible camera mounting point.
- **Coverage matrix a_ij:** For each (i,j) pair: a_ij = 1 if d(i,j) ≤ r AND line-of-sight is unobstructed (computed via terrain viewshed analysis). Use QGIS viewshed tool or Python's viewshed library.

### Step 2: Model implementation

**Recommended software:** Python with spopt (PySAL spatial optimisation module)

```python
# Install: pip install spopt geopandas pulp

import geopandas as gpd
from spopt.locate import MCLP

# Load data
demand_gdf = gpd.read_file("demand_grid.gpkg")          # columns: geometry, weight
facility_gdf = gpd.read_file("candidate_sites.gpkg")    # columns: geometry

# Build cost matrix (distance between each candidate and each demand point)
from spopt.locate.util import simulated_geo_points
cost_matrix = ...  # n_facilities × n_demand, precomputed Euclidean or network distance

# Formulate and solve MCLP
mclp = MCLP.from_cost_matrix(
    cost_matrix,
    weights=demand_gdf["weight"].values,
    service_radius=r,           # detection radius in metres (same units as cost matrix)
    p_facilities=20,            # camera budget
    solver="cbc"                # or "gurobi" for larger instances
)
mclp.solve()

# Extract solution
selected_sites = facility_gdf[mclp.fac2cli != []]       # camera locations
coverage_fraction = mclp.perc_served                     # % of weighted demand covered
```

**Alternative for full manual control (PuLP):**
```python
import pulp

prob = pulp.LpProblem("MCLP", pulp.LpMaximize)
x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in L}
y = {j: pulp.LpVariable(f"y_{j}", cat="Binary") for j in J}

prob += pulp.lpSum(w[j] * y[j] for j in J)                                  # objective
for j in J:
    prob += y[j] <= pulp.lpSum(a[i][j] * x[i] for i in L)                   # constraint (1)
prob += pulp.lpSum(x[i] for i in L) <= 20                                    # constraint (2)

prob.solve(pulp.PULP_CBC_CMD(msg=0))
```

### Step 3: Key parameters and calibration

| Parameter | Recommended starting value | Calibration advice |
|---|---|---|
| Grid resolution | 500 m × 500 m | If park < 500 km², use 250 m. Finer grids increase a_ij computation cost quadratically |
| Detection radius r | 30–50 m (camera trap standard) | Use manufacturer's claimed detection zone; validate with Moeller et al. (2023) calibration trials |
| KDE bandwidth h | Scott's rule (scipy default) or 2–5 km | Larger bandwidth smooths seasonal variation; smaller bandwidth captures hotspots. Tune by leave-one-out cross-validation on GPS points |
| Number of SAA scenarios S | 30–50 | Test stability: if consensus placement changes by < 2 sites when S increases from 30 to 50, S = 30 is sufficient |
| Line-of-sight threshold | Canopy height > 5 m blocks detection | Validate with one or two trial placements |

### Step 4: Computational considerations

- **Problem size estimate:** Park of 5,000 km² at 500 m grid → ~20,000 demand units, ~20,000 candidate sites. The a_ij matrix is 20,000 × 20,000 = 400 million entries — too large to store densely. Use **sparse matrix** representation: only store (i,j) pairs where d(i,j) ≤ r (typically ≤ 1–5% of all pairs for r = 50 m).
- **CBC solve time:** At this scale with sparse a_ij, expect < 5 minutes per solve on a standard laptop. For SAA with S = 30 scenarios: < 2.5 hours total (parallelise across CPU cores using Python's multiprocessing).
- **Memory:** Sparse a_ij with 5% fill and 20,000 × 20,000 dimensions: ~10 GB in dense float64. Use scipy.sparse.csr_matrix — reduces to ~500 MB.
- **Pre-filtering candidate sites:** Reducing |L| by 50% (removing inaccessible terrain) roughly halves solve time. Pre-filter aggressively.

---

## 5. Validation

### Primary evaluation metric
**Weighted coverage fraction:** Σ_{j covered} w_j / Σ_{j ∈ J} w_j

This measures what fraction of total elephant GPS activity falls within camera detection range. Target: > 60% weighted coverage (based on benchmarks from analogous ecological sensor placement studies).

### Baseline to beat
**Uniform random placement:** Place 20 cameras uniformly at random across accessible park area. Run 1,000 random trials, compute mean weighted coverage. The MCLP solution should exceed this baseline by ≥ 30 percentage points — if not, re-examine the a_ij matrix construction.

**Expert heuristic baseline:** Ask park rangers to nominate their 20 preferred camera sites based on local knowledge. Compare MCLP solution against ranger-selected sites. This also builds trust in the model — if MCLP agrees with experienced rangers on most sites and adds a few they didn't think of, the model is credible.

### Sensitivity analysis questions
1. **Coverage radius sensitivity:** How much does optimal weighted coverage change if r = 30 m vs. r = 50 m vs. r = 70 m? (Run MCLP for all three — if the solution is stable across r, the model is robust.)
2. **Seasonal robustness:** What is the worst-season coverage of the SAA consensus solution? (Compare consensus placement against per-season optimal placement — the gap tells you the cost of a fixed camera network.)
3. **Budget sensitivity:** What is the marginal coverage gain from cameras 15 → 16, 16 → 17, ..., 19 → 20? (Plot the coverage curve as K increases from 1 to 20 — this tells you if 20 cameras is the right number or if budget is better spent elsewhere.)
4. **Poaching integration:** Re-run MCLP with w_j multiplied by a threat score derived from historical poaching incident density. Compare with pure-GPS-weighted solution — the difference shows you which camera sites are "elephant hotspots" vs. "high-risk zones."

### Pilot approach
1. **Phase 1 (desk validation):** Run the model, produce a ranked list of 20 sites + a backup list of 10 alternative sites. Share with park rangers for face-validity review.
2. **Phase 2 (field survey):** Ground-truth the top 5 sites — visit each, confirm physical access and camera mounting feasibility. Adjust any infeasible sites using the backup list.
3. **Phase 3 (phased deployment):** Deploy 10 cameras first. After 3 months, compare actual elephant detection counts at each camera against model predictions. Calibrate KDE bandwidth and detection radius using observed data, re-run MCLP, deploy remaining 10 cameras informed by Phase 1 data.

---

## 6. Key references

1. **Church, R. & ReVelle, C. (1974).** The maximal covering location problem. *Papers in Regional Science*, 32(1), 101–118. *(Foundational MCLP formulation)*
2. **Nemhauser, G.L., Wolsey, L.A. & Fisher, M.L. (1978).** An analysis of approximations for maximizing submodular set functions. *Mathematical Programming*, 14, 265–294. *(1 − 1/e greedy guarantee)*
3. **Kleywegt, A.J., Shapiro, A. & Homem-de-Mello, T. (2002).** The sample average approximation method for stochastic discrete optimization. *SIAM Journal on Optimization*, 12(2), 479–502. *(SAA for seasonal uncertainty)*
4. **Krause, A., Singh, A. & Guestrin, C. (2008).** Near-optimal sensor placements in Gaussian processes. *JMLR*, 9, 235–284. *(Closest technical analogue — spatial sensor placement with submodular objective)*
5. **Cordeau, J.-F., Furini, F. & Ljubic, I. (2019).** Benders decomposition for very large scale partial set covering and maximal covering location problems. *EJOR*. *(State-of-the-art exact solver if scale increases)*
6. **Moeller, A.K. et al. (2023).** A simple framework for maximising camera trap detections using experimental trials. *Environmental Monitoring and Assessment*. *(Calibrating detection radius r)*
7. **Mirzasoleiman, B. et al. (2015).** Lazier than lazy greedy. *AAAI 2015*. *(Stochastic greedy — fast validation baseline)*
8. **spopt documentation:** https://pysal.org/spopt — MCLP.from_geodataframe() implementation
