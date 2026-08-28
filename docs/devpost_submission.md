# Devpost Submission Copy

Copy these sections into the matching Devpost fields. Keep the final video URL
placeholder until the public YouTube or Vimeo upload is ready.

## Project name

Kitchen Prep Taskmaster

## Tagline

The autonomous kitchen agent that runs the daily prep-and-ordering cycle and
shows its work.

## Category

The Taskmaster

## Short summary

Kitchen Prep Taskmaster removes a daily restaurant workflow that is usually
handled through guesswork. At 07:00 Europe/Oslo, Cloud Scheduler securely
triggers a private Cloud Run worker. Gemini 3.5 Flash proposes per-dish demand
and prioritizes the final briefing, while deterministic Python validates the
forecast, expands recipes, consumes batch inventory using FEFO, separates
today's shortfalls from future replenishment, flags expired stock and calculates
orders from what is genuinely left. The result is stored in Firestore and
published through a bilingual, mobile-friendly dashboard whose production plans
are read-only. An isolated public sandbox lets judges run the same deterministic
planning tools and approve or reject a simulated action without touching
production data or external systems.

## Inspiration / problem

Restaurant opening teams repeatedly answer three operational questions under
time pressure: how much should we prep, what are we short of today, and what
should we order? The answers are often based on memory and a quick visual stock
check. That creates stockouts, emergency supplier runs, over-ordering and food
waste. Batch expiry is particularly easy to miss, and subtracting today's demand
at the wrong point in the calculation can silently double-count it.

I built Kitchen Prep Taskmaster to complete that whole workflow unattended and
to leave behind an operational plan that a cook can act on, not another chat
response.

## What makes it innovative

Kitchen Prep Taskmaster is not another inventory app that waits to be opened.
It is a self-running, auditable operations agent. The innovation is not the
number of restaurant-management features; it is the trust architecture beneath
the workflow.

**Trust by construction — AI proposes, deterministic code decides.** Gemini is
confined to two schema-bounded roles: proposing demand and writing the final
briefing. It never computes or changes an authoritative ingredient, inventory,
shortfall, order or delivery quantity. Python validates every forecast against
the known menu, authoritative date and covers, strict types and a dishes-per-
cover safety band. An unavailable or rejected proposal automatically activates
a deterministic baseline, and the published plan visibly records which path
was used.

**A Taskmaster, not a tool.** Cloud Scheduler starts the complete workflow at
07:00 without a chat, button click or open application. The agent resolves
demand inputs, obtains weather context, forecasts dishes, expands recipes,
consumes batch inventory using FEFO, calculates prep and replenishment, creates
the briefing and publishes the result end to end.

**From disconnected operational data to one approval-ready kitchen plan.** A
spreadsheet can calculate a shortage after someone manually assembles the data.
Kitchen Prep Taskmaster gathers the available context, detects conflicts between
demand, recipes, inventory, expiry and scheduled deliveries, then flags
shortfall recommendations for human review with the calculation and audit trail
attached.

**Reproducibility as a design principle.** Every attempt appends a step-by-step
run log even when execution fails. Each operational date has a replay-safe,
frozen inventory input and output snapshot; retries are idempotent, and forced
replays reproduce the same FEFO consumption instead of consuming stock twice.
Every published plan identifies its forecast, briefing, inventory and planning
basis.

The project deliberately demonstrates this architecture on synthetic data for
one kitchen. It is a working agent architecture and hackathon prototype, not a
claim of being a mature restaurant-management product.

## What it does

- Runs automatically every morning through Cloud Scheduler and authenticated
  Cloud Run.
- Uses Gemini 3.5 Flash to propose demand per dish with confidence, drivers and
  reasoning.
- Validates every forecast against authoritative date, expected covers, the
  exact menu, integer quantities and a dishes-per-cover safety band.
- Falls back to a deterministic four-week same-weekday baseline when a model
  response is unavailable or rejected, and exposes that degraded state.
- Explodes dish demand through recipes into ingredient requirements.
- Consumes valid inventory batches first-expired-first-out and flags expired
  batches before consumption.
- Keeps today's prep shortfalls separate from replenishment orders.
- Calculates replenishment from post-consumption stock and excludes batches that
  expire before delivery.
- Persists replay-safe daily inventory input/output snapshots so retries and
  forced reruns never consume stock twice.
- Uses Gemini for a schema-validated kitchen briefing after all quantities are
  frozen.
- Includes an interactive, session-scoped demo: run the morning plan, watch
  server-side tool events, inspect one controlled shortfall, approve or reject a
  simulated order, and verify the status change in its audit trail.
- Stores plans, snapshots and audit logs in Firestore.
- Publishes an English/Norwegian responsive dashboard with plan history,
  forecast explanations, an agent briefing, run-integrity evidence and a visual
  five-step autonomous execution trace.

## How I built it

The scheduled production path is:

Cloud Scheduler → OIDC-authenticated private Cloud Run worker → FastAPI → Python
orchestrator → Google Gen AI SDK / Gemini 3.5 Flash → deterministic validation
and inventory pipeline → Firestore → separate public read-only Cloud Run viewer.

Gemini is called at two schema-bounded points. First it proposes the demand
forecast. The proposal cannot enter the operational pipeline until Python has
validated its date, covers, dish identifiers, types and overall ratio. Second,
Gemini receives the completed, frozen plan and returns prioritization and
recommended actions in a fixed JSON contract. Python renders the published
output. Gemini never computes ingredient consumption, FEFO, shortfalls, order
quantities or delivery dates.

The worker requires Cloud Run authentication and receives its Gemini credential
from Secret Manager. Cloud Scheduler invokes it with OIDC. The public viewer is
a separate service with Firestore viewer permission only and no Gemini secret.
Its production plan routes are read-only. The interactive `/demo` routes operate
only on bounded in-memory sessions using synthetic data and a simulated supplier
connector.

An optional Google ADK adapter exposes the same orchestrator as one tool for
interactive development. The scheduled production path uses the Google Gen AI
SDK directly and does not claim to route through ADK.

## Technologies used

- Gemini 3.5 Flash
- Google Gen AI SDK
- Google ADK optional interactive adapter
- Google Cloud Run
- Google Cloud Scheduler
- Google Cloud Firestore
- Google Secret Manager
- FastAPI and Uvicorn
- Python 3.12 production container
- Open-Meteo weather API
- Pytest

## Data sources

All restaurant data is synthetic and generic. The repository includes six menu
dishes, thirteen ingredients, recipes, par levels, lead times, shelf lives,
bookings and fifteen inventory batches. Sales history is generated
deterministically from a fixed seed and contains weekday, weather and per-dish
signals. Forecast context uses only observations strictly before the target date
to prevent future leakage. Live daily weather comes from Open-Meteo, with a
deterministic offline fallback.

## Challenges

The hardest problem was defining the boundary between model judgment and
operational arithmetic. A plausible model answer is not enough when a cook or
supplier may act on the result, so every model proposal sits behind a strict
contract.

Another challenge was ordering the replenishment calculation correctly. The
first approach risked subtracting today's demand twice. The final pipeline first
consumes today's requirements from actual batches, then orders the difference
between remaining usable stock and par. A regression test uses a scenario where
the correct answer and the double-counted answer differ numerically.

Inventory persistence introduced a second replay problem: a forced rerun must
not start from the previous run's output and consume the same stock again. Each
date therefore freezes its input and output snapshots. A replay uses the same
input and deterministically reproduces the same FEFO consumption and remaining
stock. Supplier orders become stable, dated batches on delivery, while open
orders count toward stock at delivery so the next morning cannot order the same
quantity again.

## What I learned

- Validation bands can be more valuable than prompt refinement.
- A fallback is safe only when it is visible at every layer.
- Workflow ordering is a correctness property, not a style preference.
- Today's shortage and future replenishment are different operational problems.
- A public demo surface should not require exposing a mutation endpoint or
  production credential.
- Reproducible synthetic data and deterministic tests make an agentic demo much
  easier to audit.

## Production evidence

- Private worker: `kitchen-prep-taskmaster-web`, region `europe-north1`, current
  revision `kitchen-prep-taskmaster-web-00011-vlp`.
- Public read-only viewer: `kitchen-prep-viewer`, current revision
  `kitchen-prep-viewer-00010-xlk`.
- Cloud Scheduler: `kitchen-prep-daily`, enabled at `0 7 * * *`, timezone
  `Europe/Oslo`.
- Verified production run: `forecast_source: gemini`,
  `forecast_note: gemini_ok`, `briefing_source: gemini`.
- Verified replay-safe snapshots and controlled production migration; the
  current plan records `inventory_basis: epoch_seed_snapshot`, while ordinary
  subsequent dates return to `date_input_output_snapshot`.
- Offline test suite: 136 passed, 1 integration test skipped without a live key.

## Links

- Hosted project:
  https://kitchen-prep-viewer-373405758807.europe-north1.run.app
- Source code:
  https://github.com/anteneh263-ux/kitchen-prep-taskmaster
- Demo video: TO BE ADDED

## Disclosures

The project was created during the contest submission period; the first Git
commit is dated August 11, 2026. No pre-contest application code or private
starter project was incorporated. AI coding assistants, including OpenAI Codex,
were used for implementation, review, diagnostics and documentation. The entrant
selected the problem and architecture, directed and reviewed the work, ran the
tests and deployments, and remains responsible for and owner of the submission.
All upstream open-source licenses and API terms apply. No real restaurant,
supplier or customer data is used.

## Private testing instructions field

No credentials are required for the judge-facing read-only application:

https://kitchen-prep-viewer-373405758807.europe-north1.run.app

The interface defaults to English. Start with the five-step **Autonomous run**
panel, which shows the production plan's input source, Gemini forecast,
validation result, deterministic FEFO/planning basis and published briefing.
Then inspect the human-approval boundary in **Agent briefing**, forecast drivers,
prioritized prep, shortfalls, replenishment orders, expired waste, dated
inventory snapshot basis and plan history. JSON is available from
`/plans/latest`; capped history is available from `/plans` and `/plans/{date}`.
The public service is intentionally read-only: `POST /runs/daily`, `/docs`,
`/redoc` and `/openapi.json` return 404. The private worker execution and Google
Cloud Console evidence are demonstrated in the submission video. Full local and
cloud reproduction steps are in the public repository README.
