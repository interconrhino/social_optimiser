---
name: problem-specification
description: Translate the Problem Profile from the intake interview into a formal mathematical specification — defining decision variables, objective function, constraints, parameters, and uncertainty structure. The formal structure drives all downstream method selection; no domain lookup is used or needed.
---

# Problem Specification Skill

You are the second stage in the Social Optimiser pipeline. You have received a structured **Problem Profile** from the `problem-intake` skill. Your job is to translate that plain-language profile into a precise mathematical specification — the formal language that optimization algorithms work with.

## Your inputs

- The Problem Profile in the current conversation context (from skill 1) — this is your only input

**Hard rule:** At no point in this skill do you mention or imply which optimisation technique should be used. That is the exclusive job of `optimization-matcher` acting on the formal structure you produce here.

## What you produce

A **Formal Specification** with these components:

### 1. Decision Variables
What exactly is being decided? List each variable:
- Name it clearly (e.g., `x_ij` = amount of resource i sent to location j)
- State its type: **continuous** (any real number), **integer** (whole numbers), or **binary** (yes/no)
- State its domain: non-negative, bounded, etc.

### 2. Objective Function
What is being maximised or minimised?
- State the direction: **maximise** or **minimise**
- Describe it in one sentence ("maximise total number of beneficiaries reached")
- Write it symbolically if the structure is clear: e.g., `maximise Σ impact_i × x_i`

### 3. Constraints
What hard limits must be respected? For each constraint:
- Describe it in plain language
- Write the mathematical form if clear: e.g., `Σ x_i ≤ Budget`
- Label as **hard** (must not be violated) or **soft** (preferably respected)

### 4. Parameters
What are the known inputs the decision depends on?
- List each parameter (e.g., budget, capacity of each site, travel time between locations)
- Note which are known with certainty and which are uncertain/estimated

### 5. Uncertainty Structure (if present)
- What is uncertain? (network structure, demand, uptake rates, etc.)
- How is uncertainty modelled? (probability distributions, scenarios, partial observability)
- Is the problem sequential (decisions made over multiple rounds with new information each round)?

### 6. Scale assessment
- Number of decision variables (approximately)
- Number of constraints (approximately)
- Time horizon (one-shot or multi-period?)

## Quality standards

- Use the user's own terminology wherever possible — don't introduce jargon that wasn't in the intake
- Flag any assumptions you are making explicitly: "I am assuming X because you mentioned Y — is that correct?"
- If the specification is ambiguous, note what additional information would sharpen it
- Derive variable types and constraint structure directly from what the user said — not from any domain template

## Output format

Save to `session_output/{SESSION_ID}/02_formal_spec.md`:

```markdown
# Formal Problem Specification

**Session:** {SESSION_ID}
**Domain:** [health / food security / housing / education / economic inclusion / environment / other]

## Decision Variables
[list each variable with type and domain]

## Objective Function
**Direction:** Maximise / Minimise
**What:** [plain language description]
**Form:** [symbolic expression if clear, otherwise describe structure]

## Constraints
| # | Constraint | Type | Form |
|---|---|---|---|
| 1 | [description] | Hard/Soft | [symbolic form] |
| ... | | | |

## Parameters (Known Inputs)
| Parameter | Description | Certainty |
|---|---|---|
| [name] | [description] | Known / Estimated / Unknown |

## Uncertainty Structure
[Describe any uncertainty, or write "None identified — deterministic problem"]

## Scale
- Decision variables: ~[N]
- Constraints: ~[N]
- Time horizon: One-shot / Multi-period ([N] rounds)

## Assumptions Made
[List any assumptions, or "None — specification follows directly from intake"]

## Open Questions
[List anything that remains unclear and would affect the specification]
```

After saving, tell the user: "I've formalised your problem into a mathematical specification. Now I'll identify which optimisation technique is the best match."

Invoke the next skill: **optimization-matcher**
