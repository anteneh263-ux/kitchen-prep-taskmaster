"""FastAPI service for Cloud Run.

Endpoints:
  POST /runs/daily   -> start the idempotent daily run (optional {"date": ...})
  GET  /plans/latest -> latest published plan (simple mobile view)
  GET  /healthz      -> liveness

Authentication is enforced at the edge: Cloud Scheduler invokes Cloud Run with an
OIDC token and the service is deployed with --no-allow-unauthenticated (see
deploy/scheduler.md). The run date defaults to today's date in Europe/Oslo.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .orchestrator import run_daily_prep, today_oslo
from .data_access import store as store_da
from .render.html import render_home

app = FastAPI(title="Kitchen Prep Taskmaster")


class RunRequest(BaseModel):
    date: str | None = None
    force: bool = False


@app.get("/", response_class=HTMLResponse)
def home(lang: str = "no") -> HTMLResponse:
    """Mobile-friendly server-rendered view of the latest published plan."""
    plan = store_da.get_store().get_latest_plan()
    return HTMLResponse(content=render_home(plan, language=lang))


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs/daily")
def runs_daily(req: RunRequest | None = None) -> dict[str, Any]:
    req = req or RunRequest()
    date = req.date or today_oslo()
    plan = run_daily_prep(date=date, force=req.force)
    # Idempotent summary; the full plan is available via /plans/latest.
    return {
        "date": plan["date"],
        "expected_covers": plan["expected_covers"],
        "prep_tasks": len(plan["prep_tasks"]),
        "prep_shortfalls": len(plan["prep_shortfalls"]),
        "replenishment_orders": len(plan["replenishment_orders"]),
        "waste_flagged": len(plan["waste_flagged"]),
        "forecast_source": plan["forecast"]["forecast_source"],
        "forecast_note": plan.get("forecast_note", "unavailable"),
    }


@app.get("/plans/latest")
def plans_latest() -> dict[str, Any]:
    plan = store_da.get_store().get_latest_plan()
    if plan is None:
        return {"detail": "no plans yet"}
    return plan
