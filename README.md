# Kitchen Prep Taskmaster

An autonomous daily kitchen **prep + ordering** agent for the *All Things Agentic*
hackathon (Taskmaster track). Every morning it forecasts demand, plans prep,
computes replenishment orders up to par, flags expiring stock (FEFO), and
publishes a briefing — end to end, no chat required.

- **Model:** `gemini-3.5-flash` (two controlled steps only: demand forecast + briefing).
- **Framework:** Google ADK (single tool: `run_daily_prep`).
- **Cloud:** Cloud Run (HTTP), Cloud Scheduler (07:00 Europe/Oslo, OIDC), Firestore.
- **Data:** fully synthetic. No real restaurant data is used.

Authoritative quantities are computed by deterministic Python. Gemini never
computes or changes a quantity; it proposes a demand forecast (which is validated,
with a deterministic fallback) and narrates the briefing.

## Spin-up (local, offline — no API key needed)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Generate synthetic sales history (deterministic, seeded)
python scripts/generate_sales_history.py

# 2. Verify data integrity (referential + no future leakage)
python scripts/verify_data.py

# 3. Run the local unit/e2e tests (no network)
pytest -m "not integration"

# 4. Run the pipeline for the demo date
python -c "from kitchen_prep.orchestrator import run_daily_prep; import json; \
print(json.dumps(run_daily_prep('2026-08-14'), ensure_ascii=False, indent=2))"
```

Outputs (plan JSON + `.md` briefing) are written under `out/` and are not committed.

Without `GOOGLE_API_KEY`, the two Gemini steps run in offline/deterministic mode
(baseline forecast + deterministic briefing). Set `GOOGLE_API_KEY` to use real
`gemini-3.5-flash`, then run the integration test with `pytest -m integration`.

## Run as an agent / service

```bash
adk web                       # local ADK UI, exposes the run_daily_prep tool
uvicorn kitchen_prep.server:app --port 8080   # FastAPI: POST /runs/daily, GET /plans/latest
```

## Deploy

See `deploy/cloud_run.md` and `deploy/scheduler.md`. Deployment is intentionally
not automated here.

## Design

The consolidated, authoritative specification is `RESOLVED_SPEC.md` (delivered
separately). Key rules: single ADK tool, Gemini never touches authoritative
numbers, deterministic forecast fallback (±30% ratio band), FEFO waste flagging,
today's prep shortfalls kept separate from future replenishment, run log preserved
on failure, idempotent per date, synthetic data only.
