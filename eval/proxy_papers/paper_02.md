# Teaching Our Participatory-Budgeting Assistant to Rank Neighbourhood Project Bundles the Way Residents Actually Want

*Submitted by the Director of Civic Technology, Northside Participatory Budgeting Coalition — April 2026*

## Who we are

The Northside Participatory Budgeting Coalition is a civic-tech non-profit that supports mid-sized city governments in running participatory budgeting (PB) cycles — the process where residents directly decide how a slice of the capital budget (typically 2–5% of public-works money) is spent in their own districts. Over the past eight years we've helped run cycles in 14 cities. Each cycle, residents submit hundreds of raw project ideas (a new crosswalk at Maple and 8th; after-school tutoring at the library; resurfacing a stretch of bike lane). Volunteer "budget delegate" panels then consolidate those ideas into a smaller set of fully-costed project *bundles* — usually twenty to forty bundles — and the whole neighbourhood votes on which bundles get funded subject to the district's cap.

The bottleneck we keep hitting is the consolidation step. A panel of ten to fifteen volunteers sits through weeks of evening meetings trying to package ideas into bundles that residents will actually feel good about voting on. Our delegates burn out, the bundles drift toward what the most vocal delegates want rather than what the wider neighbourhood cares about, and smaller cities simply can't run a full PB cycle because the volunteer labour is too expensive.

## What we're trying to build

We want to give each volunteer panel a software assistant that, given the pool of raw submitted ideas plus basic district context (demographics, existing infrastructure, recent service requests), can score and pre-rank *candidate project bundles* — so that delegates spend their limited meeting time refining a short list the assistant proposes rather than hand-crafting every bundle from scratch. The assistant would be deployed inside each city's existing PB platform and would run offline on modest hardware (we serve small cities and can't ask them to pay for premium cloud APIs; several of our partner cities have data-residency rules that rule out sending resident deliberation content to third-party model providers).

For the assistant to be trusted, it has to rank bundles the way residents in that district would rank them — not the way the average PB expert in our head office would rank them, and not the way a generic large language model trained on the open web would rank them. Residents in an older, transit-poor district weight things very differently from residents in a younger, denser one.

## What data we have, and where it comes from

Over the last three years we've been running a structured side-exercise during every PB cycle we support. In each participating district we recruit a broad panel of **roughly 60–90 residents** (stratified across age, income, tenure, and neighbourhood sub-area) to do **pairwise judgement tasks** online. Each task shows two candidate project bundles side-by-side, with a plain-language summary of each, and asks: *"Which of these two bundles would do more for this neighbourhood over the next five years?"* The panellist picks one of the two (or marks "too close to call").

Across the districts we've supported we now have roughly **9,000 pairwise judgement records over about 180 distinct district-prompts** (a "prompt" is a specific framing — e.g., *"for this district, prioritise safety improvements for elderly residents"* — paired with that district's context). Each pairwise judgement is a piece of noisy evidence about what the neighbourhood would, collectively, have preferred.

The judgements are noisy in ways we're very aware of:

- **Individual panellists are inconsistent** — show the same person the same pair three weeks apart and a non-trivial fraction flip their answer.
- **Panellists disagree with each other** — even a fairly clean pair will sometimes come back as 60/40 rather than 95/5, and we can't tell whether that's genuine pluralism or just noise.
- **Attention varies** — panellists on mobile, late at night, partway through a long session, give visibly noisier signals.
- **We also supplement with a second source** — a small number of trained civic-design reviewers do a similar pairwise exercise on the same pairs. They're more consistent than residents but they don't always reflect what residents would actually feel, so we can't just use them exclusively.

Because of all of this, for any given pair of bundles and any given prompt, what we end up with is not a clean "bundle A is better" label but a **soft signal** — something like "residents preferred A over B with probability roughly 0.7, but there's real uncertainty around that 0.7."

## The decision we need help with

We want to fine-tune a medium-sized open-weights language model (something in the 3–8 billion parameter range — runs on a single GPU, ships inside our partner cities' infrastructure) so that, given a district context and a prompt, it scores candidate bundles in a way that tracks the resident preference signal. Then at deployment time, in a *new* district where we have context but no fresh pairwise data yet, the model pre-ranks bundles for the volunteer panel.

The thing that worries us most is this: **the districts where we'll deploy the assistant will not look exactly like the districts where we trained it.** New cities sign on, demographics shift, priorities move (climate resilience has become much more prominent in the last two years than it was when we started collecting data). So even if our training judgements were crisp and clean — which they're not — the preference pattern at deployment is going to drift from what we trained on. We've seen earlier prototypes behave badly here: they pick up on a superficial pattern in the training panels (e.g., always prefer bundles that mention "youth") and then recommend bundles that a new neighbourhood clearly wouldn't endorse.

We'd like a training approach that doesn't over-commit to the training preference signal — one that stays cautious on pairs where the resident panel was split or inconsistent, and that degrades gracefully when the deployment neighbourhood's preferences aren't a perfect match for the training ones. We've read work that hedges against *all* sources of training-time noise at once, but that tends to produce assistants that are timid and unhelpful across the board. We want something more surgical: robustness specifically to the fact that the preference judgements themselves are noisy and will shift, without making the rest of the training artificially pessimistic.

## What success looks like

- Pre-ranked bundle short-lists that delegates agree reflect their neighbourhood within the first panel meeting, across at least three new partner cities we haven't trained on.
- Volunteer meeting hours per PB cycle reduced by roughly a third without loss of bundle quality as judged by the final neighbourhood-wide vote turnout and approval margin.
- An assistant we can actually ship on-premises — no reliance on a paid external model at inference time, because several of our partner cities cannot send deliberation content off-site.
- A credible story we can tell a city council about *why* they should trust the rankings, including how the system handles the fact that the resident panel it learned from was not unanimous.

We have a two-person ML team, a modest compute budget (a handful of A100-class GPUs for training), and a six-month runway to get a pilot ready for the autumn PB cycles. We're open to partnering with an academic group on the methodology.
