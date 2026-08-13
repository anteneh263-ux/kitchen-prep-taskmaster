# Competition Demo Storyboard

Target length: **3:35–3:50**. Language: English. Format: 16:9, 1080p.

This is a competition proof video, not a generic product commercial. Use the
rhythm of a polished SaaS explainer, but preserve one continuous recording and
show the real production run. Every spoken claim must have visible evidence.

## Message

- **Primary audience:** All Things Agentic Hackathon judges.
- **Operational user:** an independent restaurant kitchen manager.
- **Problem:** the daily prep-and-ordering plan is assembled manually from
  disconnected demand, recipe and inventory information.
- **Promise:** one autonomous agent produces the plan every morning and shows
  exactly how it reached the result.
- **Three proof points:** unattended execution; bounded and validated Gemini
  judgment; deterministic FEFO, shortfall and replenishment arithmetic.
- **Outcome:** a ready-to-use plan with visible sources, fallback state, human
  approval boundaries and an audit trail.
- **Call to action:** open the live read-only dashboard and inspect the evidence.

## Scene-by-scene plan

| Time | Voiceover | On-screen evidence | Motion |
|---|---|---|---|
| 0:00–0:18 | “Every morning, a restaurant must decide what to prep, what will run short, and what to order—before service begins. Kitchen Prep Taskmaster completes that whole job automatically, and shows its work.” | Dashboard hero and four KPIs. Headline overlay: **A complete kitchen plan before service.** | Begin on clean hero; slow scroll to KPIs. |
| 0:18–0:42 | “At 07:00, Cloud Scheduler securely triggers a private Cloud Run worker. No chat and no button click. The agent combines bookings, weather, sales history, recipes and batch inventory, then publishes one operational plan.” | Architecture diagram, framed tightly around Scheduler → worker → pipeline → Firestore → viewer. | One deliberate cursor trace across the pipeline. |
| 0:42–1:05 | “Gemini has two bounded jobs: propose dish demand and write the briefing. Python validates the proposal before it can affect operations. Ingredient expansion, FEFO consumption, shortfalls, order quantities and delivery dates remain deterministic.” | Architecture safety boundary, then dashboard **Autonomous run** panel. | Move from diagram to steps 2–4 in the panel. |
| 1:05–1:24 | “If Gemini is unavailable or returns an invalid proposal, the agent activates a deterministic baseline and visibly marks the degraded path. It keeps running without hiding what happened.” | Run-integrity sources and validation step. Do not claim fallback occurred in the current operational run unless the screen shows it. | Point to `gemini`, `gemini_ok` and operational status; briefly mention the tested alternate path verbally. |
| 1:24–1:42 | “The mutation endpoint is private. The public judge viewer uses a separate identity with read-only Firestore access and no Gemini secret.” | Cloud Run worker: authentication required and 100% traffic. Then public viewer service identity/traffic if readable. | Two prepared Cloud Console tabs; no navigation into secrets. |
| 1:42–1:54 | “The same worker is scheduled every day at seven in the morning, Europe/Oslo.” | Cloud Scheduler job name, enabled state, `0 7 * * *`, timezone. | Static proof shot. |
| 1:54–2:32 | “Now I’ll run the real production agent. The command obtains authentication internally and prints only judge-safe evidence—not the identity token or full inventory payload.” After completion: “Gemini produced and passed the forecast, Gemini produced the briefing, and the plan used replay-safe dated inventory with deterministic post-consumption ordering.” | Terminal running `python scripts/run_production_demo.py`. Keep the whole wait visible and uncut. Output must show `gemini`, `gemini_ok`, `date_input_output_snapshot` and `today_consumption_plus_par`. | Single live terminal shot. Do not switch away while it runs. |
| 2:32–3:12 | “The refreshed plan traces the same run from the live guest input through dish forecasts, validation, FEFO batch withdrawals and publication. The kitchen receives prioritized prep, today’s shortfall separately from future orders, and supplier delivery dates.” Read the current counts from the screen rather than memorizing demo-day values. | Refresh dashboard. Show **Autonomous run**, prioritized prep, shortfall and replenishment. | Smooth vertical scroll; pause on each evidence group. |
| 3:12–3:28 | “The agent briefing recommends how to resolve the shortage, but marks that action for human approval. Gemini provides judgment; deterministic code owns the quantities.” If the live plan has no shortage, say that no approval action was needed today. | **Agent briefing**, current recommendation and **Human approval required** badge when present. | Hold long enough for the current action or empty state to be read. |
| 3:28–3:40 | “The repository includes reproducible deployment instructions and 124 passing tests covering validation, fallback, FEFO, replay safety and public-route security.” | Prepared terminal test result or GitHub test evidence. | Static proof shot. |
| 3:40–3:50 | “Kitchen Prep Taskmaster is the autonomous kitchen agent that runs the daily loop and shows its work. Open the live read-only plan and inspect the evidence.” | Dashboard hero plus hosted URL and GitHub URL. | Return to hero; simple fade only after the continuous proof is complete. |

## Visual system

- Use the dashboard's dark green, off-white and restrained red warning accent.
- Use one sans-serif typeface and large English captions.
- Keep browser zoom high enough to read every proof value at 1080p.
- Prefer prepared tabs and smooth scrolling over decorative animation.
- Use no stock footage or generic AI imagery; the working product is the visual.
- Background music is optional and must remain well below narration.
- Captions are required for silent viewing.

## Recording order

Prepare exactly these surfaces before recording:

1. English public dashboard at the top.
2. Architecture diagram.
3. Private Cloud Run worker revision and traffic.
4. Enabled Cloud Scheduler job.
5. Clean terminal in the repository directory.
6. Test-result evidence.

Close unrelated tabs, disable notifications and clear sensitive terminal
scrollback. Do not open Secret Manager. Run `python scripts/run_production_demo.py`
only during the take so the live execution remains genuine.

Immediately before recording, run `python scripts/recording_preflight.py`. It is
read-only and must end with `READY TO RECORD`.

## Acceptance check

- Target user and problem are clear within 18 seconds.
- The central idea is repeatable: **runs itself and shows its work**.
- The live agent execution is continuous and unedited.
- Every technical claim has a visible value, route boundary or architecture box.
- The video remains understandable with captions and no sound.
- Duration is below four minutes.
- Final CTA points to the credential-free viewer, not a sales or sign-up flow.
