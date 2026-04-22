# Technique Classification — Session 0001

## Catalog match

**Primary match: Integer Programming (Binary / Combinatorial)**
- Catalog ID: `integer_programming`
- Match strength: Strong
- Matching signals:
  - Placement decisions are binary (place camera here: yes/no) ✓
  - Selecting which subset of locations to use from a larger candidate set ✓
  - Fixed budget constraint (≤ 20 cameras) ✓
  - Facility location analogy: camera sites ≈ "where to open distribution hubs" ✓

**Specific problem class: Maximum Coverage Location Problem (MCLP)**
- MCLP is a canonical integer programming formulation (Church & ReVelle, 1974)
- Directly models: select K facilities to maximise weighted population covered within radius r
- Here: facilities = cameras, population = elephant GPS locations, radius = camera detection range

## Why not other catalog entries

| Technique | Reason not primary |
|---|---|
| Linear Programming | Placement decisions are binary, not continuous — LP relaxation would give fractional placements |
| Network / Routing | No movement or routing involved — purely a location selection problem |
| Matching | No pairing between two populations — single-sided selection problem |
| Influence Maximisation | No social network; spread dynamics not relevant |
| Simulation | Could supplement (e.g., test robustness of placement across seasonal elephant movement) but not the primary method |
| Multi-objective | Could extend if poaching risk is added as a second objective, but not required at baseline |

## Technique for downstream research (Skill 4)

Search focus:
- Maximum Coverage Location Problem (MCLP) algorithms — exact and heuristic
- Wildlife camera trap placement optimisation (ecology literature)
- Sensor placement under spatial uncertainty / probabilistic coverage
- Conservation planning spatial optimisation (Marxan, Zonation as field references)
- State-of-the-art: submodular maximisation methods for coverage (greedy guarantees)
