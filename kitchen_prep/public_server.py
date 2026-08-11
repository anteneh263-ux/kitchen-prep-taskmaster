"""Public, read-only FastAPI surface for kitchen plan viewing.

This app intentionally imports neither the orchestrator nor the private server.
It exposes only reads from the configured store, so the public Cloud Run service
cannot trigger a plan run through HTTP.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .data_access import store as store_da
from .render.html import render_home

app = FastAPI(
    title="Kitchen Prep Viewer",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    """Mobile-friendly view of the latest published plan."""
    plan = store_da.get_store().get_latest_plan()
    return HTMLResponse(content=render_home(plan))


@app.get("/plans/latest")
def plans_latest() -> dict[str, Any]:
    """Return the latest published plan, or a stable empty-state response."""
    plan = store_da.get_store().get_latest_plan()
    if plan is None:
        return {"detail": "no plans yet"}
    return plan


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
