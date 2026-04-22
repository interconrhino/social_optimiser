---
name: method-research
description: Spawn a web-search subagent to find current state-of-the-art algorithms for the identified optimization category, with a focus on social sector applications. Returns SOTA algorithm names and key papers. Saves research findings to the session folder.
---

# Method Research Skill

You are the fourth stage in the Social Optimiser pipeline. You have the **Classification Result** from skill 3. Your job is to research the current best-known algorithms for that technique category, especially any applied to social sector problems.

## How to execute this skill

**Spawn a subagent** using the Agent tool with the following brief. The subagent has WebSearch and WebFetch access. You will NOT do the web search yourself — delegate it entirely.

### Subagent brief

```
You are a research agent finding current state-of-the-art optimization algorithms for a social impact application.

TECHNIQUE CATEGORY: [paste the primary match from the Classification Result]
PROBLEM CONTEXT: [paste the 2-3 sentence "Why this fits" description from the Classification Result]
FORMAL OBJECTIVE: [paste the objective function from the Formal Specification]

Your task:
1. Search for the best-known algorithms for this technique category applied to social sector or humanitarian problems. Use queries like:
   - "[technique name] algorithm social impact [specific domain] site:arxiv.org"
   - "[technique name] humanitarian operations research"
   - "[technique name] algorithm comparison benchmark"
   - "[specific algorithm name] theoretical properties approximation ratio"

2. For each promising algorithm or paper you find, retrieve:
   - Algorithm name and brief description of how it works
   - Key paper citation (title, authors, year, URL if available)
   - Theoretical properties: optimality guarantees, approximation ratio, complexity class
   - Any reported performance on real-world social sector problems

Return a structured report with:
- Top 2-3 algorithms ranked by relevance to this specific problem
- For each: name, how it works, key paper, theoretical properties
- Any recent developments (last 3 years) in this algorithm class worth noting
```

## What to do with the subagent's findings

When the subagent returns, combine its findings with the catalog entry's `algorithm_examples` field (from `knowledge/optimization_catalog.json` for the matched technique) to produce a consolidated research summary.

## Output format

Save to `session_output/{SESSION_ID}/04_research_findings.md`:

```markdown
# Method Research Findings

**Session:** {SESSION_ID}
**Technique category:** [from classification]

## State-of-the-Art Algorithms

### 1. [Algorithm Name] ⭐ Recommended starting point
**How it works:** [2-3 sentences on the algorithmic approach]
**Key reference:** [citation + URL]
**Theoretical properties:** [optimality / approximation ratio / complexity]
**Social sector use:** [any known applications]

### 2. [Algorithm Name]
**How it works:** [...]
**Key reference:** [...]
**Theoretical properties:** [...]

### 3. [Algorithm Name] (if found)
[same structure]

## Recent Developments
[Any notable advances in the last 3 years, or "No major recent shifts identified"]

## Research gaps
[Any aspect of the problem that is poorly served by current literature, or "Well-served area"]
```

After saving, tell the user: "I've completed the research. Now I'll select the best method for your specific situation."

Invoke the next skill: **method-selection**
