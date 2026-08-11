"""Gemini step 1: propose a demand forecast (raw). Validation happens downstream."""
from __future__ import annotations

from typing import Any


def build_context(date: str, expected_covers: int, weather: dict, weekday: int) -> dict:
    return {
        "forecast_date": date,
        "expected_covers": expected_covers,
        "weekday": weekday,
        "weather": weather,
    }


def propose(client, context: dict[str, Any]) -> dict:
    """Delegate to the model client. Raises GeminiUnavailable when offline/failed."""
    return client.propose_forecast(context)
