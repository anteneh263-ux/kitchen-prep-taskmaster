"""Deterministic baseline forecast: average qty for the same weekday over the
last 4 occurrences strictly before the target date."""
from __future__ import annotations

from ..contracts import DishForecast, Forecast
from ..data_access import menu as menu_da
from ..data_access import sales as sales_da

WEEKDAY_NAMES = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]


def baseline_forecast(date: str, expected_covers: int) -> Forecast:
    from datetime import date as _date

    weekday = _date.fromisoformat(date).weekday()
    dishes: list[DishForecast] = []
    for dish_id in menu_da.dish_ids():
        history = sales_da.same_weekday_history(date, dish_id, weeks=4)
        qty = round(sum(history) / len(history)) if history else 0
        dishes.append(
            DishForecast(
                dish_id=dish_id,
                expected_qty=int(qty),
                confidence="medium",
                reasoning=(
                    f"Deterministisk baseline: snitt siste {len(history)} "
                    f"{WEEKDAY_NAMES[weekday]}(er) = {qty}"
                ),
            )
        )
    return Forecast(
        forecast_date=date,
        expected_covers=expected_covers,
        dishes=dishes,
        drivers=["deterministic_baseline"],
        forecast_source="deterministic_fallback",
    )
