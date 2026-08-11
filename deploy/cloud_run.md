# Cloud Run deployment (reference — not automated here)

The service is a FastAPI app (`kitchen_prep/server.py`) served by Uvicorn.

## Container entrypoint

```
uvicorn kitchen_prep.server:app --host 0.0.0.0 --port ${PORT:-8080}
```

## Build & deploy (run manually when ready)

```bash
export PROJECT=your-project-id
export REGION=us-central1

gcloud run deploy kitchen-prep-taskmaster \
  --source . \
  --project="$PROJECT" \
  --region="$REGION" \
  --no-allow-unauthenticated \
  --set-env-vars=KP_STORE=firestore,GOOGLE_CLOUD_PROJECT=$PROJECT,GOOGLE_CLOUD_LOCATION=$REGION,RESTAURANT_LAT=59.91,RESTAURANT_LON=10.75
```

- `GOOGLE_API_KEY` should be provided via Secret Manager, not `--set-env-vars`.
- `--no-allow-unauthenticated`: only the Scheduler service account may invoke it.

## Endpoints

- `POST /runs/daily` — start the idempotent daily run (optional body `{"date": "YYYY-MM-DD", "force": false}`).
- `GET /plans/latest` — latest published plan (simple mobile view).
- `GET /healthz` — liveness.

## Persistence

With `KP_STORE=firestore`, plans/run-logs/inventory live in Firestore
(`daily_plans`, `run_logs`, `inventory`). The published markdown is stored as a
field on the `daily_plans/{date}` document.
