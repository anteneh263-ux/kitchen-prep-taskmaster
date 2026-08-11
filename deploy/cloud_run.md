# Cloud Run deployment (reference — not automated here)

The service is a FastAPI app (`kitchen_prep/server.py`) served by Uvicorn.

## Container entrypoint

The repository root contains a `Dockerfile`, so `gcloud run deploy --source .`
builds from it rather than falling back to buildpacks. Its entrypoint is:

```
uvicorn kitchen_prep.server:app --host 0.0.0.0 --port ${PORT:-8080}
```

It is declared as `CMD ["sh", "-c", "exec uvicorn ..."]` so Cloud Run's injected
`$PORT` expands and uvicorn runs as PID 1 (clean SIGTERM handling on scale-down).

Notes on the image:

- Base `python:3.12-slim`; dependencies come from `requirements.txt`.
- Only `kitchen_prep/` and `scripts/` are copied. `.env`, `.git`, `.venv`,
  `out/`, caches and tests are excluded by both the explicit `COPY` paths and
  `.dockerignore`.
- `scripts/generate_sales_history.py` runs at build time. The file is gitignored
  but the deterministic fallback forecast reads it, so generating it during the
  build keeps the image self-contained; the generator is seeded, so the result is
  identical on every build. `scripts/verify_data.py` then runs as a build-time
  gate, failing the build on a data-integrity regression.
- The image runs as the unprivileged `appuser`. `/app` stays writable so the
  local JSON store can create `out/` if `KP_STORE` is not set to `firestore`.

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
