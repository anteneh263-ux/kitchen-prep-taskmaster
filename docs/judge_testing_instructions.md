# Judge Testing Instructions

No login is required for the read-only judge interface:

https://kitchen-prep-viewer-373405758807.europe-north1.run.app

The interface defaults to English. Use the **Norsk** link to verify the second
supported language.

## What to verify

1. The page loads without authentication and displays the latest Firestore plan.
2. The status is `OK` when both forecast and briefing sources are `gemini`.
3. The page shows expected guests, prioritized prep, today's shortfalls,
   replenishment orders, delivery dates and expired-batch waste.
4. The run integrity panel identifies the dated input/output inventory snapshot
   basis, and a forced rerun replays the original input without double-consuming.
5. The JSON representation is available at `/plans/latest`; capped read-only
   history is available at `/plans` and `/plans/{date}`.
6. The public service is read-only: `POST /runs/daily`, `/docs`, `/redoc` and
   `/openapi.json` return 404.
7. The health endpoint is `/health`.

## Reproducing locally

Follow the root `README.md` for environment setup. A network-free deterministic
run requires no credentials:

```bash
python scripts/generate_sales_history.py
pytest -m "not integration"
python -c "from kitchen_prep.orchestrator import run_daily_prep; print(run_daily_prep('2026-08-14'))"
```

With `GOOGLE_API_KEY` configured manually, run the integration test to verify
that both controlled model steps use Gemini rather than silently degrading:

```bash
pytest -m integration -q
```

The private worker is intentionally not exposed to judges. Its authenticated
live execution and Google Cloud deployment are demonstrated in the submission
video; the public viewer has no mutation endpoint and no Gemini secret.
