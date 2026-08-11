"""Read bookings (authoritative expected covers per date)."""
from __future__ import annotations

import csv
from functools import lru_cache

from .. import config


@lru_cache(maxsize=1)
def _load() -> dict[str, int]:
    out: dict[str, int] = {}
    with open(config.BOOKINGS_PATH, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["date"]] = int(row["expected_covers"])
    return out


def get_expected_covers(date: str) -> int:
    bookings = _load()
    if date not in bookings:
        raise KeyError(f"No booking (expected_covers) for date {date}")
    return bookings[date]
