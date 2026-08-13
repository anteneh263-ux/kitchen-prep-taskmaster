import pytest

from kitchen_prep.contracts import validate_briefing
from kitchen_prep.gemini.briefing_step import build_deterministic_briefing


def _plan():
    return {
        "date": "2026-08-14",
        "expected_covers": 80,
        "forecast": {"forecast_source": "deterministic_fallback"},
        "prep_tasks": [
            {"task_id": "prep_bbq_ribs", "dish_id": "bbq_ribs", "qty": 20, "prep_minutes": 80.0, "priority": 1},
            {"task_id": "prep_classic_burger", "dish_id": "classic_burger", "qty": 42, "prep_minutes": 63.0, "priority": 2},
        ],
        "prep_shortfalls": [
            {"item_id": "beef_patty", "required": 67, "available": 40, "shortfall": 27}
        ],
        "replenishment_orders": [{"item_id": "beef_patty"}],
        "waste_flagged": [
            {"batch_id": "b06", "item_id": "pork_ribs", "qty": 7, "expiry_date": "2026-08-13"}
        ],
    }


def test_deterministic_briefing_matches_contract():
    b = build_deterministic_briefing(_plan())
    validate_briefing(b)  # raises on any contract violation
    assert b["priority_task_ids"] == ["prep_bbq_ribs", "prep_classic_burger"]
    assert b["shortfall_actions"][0]["item_id"] == "beef_patty"
    assert b["shortfall_actions"][0]["requires_human_approval"] is True
    assert "Today's shortfall" in b["shortfall_actions"][0]["recommended_action"]
    assert "guests expected" in b["summary"]
    assert any("b06" in w for w in b["warnings"])


def test_validate_briefing_rejects_bad_types():
    with pytest.raises(ValueError):
        validate_briefing({"summary": "", "priority_task_ids": [], "shortfall_actions": [], "warnings": []})
    with pytest.raises(ValueError):
        validate_briefing({"summary": "x", "priority_task_ids": "no", "shortfall_actions": [], "warnings": []})
