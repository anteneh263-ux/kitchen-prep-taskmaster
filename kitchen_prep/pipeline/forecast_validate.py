"""Validation of a proposed (Gemini) forecast against the locked rules.

Reject when: a menu dish is missing, an unknown dish_id appears, expected_qty is
negative or not an integer, or the total dishes-per-cover ratio falls outside the
+/-30% band. On rejection the caller switches to the deterministic baseline.
"""
from __future__ import annotations

from .. import config
from ..contracts import DishForecast, Forecast
from ..data_access import menu as menu_da


class ForecastRejected(ValueError):
    """Raised when a proposed forecast violates the contract."""


def validate_and_build(proposed: dict) -> Forecast:
    menu_ids = set(menu_da.dish_ids())

    if not isinstance(proposed, dict):
        raise ForecastRejected("forecast is not an object")

    covers = proposed.get("expected_covers")
    if not isinstance(covers, int) or covers <= 0:
        raise ForecastRejected("expected_covers must be a positive integer")

    raw_dishes = proposed.get("dishes")
    if not isinstance(raw_dishes, list):
        raise ForecastRejected("dishes must be a list")

    seen: dict[str, int] = {}
    dish_objs: list[DishForecast] = []
    for d in raw_dishes:
        did = d.get("dish_id")
        qty = d.get("expected_qty")
        if did not in menu_ids:
            raise ForecastRejected(f"unknown dish_id: {did!r}")
        if isinstance(qty, bool) or not isinstance(qty, int):
            raise ForecastRejected(f"expected_qty for {did} must be an integer")
        if qty < 0:
            raise ForecastRejected(f"expected_qty for {did} is negative")
        seen[did] = qty
        dish_objs.append(
            DishForecast(
                dish_id=did,
                expected_qty=qty,
                confidence=d.get("confidence", "medium"),
                reasoning=d.get("reasoning", ""),
            )
        )

    missing = menu_ids - set(seen)
    if missing:
        raise ForecastRejected(f"missing dishes: {sorted(missing)}")

    total = sum(seen.values())
    ratio = total / covers
    if not (config.RATIO_MIN <= ratio <= config.RATIO_MAX):
        raise ForecastRejected(
            f"dishes-per-cover ratio {ratio:.3f} outside "
            f"[{config.RATIO_MIN}, {config.RATIO_MAX}]"
        )

    return Forecast(
        forecast_date=proposed["forecast_date"],
        expected_covers=covers,
        dishes=dish_objs,
        drivers=list(proposed.get("drivers", [])),
        forecast_source="gemini",
    )
