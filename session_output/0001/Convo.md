# Session 0001 — Full Conversation Transcript

---

**User:** okay what is this program

**Assistant:**
> "Welcome to the Social Optimiser. I help social innovators figure out whether their problem can be mathematically optimised — and if so, which specific approach to use.
>
> Tell me about the challenge you're facing. What outcome are you trying to improve, and what's making it difficult?"

In short: you describe a real-world social problem (e.g. allocating food bank resources, routing community health workers, reducing school dropout rates), and this tool will:

1. Diagnose whether the problem is the kind that maths can actually solve
2. If yes, identify the right optimisation technique and give you a research-grade recommendation you could hand to a data scientist or developer

---

**User:** okay I am working for a nonprofit and I am trying to find where to place new cameras in the national park to protect elephants

**Assistant:**
Great — let me set up a session and run this through the intake process.

[Sets up session_output/0001/, reads adaptive_types.json]

Good news — this is the kind of problem maths can help with. Before I run the full analysis, I need a few details to build an accurate profile.

**Three quick questions:**

1. **How many cameras** do you have (or plan to buy)? Is there a budget limit?

2. **What are you trying to detect?** Just elephant presence, or also signs of poaching (people, vehicles, snares)?

3. **What data do you have about the park?** For example: maps, past poaching incident locations, elephant GPS tracking data, or terrain/vegetation information?

(You don't need all of these — just tell me what you have.)

---

**User:** I have a budget limit of around 20 cameras. I am trying to identify elephant movement. I have maps, past poaching incidence locations, elephant gps tracking data, and terrain info

**Assistant:**
Perfect — I have everything I need. Let me complete the intake and save the profile.

[Saves 01_problem_profile.md]

Good — this is a **Technical** problem. Your goal is well-defined, your actions are well-defined, and maths can genuinely help here. Moving to Step 2: translating your problem into a formal mathematical specification.

[Saves 02_formal_spec.md]

Step 2 complete. Now matching this formal spec to the technique catalog — Step 3.

[Reads optimization_catalog.json, saves 03_classification.md]

Step 3 complete — matched to technique catalog. Now spawning the research subagent for Step 4.

[Spawns web research subagent, saves 04_research_findings.md]

Excellent research. Saving findings and moving to method selection.

[Saves 05_method_selection.md]

Now writing the full research-grade recommendation.

[Saves 06_recommendation.md]

All six stages complete. Here is your recommendation:

---

**Your recommendation: Maximum Coverage Location Planning**

Your problem is a great fit for maths. Here is what the analysis found.

**The core idea:** Your elephant GPS data tells you exactly where elephants spend their time — certain corridors, watering holes, and seasonal routes. A method called **Maximum Coverage Location Planning** (MCLP) takes that GPS data, your park terrain, and your 20-camera budget, and calculates the placement that puts cameras in front of the highest possible fraction of elephant activity. It doesn't guess — it finds the mathematically best answer.

**What the method does:**

1. Divides the park into a grid of cells (e.g., 500 m × 500 m)
2. Weights each cell by how often elephants visited it in the GPS data
3. Selects which 20 grid cells to place cameras in, so that the total weight of cells "in view" of at least one camera is maximised
4. Accounts for terrain — cells blocked by hills or dense canopy are excluded from each camera's coverage zone

Because elephants move differently by season, the method runs the placement across 30–50 different slices of your GPS data and finds the placement that performs well across all seasons — not just one.

**What you need to run it:**

| Input | Status |
|---|---|
| Park boundary map | You have this |
| Elephant GPS tracking data | You have this — the most important input |
| Terrain / elevation data | You have this — used to determine line-of-sight |
| Camera detection range (from hardware spec) | Need to check your camera datasheet |
| Python (free) + spopt library (free) | Needs a data scientist or GIS analyst to run |

**What it will produce:**

- A ranked list of the 20 best camera locations (with coordinates)
- A backup list of alternatives in case any sites are physically inaccessible
- A coverage estimate: "these 20 cameras cover X% of total elephant GPS activity"
- A sensitivity chart showing how coverage improves if you add cameras 21, 22, ... (useful for future funding asks)

**Suggested next step:** Share the GPS data and terrain data with a GIS analyst or data scientist, and point them to the session_output/0001/06_recommendation.md file — it contains the full technical specification, Python code templates, and calibration guidance they will need.

---

**User:** okay modify the relevant files to make sure this is now the default operation [referring to the two-file 06a/06b output format]

**Assistant:**
Let me read the existing recommendation file before splitting it.

[Reads 06_recommendation.md]

Creating both files now in parallel.

[Saves 06a_rec_formal_spec.md and 06b_rec_plain_english.md]

Both files are saved in session_output/0001/:

- **06a_rec_formal_spec.md** — formal problem formulation, algorithm spec, implementation code, validation protocol, and references. Hand this to a data scientist or GIS analyst.

- **06b_rec_plain_english.md** — the plain-language version from the chat, expanded with a "one thing to watch out for" section (GPS collar representativeness) that's worth flagging for your team.

The original 06_recommendation.md is untouched — these are additional outputs alongside it.

---

**User:** okay modify the relevant files to make sure this is now the default operation

**Assistant:**
[Reads CLAUDE.md, makes three edits:]
1. File naming — step 6 now saves 06a_rec_formal_spec.md and 06b_rec_plain_english.md instead of 06_recommendation.md
2. Pipeline description — the recommender step now explicitly states it produces two files
3. Depth standard — expanded to define what goes in each file

Done. Every pipeline run from here on will produce both outputs by default.

---

**User:** copy this entire conversation and save it as Convo.md under 0001/ folder

**Assistant:** [Saves this file]
