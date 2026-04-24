---
name: proxy-paper-generator
description: Given a source research paper (PDF) and its gold-standard method label, produce a "proxy brief" — a rewritten problem description in a different social-impact domain that preserves the paper's underlying optimisation structure (decision variables, objective, constraints, dynamics, data availability). The proxy is designed so that (a) the social_optimiser, when given the proxy, should converge on the same method family as the original paper, and (b) a web search on the proxy's domain keywords does not easily surface the original paper. Used for evaluation of the social_optimiser agent.
---

# Proxy Paper Generator

You translate an academic paper's optimisation problem into a new social-impact domain that a grassroots NGO, funder, or policy officer might plausibly describe in plain language. You preserve the mathematical structure; you change the narrative.

---

## Inputs

- **Source PDF path** — absolute path to the paper (e.g., `/Users/Gillian/Downloads/AI4SI PROJECT/sources/2202.00916v1.pdf`)
- **Gold-label row** — the JSONL entry from `gold_method_labels.jsonl` with `case_id`, `title`, `social_problem`, `gold_optimization_type`, `gold_key_method`

---

## Step 1 — Extract the structural core

Read the paper's abstract, introduction, problem statement, and formal model sections. Extract these invariants into a bulleted list. This is what the proxy **must** preserve.

- **Decision variables** — what is chosen, at what granularity; binary / integer / continuous; per entity or aggregate
- **Objective** — what is maximised / minimised; single-period or cumulative; discount factor if any
- **Constraints** — budget, capacity, coupling, logical, regulatory
- **Dynamics** — deterministic / stochastic / adversarial; one-shot / sequential / Markov; time horizon
- **Information structure** — what's known a priori, what's observed over time, what's hidden
- **Data availability** — historical records, features, demographics, labels
- **Scale** — N entities, T periods, K budget, typical magnitudes

Do not skip this step. The rest of the skill depends on it.

---

## Step 2 — Pick a new social domain

Brainstorm **3 candidate domains**, each of which could in principle have the same structural core. Reject any candidate that:

- Shares the original paper's primary keywords (e.g., if original is "maternal health", reject "tuberculosis adherence")
- Is itself a well-known target of the same method family in the AI4SI literature (e.g., do not map RMAB problems to "poaching patrols" — PAWS already exists)
- Shares the original's named programme, geography, or distinctive numerical examples

Select the candidate that best preserves the structural core with the least narrative contortion. If all three candidates require contortion, brainstorm 3 more.

Document your reasoning in the sidecar metadata (Step 5).

---

## Step 3 — Draft the proxy brief

Write in the voice of an **NGO programme officer or social entrepreneur** describing their problem in an email or a funder pitch. Length: 400–800 words. Tone: plain, grounded, real-world.

**Must include:**
- Plain-language problem statement (no optimisation jargon)
- Organisation and mission context
- What decisions need to be made, at what cadence, across how many entities
- What resources / capacity they have (staff, budget, per-period limits)
- What data is available — including historical data from current practices
- What success looks like in their terms
- Concrete numbers (can be illustrative): N entities, K per-period capacity, T horizon, rough data volumes

**Must not include:**
- Any named optimisation technique (bandit, MDP, LP, IP, Whittle, DFL, RL, etc.)
- References to mathematical frameworks or formulations
- Hints at solution methodology
- The original paper's title, authors, named programme, or distinctive quantitative examples
- Vocabulary that directly telegraphs the method class ("arm", "reward", "policy", "state", "transition")

Ordinary domain words that happen to overlap with optimisation vocabulary (e.g., "allocate", "schedule", "assign") are fine — do not contort the narrative to avoid them.

---

## Step 4 — Self-test for search leakage

Generate **3 plausible Google queries** a user with this problem might realistically type:

1. One using the domain's core vocabulary (e.g., "refugee caseworker weekly home visit scheduling")
2. One using structural problem language (e.g., "how to prioritise limited staff across hundreds of cases")
3. One using "what methods exist" framing (e.g., "data-driven approach to dynamic case prioritisation")

For each query, assess in one sentence: would the original paper's title, authors, or named programme plausibly appear on the first page of Google results? Be honest — if there's meaningful leakage risk, revise the proxy's narrative (different domain specifics) and re-run the self-test. Log both the initial queries and the final queries in the sidecar.

---

## Step 5 — Write the sidecar metadata

Save `eval/proxy_papers/paper_NN_meta.json` with:

```json
{
  "original_paper_id": "paper_04",
  "original_title": "...",
  "original_local_file": "2202.00916v1.pdf",
  "proxy_domain": "refugee_resettlement_casework",
  "structural_core": {
    "decision_variables": "...",
    "objective": "...",
    "constraints": "...",
    "dynamics": "...",
    "information_structure": "...",
    "data": "...",
    "scale": "..."
  },
  "candidate_domains_considered": ["...", "...", "..."],
  "domain_selection_rationale": "...",
  "leakage_queries": [
    {"query": "...", "assessment": "..."},
    {"query": "...", "assessment": "..."},
    {"query": "...", "assessment": "..."}
  ],
  "gold_method_family": "...",
  "gold_key_method": "..."
}
```

The `gold_method_family` and `gold_key_method` fields are copied from the gold label and live **only in the sidecar**. They are used later by the recommendation-judge. Never place them in `paper_NN.md`.

---

## Outputs

- `eval/proxy_papers/paper_NN.md` — the proxy brief (what the simulated-innovator will read and use)
- `eval/proxy_papers/paper_NN_meta.json` — metadata sidecar (what the judge will reference)

After both files are written, print a one-paragraph summary: the original paper, the chosen proxy domain, the structural invariants preserved, and any flagged leakage risks. This is what Gillian reads for the spot-check.
