# Four-Minute Demo Script

For the final shot-by-shot production plan, captions and visual direction, use
[`video_storyboard.md`](video_storyboard.md). This file remains the compact
narration reference.

Target duration: **3:54**. English narration is synchronized scene by scene.
Keep the browser and evidence-card text large enough to remain readable in the
Devpost player; the approved master uses no terminal footage.

## 0:00–0:30 — Problem and value

> A restaurant kitchen starts every day by guessing what to prep, what will run
> short, what should be ordered, and which stock will expire. Kitchen Prep
> Taskmaster turns that multi-step morning chore into one unattended workflow.
> It forecasts demand, validates the model output, calculates prep and ordering
> deterministically, applies first-expired-first-out inventory consumption, and
> publishes one operational briefing before service.

Show the English public viewer:

https://kitchen-prep-viewer-373405758807.europe-north1.run.app

## 0:30–1:05 — Architecture and safety boundary

Show the architecture diagram in `docs/architecture.md`.

> Cloud Scheduler triggers a private Cloud Run worker at 07:00 Europe/Oslo.
> The production workflow uses Gemini 3.5 Flash through the Google Gen AI SDK
> for exactly two schema-bounded judgment steps: forecasting and briefing.
> Deterministic Python owns recipe expansion, FEFO inventory consumption,
> shortfalls and order quantities. Every model proposal is validated, and a
> deterministic fallback keeps the kitchen running if the model is unavailable
> or returns an invalid forecast. Firestore stores the plan and audit log. A
> separate public service can only read plans; it cannot trigger a run and has
> no Gemini secret. Dated inventory snapshots make retries and forced reruns
> replay-safe, so the same stock is never consumed twice.

## 1:05–1:35 — Visible Google Cloud proof

Show the Google Cloud Run service page for `kitchen-prep-taskmaster-web` and make
the following visible:

- project `kitchen-prep-taskmaster-263`;
- region `europe-north1`;
- latest ready revision;
- 100% traffic;
- authentication required.

The expected worker revision is `kitchen-prep-taskmaster-web-00011-vlp`. The
public viewer revision is `kitchen-prep-viewer-00010-xlk`.

Then briefly show Cloud Scheduler job `kitchen-prep-daily`, enabled with schedule
`0 7 * * *` and timezone `Europe/Oslo`.

> The mutation surface is private and invoked with OIDC. The public judge viewer
> runs under a different service account with Firestore viewer permission only.

## 1:35–2:30 — Autonomous execution and verified result

Show the clean five-stage execution sequence: Inputs → AI forecast → Validation
→ Inventory → Publish. Follow it with the verified result card and then the
refreshed public viewer. No shell prompt, username, token or private inventory
payload appears in the approved master.

> Operational inputs enter the private worker. Gemini proposes demand. Python
> validates the proposal, applies first-expired-first-out inventory consumption,
> calculates shortages and replenishment, and publishes one replay-safe plan to
> Firestore. Each stage is bounded, observable and auditable.

## 2:30–3:10 — Proof of action

Point to these live results in the viewer:

- the five-step **Autonomous run** evidence path;
- expected guests;
- forecast and briefing sources;
- `OPERATIONAL` or clearly disclosed degraded status;
- the current dated inventory basis (`date_input_output_snapshot` or the
  explicitly disclosed `epoch_seed_snapshot` migration boundary);
- prioritized prep tasks;
- today's shortfalls;
- replenishment orders and delivery dates;
- expired-batch waste.
- the **Agent briefing** recommendation and human-approval boundary.

> This is not model-written prose pretending to take action. The workflow has
> transformed bookings, weather, sales history, recipes and inventory batches
> into a validated plan stored in Firestore. The model provides judgment, while
> deterministic code owns every quantity a cook or supplier would act on. The
> dated inventory basis also proves that a forced replay starts from the same
> frozen stock snapshot instead of consuming the previous output again.

## 3:10–3:40 — Reliability and reproducibility

Show the prepared test-evidence card or the GitHub repository test section.

> The repository contains reproducible local and Cloud Run setup instructions,
> a complete architecture document, synthetic data and 128 passing tests. It
> tests forecast contracts, fallback behavior, FEFO, idempotency, forced plan
> replacement, API security and the English judge interface. The worker stays
> private, while the read-only viewer remains available to judges.

## 3:40–3:50 — Close

> Kitchen Prep Taskmaster removes a real daily operational burden: one secure,
> observable, autonomous workflow instead of a morning of guesswork.

## Recording checklist

- Do not show API keys, Secret Manager values, identity tokens, email inboxes or
  unrelated browser tabs.
- Keep the video publicly visible on YouTube or Vimeo, not private or unlisted.
- Confirm the final uploaded duration is below four minutes.
- Put the hosted viewer, repository and video URLs in the Devpost submission.
- Mention that the video was created for entry into the All Things Agentic
  Hackathon if the same public video is also used for the optional content bonus.
