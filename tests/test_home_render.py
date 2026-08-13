"""Pure HTML rendering of the home page (no web framework required)."""
from kitchen_prep.render.html import render_home


def _plan():
    return {
        "date": "2026-08-14",
        "expected_covers": 80,
        "forecast": {"forecast_source": "deterministic_fallback"},
        "briefing_source": "deterministic_fallback",
        "generated_at": "2026-08-11T07:00:00+02:00",
        "prep_tasks": [
            {"task_id": "prep_bbq_ribs", "dish_id": "bbq_ribs", "qty": 19, "prep_minutes": 76.0, "priority": 1},
            {"task_id": "prep_classic_burger", "dish_id": "classic_burger", "qty": 45, "prep_minutes": 67.5, "priority": 2},
        ],
        "prep_shortfalls": [
            {"item_id": "beef_patty", "required": 71.0, "available": 40, "shortfall": 31.0}
        ],
        "replenishment_orders": [
            {"item_id": "burger_bun", "order_qty": 60, "unit": "stk", "supplier": "BakeryCo",
             "delivery_date": "2026-08-15"}
        ],
        "waste_flagged": [
            {"batch_id": "b06", "item_id": "pork_ribs", "qty": 7, "expiry_date": "2026-08-13"}
        ],
    }


def test_render_home_is_html_document():
    html = render_home(_plan())
    low = html.lower()
    assert low.startswith("<!doctype html")
    assert "<html" in low and "</html>" in low
    assert '<meta name="viewport"' in html  # mobile-friendly


def test_render_home_contains_all_sections():
    html = render_home(_plan())
    # Header + sources + status + timestamp
    assert "2026-08-14" in html
    assert "80" in html
    assert "deterministic_fallback" in html
    assert "2026-08-11T07:00:00+02:00" in html
    assert "DEGRADERT" in html  # run status reflects fallback
    # Prep
    assert "bbq_ribs" in html
    # Shortfalls
    assert "Mangler i dag" in html and "beef_patty" in html
    # Orders
    assert "Bestillinger" in html and "burger_bun" in html and "BakeryCo" in html
    # Waste
    assert "Svinn" in html and "b06" in html


def test_render_home_status_ok_when_no_fallback():
    plan = _plan()
    plan["forecast"]["forecast_source"] = "gemini"
    plan["briefing_source"] = "gemini"
    html = render_home(plan)
    assert ">OK<" in html
    assert "DEGRADERT" not in html


def test_render_home_handles_no_plan():
    html = render_home(None)
    assert html.lower().startswith("<!doctype html")
    assert "Ingen plan" in html


def test_render_home_supports_english():
    html = render_home(_plan(), language="en")
    assert '<html lang="en">' in html
    assert "Kitchen briefing" in html
    assert "80</strong> expected guests" in html
    assert "Forecast source" in html
    assert "DEGRADED (fallback used)" in html
    assert "Today’s shortfalls" in html
    assert "Replenishment orders" in html
    assert "Waste (expired batches)" in html
    assert 'href="?lang=no"' in html


def test_render_home_english_empty_state():
    html = render_home(None, language="en")
    assert '<html lang="en">' in html
    assert "No plan has been published yet." in html
