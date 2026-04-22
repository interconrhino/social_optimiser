---
name: optimization-matcher
description: Match the Formal Specification against the optimization catalog to identify the primary technique category and up to two alternatives. Reads optimization_catalog.json and uses structural signals (variable types, objective structure, uncertainty, scale) to score each technique. Outputs a Classification Result saved to the session folder.
---

# Optimization Matcher Skill

You are the third stage in the Social Optimiser pipeline. You have the **Formal Specification** from skill 2. Your job is to identify which optimization technique from the catalog is the best structural match — and explain why.

## Your inputs

- Formal Specification in the current conversation context (from skill 2)
- `knowledge/optimization_catalog.json` — read this in full

## Matching logic

Work through each catalog entry systematically. For each technique, score it against the formal spec:

### Structural matching signals

| Spec feature | What it suggests |
|---|---|
| Binary decision variables | Integer Programming or Matching |
| Continuous decision variables only | Linear Programming |
| Multiple objectives that conflict | Multi-objective Optimisation |
| Movement between locations, routes | Network / Routing Optimisation |
| Hard scheduling rules + time slots | Constraint Satisfaction |
| One-to-one or one-to-many pairing | Matching / Assignment |
| Sequential rounds + social network | Influence Maximisation (POMDP) |
| Uncertainty in inputs, scenario testing | Simulation |
| Partial observability + sequential decisions | POMDP (Influence Maximisation or MDP) |

### Contraindication checking

For your top candidate, check the `contraindications` field in the catalog. If any contraindication applies, demote that technique and re-evaluate.

### Confidence scoring

Assign a confidence level to your primary pick:
- **High** — 4+ signals match, no contraindications apply
- **Medium** — 2-3 signals match, minor caveats
- **Low** — the problem is at the boundary between two techniques

## Output format

Save to `session_output/{SESSION_ID}/03_classification.md`:

```markdown
# Optimization Category Classification

**Session:** {SESSION_ID}

## Primary Match
**Technique:** [name from catalog]
**Catalog ID:** [id field]
**Confidence:** High / Medium / Low

**Matching signals:**
- [Signal 1: which spec feature → which catalog signal]
- [Signal 2: ...]
- ...

**Why this fits:**
[2-3 sentences explaining the structural match in plain language]

**Contraindications checked:**
- [List each contraindication from the catalog entry and whether it applies or not]

## Alternative 1 (if applicable)
**Technique:** [name]
**Catalog ID:** [id]
**When this would be preferred instead:** [1 sentence]

## Alternative 2 (if applicable)
**Technique:** [name]
**Catalog ID:** [id]
**When this would be preferred instead:** [1 sentence]

## Why alternatives were not the primary pick
[Brief explanation of why the primary was chosen over alternatives]
```

After saving, tell the user: "I've identified the technique category. Now I'll research the current state-of-the-art algorithms that have been applied to problems like yours."

Invoke the next skill: **method-research**
