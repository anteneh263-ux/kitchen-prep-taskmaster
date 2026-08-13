# Demo Recording Runbook

Prepare these windows before recording. Do not improvise navigation during the
four-minute take.

## Window 1 — public dashboard

Open:

https://kitchen-prep-viewer-373405758807.europe-north1.run.app

Keep the page at the top, in English, with browser zoom large enough to read the
hero, metrics and run-integrity panel.

## Window 2 — architecture

Open the rendered diagram from `docs/architecture.md` on GitHub. Position it so
the Scheduler, private worker, Gemini gates, deterministic core, Firestore and
public viewer are visible.

## Window 3 — Google Cloud Console

Prepare these pages without displaying secret values:

1. Cloud Run → `kitchen-prep-taskmaster-web` → revisions/traffic.
2. Cloud Scheduler → `kitchen-prep-daily` → schedule and state.

Do not open Secret Manager during the recording.

## Window 4 — terminal

Before recording:

```bash
cd "$HOME/Downloads/kitchen-prep-taskmaster-v2"
gcloud config set project kitchen-prep-taskmaster-263
```

During the unedited live execution, run:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"force":true}' \
  https://kitchen-prep-taskmaster-web-373405758807.europe-north1.run.app/runs/daily
```

The identity token is substituted by the shell and is not printed. The response
should show `forecast_source: gemini` and `forecast_note: gemini_ok`.

Refresh the public dashboard and point out:

- `OPERATIONAL`;
- Gemini forecast and briefing sources;
- `date_input_output_snapshot`;
- prioritized prep and readable dish names;
- today's shortfalls;
- replenishment orders;
- forecast drivers and reasoning;
- plan history.

## Test evidence

Prepare this output before recording, or run it if timing permits:

```bash
pytest -q
```

Expected offline result: `121 passed, 1 skipped`. The skipped test is the
credentialed integration test; the live production execution is the evidence for
that path.

## Safety check immediately before recording

- Close email, messaging, billing and unrelated tabs.
- Clear terminal scrollback containing sensitive or irrelevant commands.
- Confirm no `.env` file or Secret Manager value is visible.
- Disable desktop notifications.
- Confirm microphone and screen resolution.
- Start a timer and stop the take if it will exceed 3:50.
