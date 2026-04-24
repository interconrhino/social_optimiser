# Optimisation Recommendation — Plain English

**Session:** 0006
**For:** Head of Strategy and Board, Tri-Valley Workforce Partnership
**Method in plain terms:** *A principled menu builder for five-year placement strategies*

---

## 1. Problem in plain terms

You want to hand your board a short menu — three to ten candidate five-year placement strategies — where each one is the best possible strategy *if* the board commits to a particular view about how to balance your four participant groups. Each strategy should come with a clear picture of what it delivers for school-leavers, mid-career displaced workers, returners, and justice-affected adults over the 20 quarters. The board then chooses.

The right tool for this is a **stance-indexed menu builder**: a method that generates one strategy per named ethical stance, where each stance is a precise, defensible position on the spectrum from "maximise totals" through "proportional/balanced" to "protect the worst-off group." Every strategy on the menu is guaranteed to be non-wasteful (you can't help one group more without hurting another on the menu), and every strategy has a plainly stated ethical label so your board can discuss it in English rather than in maths.

The engine that builds the menu uses your existing trusted simulator as its test-bed. For each ethical stance on the menu, the engine searches across many candidate placement rules, simulates each one forward 20 quarters, and returns the one that comes out best *under that stance*. That search is repeated once per stance, and the resulting set is the menu.

---

## 2. Step-by-step explanation

1. **Agree a short ladder of ethical stances.** The three your board already named — maximise totals, balanced across groups, protect the worst-off — sit naturally on a well-studied family of fairness functions. We add two or three intermediate stances on that family so the menu covers the full spectrum without gaps. Six points is a comfortable default; three or ten are both reasonable.
2. **Agree a policy language.** Rather than choose raw numbers for every quarter (which would be 320 decisions), your strategy is written as a *rule*: "each quarter, give this share of slots to each group, with an adjustment when a group's backlog grows beyond a threshold." The rule has maybe 20–30 knobs. The optimiser turns those knobs.
3. **For each stance on the menu, run the search.** The optimiser proposes a knob-setting, runs your simulator 50-ish times to see how that rule plays out under different random futures, averages the outcomes for the four groups, scores it by that stance's rulebook, and updates the knobs. After a few hundred rounds it converges on the best knob-setting *under that stance*. Repeat for each stance.
4. **Clean the menu.** If two stances produce almost identical outcome curves, drop one — the board shouldn't see redundant options. If gaps appear, add a stance between them and re-run.
5. **Package for the board.** Each menu entry gets: a named stance ("maximise totals", "proportional", "worst-off first", plus their interpolating cousins), the policy's plain-English behaviour, a chart showing 20-quarter outcomes for each of the four groups with uncertainty bands, and a short note on what trade-off that entry makes.
6. **Board picks. Re-run when needed.** When the board chair or government changes, the ethical weighting may shift — regenerate the menu with a different ladder, or add new stances. The methodology is reusable; the simulator stays.

---

## 3. Data checklist

You already have most of what is needed:

| What we need | Have it? | Note |
|---|---|---|
| A simulator that takes a placement rule and returns 20-quarter group outcomes | **Yes** — your commissioned simulator | Needs a documented Python callable interface — confirm with the simulator's original builders |
| Nine years of quarterly allocation and outcome records | **Yes** | Used to back-test and calibrate confidence |
| Participant-level intake data for ~14,000 past participants | **Yes** | Used to calibrate per-group success rates and caseworker-hour costs |
| Employer-side historical data | **Yes** | Already feeds the simulator |
| Caseworker-hours per placement, per group | Probably derivable from your records | Needed for the staff-hour budget constraint |
| Any statutory floors on group allocations | To confirm with your legal/compliance team | If any group has a legally mandated minimum, every menu entry must respect it regardless of stance |
| Decision on per-capita vs raw group outcomes | To confirm with the board before the first run | Affects how "balanced" is defined |

Nothing new needs to be collected. Two items need internal confirmation (statutory floors; per-capita vs raw) before the first full run.

---

## 4. What it will produce

At the end of the engagement, your data team will hand you:

- A **curated menu of 3–10 five-year placement strategies**, each tied to a named ethical stance.
- For each strategy: a **plain-language description of how it behaves** each quarter (e.g., "prioritise school-leavers in green energy for the first four quarters; boost returners in allied health once backlogs exceed 120; protect justice-affected slots during capacity dips").
- For each strategy: **four trajectories over 20 quarters** — one per participant group — with uncertainty bands from the simulator, so the board can see concretely what each group gets under each strategy.
- A **side-by-side comparison table** showing each menu entry's total placements, worst-off-group outcome, and inter-group spread, so the board can scan the trade-offs in one view.
- A **methodology note** for your data team so they can re-run the menu generation whenever the strategic cycle refreshes.
- A **working tool** (Python, open-source, maintained by your three-person data team) that wraps the simulator and produces updated menus on demand.

---

## 5. Confidence and validation

**How to know the result is trustworthy:**

- **Back-test against history.** Before trusting any menu entry, we replay it against the last two years of operational data through the simulator and compare predicted outcomes to what actually happened. Any menu entry that materially disagrees with history gets scrutinised.
- **Beat the sensible baselines.** Every menu entry should beat (a) your current practice under *its own* stance, and (b) a dumb "equal shares" baseline. If a menu entry can't beat these, something is wrong.
- **Sensitivity checks.** We run each menu entry with your slot capacity, caseworker budget, and estimated success rates nudged ±20% and check that the menu's ranking is stable. Strategies that are highly sensitive to small forecast errors get flagged to the board as "fragile under this assumption."
- **Simulator noise.** Because the simulator is stochastic, each evaluation is averaged over 50+ runs. We calibrate that number at the start so the rankings between menu entries are statistically reliable.
- **Redundancy check.** No two menu entries should tell effectively the same story — we filter for this automatically.

The headline honesty: **every number on the menu is conditioned on the simulator being right**. The simulator is trusted by the board for scenario comparison, which is exactly what this use case demands (*relative* rankings between strategies), but less so for absolute forecasts. We'll surface this caveat clearly in the board pack.

---

## 6. Next steps

An 8-month engagement, comfortable within your stated window:

- **Month 1:** Kick-off. Confirm statutory floors, per-capita-vs-raw decision, and the α-ladder (the list of ethical stances). Agree the policy language (share-vector + backlog-pressure knobs).
- **Month 2:** Build the simulator wrapper. Smoke-test on a reduced 2-group × 2-sub-programme problem. Calibrate the number of simulator rollouts per evaluation.
- **Months 3–4:** Full-scale menu generation on the real 4-group × 4-sub-programme × 20-quarter problem. Back-test each menu entry against the last two years of operational data.
- **Month 5:** Sensitivity analyses; refine the α-ladder to fill any gaps and drop any redundancy.
- **Months 6–7:** Board-facing visualisation: charts per menu entry, side-by-side comparison, methodology note.
- **Month 8:** Board presentation. If a menu entry is adopted, plan the first-cycle implementation with an A/B or phased roll-out at the sub-programme level where feasible.
- **Post-engagement:** Your data team owns the tool. When the board chair or government changes, or when forecasts shift, your team re-runs the menu generation in days, not months.

**What we need from you in month 1:** 1–2 meetings with your data team and one with your board chair to lock the ladder of stances and the per-capita question.

---

## 7. Caveats

- **Simulator ceiling.** Everything we report is as good as the simulator. If the simulator misses a dynamic (e.g., a structural shift in employer behaviour after a policy change), the menu's absolute numbers will drift. We mitigate by reporting *relative* differences and by back-testing against history, but we cannot eliminate this.
- **Policy language limits.** Our policies are written as rules with ~20–30 knobs. This is deliberately interpretable, but it means some exotic strategies (e.g., highly non-linear, state-dependent rules) will be out of reach. If back-testing suggests we're leaving meaningful gains on the table, we can enrich the policy language in a follow-up phase — or, more ambitiously, upgrade to a learned-policy approach (welfare-aware reinforcement learning) in a second engagement.
- **Ethical stance is still a choice.** The menu removes the need to pick a weighting *before* seeing outcomes, but someone still has to pick an entry from the menu. That remains the board's political and ethical call, exactly as you intended.
- **Board drift.** If the board's implicit weighting shifts mid-cycle, the chosen menu entry may become suboptimal. Plan a mid-cycle re-run at the two-year mark, or any time the chair / government changes.
- **Statutory floors matter.** If any group (likely justice-affected adults) has a legally mandated minimum, that floor applies to every menu entry. Getting that confirmed in month 1 matters — it shapes every strategy on the menu.
- **First-run caution.** For the first cycle after board adoption, we strongly recommend phasing the new policy in alongside current practice for at least one quarter before full commitment.
