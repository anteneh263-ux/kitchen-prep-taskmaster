# Demo Recording Runbook

Use the timed scene plan and final English narration in
[`video_storyboard.md`](video_storyboard.md). This runbook covers the operational
setup for that recording.

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
python scripts/recording_preflight.py
```

Do not start the take unless the final line says `READY TO RECORD`. The preflight
is read-only: it does not invoke the worker or change Firestore.

During the unedited live execution, run:

```bash
python scripts/run_production_demo.py
```

The script obtains the identity token internally and never prints it. Its compact
evidence output should show `forecast_source: gemini`, `forecast_note: gemini_ok`,
`briefing_source: gemini`, `date_input_output_snapshot` and
`today_consumption_plus_par`.

Refresh the public dashboard and point out:

- `OPERATIONAL`;
- the five-step **Autonomous run** panel;
- Gemini forecast and briefing sources;
- `date_input_output_snapshot`;
- prioritized prep and readable dish names;
- today's shortfalls;
- replenishment orders;
- forecast drivers and reasoning;
- the **Agent briefing** human-approval boundary;
- plan history.

## Test evidence

Prepare this output before recording, or run it if timing permits:

```bash
pytest -q
```

Expected offline result: `124 passed, 1 skipped`. The skipped test is the
credentialed integration test; the live production execution is the evidence for
that path.

## Safety check immediately before recording

- Close email, messaging, billing and unrelated tabs.
- Clear terminal scrollback containing sensitive or irrelevant commands.
- Confirm no `.env` file or Secret Manager value is visible.
- Disable desktop notifications.
- Confirm microphone and screen resolution.
- Start a timer and stop the take if it will exceed 3:50.
