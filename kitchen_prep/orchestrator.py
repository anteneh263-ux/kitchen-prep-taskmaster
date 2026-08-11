"""run_daily_prep: the single orchestrated, idempotent daily pipeline.

Flow: covers -> weather -> forecast (Gemini step 1, validated, deterministic
fallback) -> ingredient requirements -> FEFO consumption + prep shortfalls ->
replenishment orders -> briefing (Gemini step 2, deterministic fallback) ->
markdown -> persist. The run log is always written (finally), even on failure.
"""
from __future__ import annotations

from datetime import date as _date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from . import config
from .contracts import Forecast
from .data_access import bookings as bookings_da
from .data_access import store as store_da
from .data_access import weather as weather_da
from .gemini import briefing_step, forecast_step
from .gemini.client import GeminiUnavailable, get_client
from .pipeline import ingredients as ingredients_pipe
from .pipeline import prep as prep_pipe
from .pipeline import replenishment as replen_pipe
from .pipeline.baseline import baseline_forecast
from .pipeline.forecast_validate import ForecastRejected, validate_and_build
from .render import markdown as md_render


def _now_oslo() -> str:
    return datetime.now(ZoneInfo(config.TIMEZONE)).isoformat(timespec="seconds")


def today_oslo() -> str:
    return datetime.now(ZoneInfo(config.TIMEZONE)).date().isoformat()


def _resolve_forecast(date: str, covers: int, weather: dict, client) -> tuple[Forecast, str]:
    """Return (forecast, note). Only model-side failures trigger the baseline."""
    weekday = _date.fromisoformat(date).weekday()
    context = forecast_step.build_context(date, covers, weather, weekday)
    try:
        raw = forecast_step.propose(client, context)
        return validate_and_build(raw), "gemini_ok"
    except GeminiUnavailable as exc:
        return baseline_forecast(date, covers), f"fallback:model_unavailable:{exc}"
    except ForecastRejected as exc:
        return baseline_forecast(date, covers), f"fallback:rejected:{exc}"


def run_daily_prep(
    date: str | None = None,
    store: store_da.BaseStore | None = None,
    client: Any | None = None,
    force: bool = False,
) -> dict:
    date = date or today_oslo()
    store = store or store_da.get_store()
    client = client or get_client()
    run_id = date
    steps: list[dict] = []

    def log(step: str, **info: Any) -> None:
        steps.append({"ts": _now_oslo(), "step": step, **info})

    status = "ok"
    error: str | None = None
    try:
        # Idempotency: same date never produces a duplicate plan.
        if not force and store.plan_exists(date):
            log("idempotent_hit")
            return store.get_plan(date)

        log("start", date=date)
        covers = bookings_da.get_expected_covers(date)
        log("covers", expected_covers=covers)

        weather = weather_da.get_weather(date)
        log("weather", **weather)

        forecast, note = _resolve_forecast(date, covers, weather, client)
        log("forecast", source=forecast.forecast_source, note=note)

        required = ingredients_pipe.explode_to_ingredients(forecast)
        log("ingredient_requirements", items=len(required))

        batches = store_da.load_seed_batches()
        consumption = prep_pipe.consume_today(required, batches, date)
        log(
            "consume_today",
            shortfalls=len(consumption["prep_shortfalls"]),
            waste=len(consumption["waste_flagged"]),
        )

        prep_tasks = prep_pipe.build_prep_tasks(forecast)
        orders = replen_pipe.compute_orders(consumption["remaining_by_item"], date)
        log("replenishment", orders=len(orders))

        remaining_stock = {
            item: round(sum(b["qty"] for b in batch_list), 3)
            for item, batch_list in consumption["remaining_by_item"].items()
        }

        plan: dict[str, Any] = {
            "date": date,
            "expected_covers": covers,
            "planning_basis": replen_pipe.PLANNING_BASIS,
            "forecast": forecast.to_dict(),
            "ingredient_requirements": required,
            "prep_tasks": prep_tasks,
            "fefo_consumption": consumption["fefo_consumption"],
            "prep_shortfalls": consumption["prep_shortfalls"],
            "replenishment_orders": orders,
            "waste_flagged": consumption["waste_flagged"],
            "remaining_stock": remaining_stock,
            "generated_at": _now_oslo(),
        }

        briefing, briefing_source = briefing_step.make_briefing(client, plan)
        plan["briefing"] = briefing
        plan["briefing_source"] = briefing_source
        plan["briefing_markdown"] = md_render.render(plan)
        log("briefing", source=briefing_source)

        saved = store.save_plan(date, plan)
        log("saved")
        return saved
    except Exception as exc:  # noqa: BLE001 - logged then re-raised (error policy)
        status = "error"
        error = repr(exc)
        raise
    finally:
        # Run log is preserved even when the pipeline fails.
        store.append_run_log(
            run_id,
            {"ts": _now_oslo(), "date": date, "status": status, "error": error, "steps": steps},
        )
