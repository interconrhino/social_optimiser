# Problem Profile — Session 0001

## Raw problem statement
A nonprofit working in wildlife conservation wants to place new camera traps in a national park to monitor and protect elephants. They need to decide where to position up to 20 cameras across the park.

## Classification

| Axis | Assessment |
|---|---|
| End state defined? | Yes — maximise detection of elephant movement across the park |
| Activities defined? | Yes — place cameras at discrete locations within the park |
| **Classification** | **Technical** → proceed to pipeline |

**Technical sub-type:** Resource scarcity + Information flow
- 20 cameras is a finite, scarce resource relative to the park area
- Cameras are information-gathering instruments — the problem is about maximising coverage of elephant movement information

**Closest OR analogy:** Maximum coverage facility location / sensor placement optimisation

## Problem Profile

| Field | Detail |
|---|---|
| Actor | Nonprofit conservation organisation |
| Domain | Wildlife conservation / anti-poaching |
| Decision | Where to place each of up to 20 camera traps in a national park |
| Primary objective | Maximise detection of elephant movement |
| Budget constraint | Maximum 20 cameras |
| Data available | Park maps, past poaching incident locations, elephant GPS tracking data, terrain/vegetation information |
| What is NOT the goal | Camera placement is not directly optimising for poaching interdiction — it is optimising for elephant movement detection |

## Notes for downstream skills
- Elephant GPS tracking data is the key input — it defines where elephants actually move (the coverage target)
- Terrain data may constrain where cameras can physically be placed (line-of-sight, accessibility)
- Poaching incident data is secondary context — could be used to weight certain areas more heavily if the user wants to incorporate threat exposure
- The problem is spatially structured — candidate locations and coverage areas are defined in geographic space
