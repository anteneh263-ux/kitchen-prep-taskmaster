"""Public, read-only FastAPI surface for kitchen plan viewing.

This app intentionally imports neither the orchestrator nor the private server.
It exposes only reads from the configured store, so the public Cloud Run service
cannot trigger a plan run through HTTP.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from .data_access import store as store_da
from .render.html import render_home

app = FastAPI(
    title="Kitchen Prep Viewer",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
_HERO_IMAGE = Path(__file__).parent / "assets" / "food-hero.webp"


def _plan_summary(plan: dict[str, Any]) -> dict[str, Any]:
    """Stable public summary without inventory or model reasoning payloads."""
    return {
        "date": plan["date"],
        "generated_at": plan.get("generated_at"),
        "expected_covers": plan.get("expected_covers"),
        "forecast_source": plan.get("forecast", {}).get("forecast_source"),
        "briefing_source": plan.get("briefing_source"),
        "prep_tasks": len(plan.get("prep_tasks", [])),
        "prep_shortfalls": len(plan.get("prep_shortfalls", [])),
        "replenishment_orders": len(plan.get("replenishment_orders", [])),
        "waste_flagged": len(plan.get("waste_flagged", [])),
    }


@app.get("/", response_class=HTMLResponse)
def home(lang: str = "en", date: str | None = None) -> HTMLResponse:
    """Mobile-friendly view of the latest published plan."""
    store = store_da.get_store()
    plans = store.list_plans(limit=14)
    plan = store.get_plan(date) if date else (plans[0] if plans else None)
    return HTMLResponse(content=render_home(plan, language=lang, available_plans=plans))


@app.get("/assets/food-hero.webp", include_in_schema=False)
def food_hero() -> FileResponse:
    return FileResponse(_HERO_IMAGE, media_type="image/webp", headers={"Cache-Control": "public, max-age=86400"})


@app.get("/plans/latest")
def plans_latest() -> dict[str, Any]:
    """Return the latest published plan, or a stable empty-state response."""
    plan = store_da.get_store().get_latest_plan()
    if plan is None:
        return {"detail": "no plans yet"}
    return plan


@app.get("/plans")
def plans_history(limit: int = 14) -> list[dict[str, Any]]:
    """Return capped plan summaries for read-only history navigation."""
    safe_limit = max(1, min(limit, 31))
    return [_plan_summary(plan) for plan in store_da.get_store().list_plans(safe_limit)]


@app.get("/plans/{date}")
def plan_by_date(date: str) -> dict[str, Any]:
    plan = store_da.get_store().get_plan(date)
    if plan is None:
        return {"detail": "plan not found", "date": date}
    return plan


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
