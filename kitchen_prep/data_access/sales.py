"""Read generated sales history."""
from __future__ import annotations

import csv
from datetime import date as _date

from .. import config


def load_sales_rows() -> list[dict]:
    rows: list[dict] = []
    with open(config.SALES_HISTORY_PATH, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(
                {
                    "date": r["date"],
                    "dish_id": r["dish_id"],
                    "qty_sold": int(r["qty_sold"]),
                    "covers": int(r["covers"]),
                    "weather_code": int(r["weather_code"]),
                    "temperature_c": float(r["temperature_c"]),
                    "precipitation_mm": float(r["precipitation_mm"]),
                }
            )
    return rows


def same_weekday_history(target_date: str, dish_id: str, weeks: int = 4) -> list[int]:
    """Return qty_sold for the last ``weeks`` occurrences of the target weekday
    strictly before ``target_date`` (guards against future leakage)."""
    target = _date.fromisoformat(target_date)
    weekday = target.weekday()
    hits = [
        (row["date"], row["qty_sold"])
        for row in load_sales_rows()
        if row["dish_id"] == dish_id
        and _date.fromisoformat(row["date"]) < target
        and _date.fromisoformat(row["date"]).weekday() == weekday
    ]
    hits.sort(key=lambda x: x[0])
    return [q for _, q in hits[-weeks:]]
