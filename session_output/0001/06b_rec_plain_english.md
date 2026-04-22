# Recommendation: Plain English Summary — Session 0001
## Optimal Camera Trap Placement for Elephant Movement Detection

---

## The problem in plain terms

You have 20 cameras and a national park full of elephants. The challenge is that elephants don't spread evenly across the park — they have favourite corridors, watering holes, and seasonal routes. Placing cameras without this knowledge risks wasting most of them in areas elephants rarely visit.

This recommendation uses a mathematical method called **Maximum Coverage Location** to analyse your elephant GPS data and park terrain together, and calculate exactly which 20 locations would put cameras in front of the most elephant activity. The method guarantees you are getting the best possible 20-camera coverage, not just a reasonable guess — and it accounts for the fact that elephants move differently in different seasons.

---

## What the method does, step by step

1. Divides the park into a grid of cells (e.g., 500 m × 500 m squares)
2. Weights each cell by how often elephants visited it in the GPS data — hotspots like watering holes and known corridors get scored higher
3. Selects which 20 grid cells to place cameras in, so the total weight of cells "in view" of at least one camera is as large as possible
4. Accounts for terrain — cells blocked by hills or dense canopy are excluded from each camera's coverage zone
5. Runs the placement across 30–50 different slices of your GPS data (e.g., wet season vs. dry season) and finds the placement that holds up well across all seasons — not just one

---

## What you need to run it

| Input | Do you have it? |
|---|---|
| Park boundary map | Yes |
| Elephant GPS tracking data | Yes — the most important input |
| Terrain / elevation data | Yes — used to work out line-of-sight |
| Vegetation / canopy data | Yes |
| Past poaching incident locations | Yes — optional enhancement |
| Camera detection range (from hardware datasheet) | Check your camera spec sheet |
| Python (free) + spopt library (free) | Needs a data scientist or GIS analyst to run |

---

## What it will produce

- A ranked list of the 20 best camera locations, with coordinates you can navigate to in the field
- A backup list of alternative sites in case any of the top 20 are physically inaccessible
- A coverage estimate: "these 20 cameras cover X% of total elephant GPS activity"
- A sensitivity chart showing how coverage improves if you were to add cameras 21, 22, and beyond — useful for future funding conversations

---

## How confident can you be in the result?

Very confident, for two reasons:

1. **The maths guarantees optimality.** This is not a heuristic or a best guess — the solver proves that no other placement of 20 cameras could do better, given your data.

2. **You can cross-check against your rangers.** A good first validation step is to ask your park rangers to nominate their 20 preferred sites from local knowledge, then compare. If the model agrees with them on most sites and adds a few they hadn't thought of, that builds confidence in both directions.

---

## Suggested next steps

1. **Check your camera datasheet** for the maximum detection range in metres — this is the one piece of data you didn't mention having, and it's needed to run the model.

2. **Find a GIS analyst or data scientist** who can run the model. Point them to [06a_rec_formal_spec.md](06a_rec_formal_spec.md) — it contains the full technical specification, Python code templates, and calibration guidance.

3. **Start with 10 cameras.** Deploy the top 10 sites first. After 3 months, compare actual elephant detections at each camera against what the model predicted. Use that real-world data to refine the model before deploying the remaining 10. This phased approach lets you course-correct early if anything was miscalibrated.

---

## One thing to watch out for

The model is only as good as your GPS data. If the GPS collars are on a small or unrepresentative sample of your elephant population, the model will over-index on where those specific animals go. If possible, include GPS data from multiple animals across different age and sex classes to get a fuller picture of herd movement patterns across the park.
