# Formal Mathematical Specification — Session 0001

## Problem class
Maximum Weighted Coverage Location Problem (MCLP) — spatial sensor placement variant

---

## Sets and indices

| Symbol | Definition |
|---|---|
| L | Set of candidate camera locations i (grid cells or pre-screened sites across the park) |
| J | Set of spatial units j (grid cells covering the park area) |
| K = 20 | Maximum number of cameras (budget) |

---

## Parameters

| Symbol | Definition | Source |
|---|---|---|
| w_j | Weight of spatial unit j — elephant presence frequency or time spent | Elephant GPS tracking data (kernel density estimation over GPS points) |
| a_ij ∈ {0,1} | Coverage indicator: 1 if camera at location i can detect events at unit j, 0 otherwise | Defined by detection radius r and line-of-sight (terrain/vegetation data) |
| r | Detection radius of a single camera (metres) | Camera hardware spec |

---

## Decision variables

| Symbol | Type | Definition |
|---|---|---|
| x_i | Binary ∈ {0,1} | 1 if a camera is placed at candidate location i, 0 otherwise |
| y_j | Binary ∈ {0,1} | 1 if spatial unit j is covered by at least one camera, 0 otherwise |

---

## Objective function

**Maximise** total weighted coverage of elephant movement:

```
maximise  Σ_{j ∈ J}  w_j · y_j
```

---

## Constraints

```
(1)  y_j  ≤  Σ_{i ∈ L}  a_ij · x_i       ∀ j ∈ J     [a unit is covered only if a camera covers it]

(2)  Σ_{i ∈ L}  x_i  ≤  K                              [camera budget: at most 20 cameras]

(3)  x_i ∈ {0,1}                           ∀ i ∈ L     [camera placement is binary]

(4)  y_j ∈ {0,1}                           ∀ j ∈ J     [coverage is binary]
```

---

## Interpretation

The model asks: *"Given 20 cameras, which locations should they be placed in to maximise the total weighted area of elephant habitat that is detectable?"*

- **w_j** encodes where elephants actually spend time — areas with high GPS density get high weight, so cameras are pulled toward high-traffic elephant corridors and watering holes
- **a_ij** encodes physical reachability — a camera can only detect what it can see (within range and not blocked by terrain or dense vegetation)
- Constraint (1) links the y (coverage) variables to actual placement decisions
- Constraint (2) enforces the 20-camera budget

---

## Extensions (for downstream consideration)

- **Probabilistic coverage**: Replace binary a_ij with a decay function p_ij = f(distance, terrain) to capture partial detection probability at range
- **Threat weighting**: Multiply w_j by a poaching risk score derived from historical incident data, shifting cameras toward high-elephant + high-threat overlap zones
- **Temporal variation**: If GPS data has timestamps, build seasonal movement models and solve for coverage that is robust across seasons
