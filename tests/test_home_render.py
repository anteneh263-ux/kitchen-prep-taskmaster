"""Pure HTML rendering of the home page (no web framework required)."""
from kitchen_prep.render.html import render_home


def _plan():
    return {
        "date": "2026-08-14",
        "expected_covers": 80,
        "forecast": {"forecast_source": "deterministic_fallback"},
        "briefing_source": "deterministic_fallback",
        "inventory_basis": "date_input_output_snapshot",
        "covers_source": "bookings_csv",
        "planning_basis": "today_consumption_plus_par",
        "forecast_note": "fallback:model_unavailable:test",
        "generated_at": "2026-08-11T07:00:00+02:00",
        "prep_tasks": [
            {"task_id": "prep_bbq_ribs", "dish_id": "bbq_ribs", "qty": 19, "prep_minutes": 76.0, "priority": 1},
            {"task_id": "prep_classic_burger", "dish_id": "classic_burger", "qty": 45, "prep_minutes": 67.5, "priority": 2},
        ],
        "prep_shortfalls": [
            {"item_id": "beef_patty", "required": 71.0, "available": 40, "shortfall": 31.0}
        ],
        "fefo_consumption": [
            {"batch_id": "b01", "item_id": "beef_patty", "qty_consumed": 40}
        ],
        "replenishment_orders": [
            {"item_id": "burger_bun", "order_qty": 60, "unit": "stk", "supplier": "BakeryCo",
             "delivery_date": "2026-08-15"}
        ],
        "waste_flagged": [
            {"batch_id": "b06", "item_id": "pork_ribs", "qty": 7, "expiry_date": "2026-08-13"}
        ],
        "briefing": {
            "summary": "80 guests expected. One shortfall needs attention.",
            "shortfall_actions": [{
                "item_id": "beef_patty",
                "recommended_action": "Source 31 patties before service.",
                "requires_human_approval": True,
            }],
            "warnings": ["Discard expired batch b06."],
        },
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
    assert "KLAR MED BEGRENSNINGER" in html
    assert "Prognosemodellen er utilgjengelig" in html
    assert "Classic Cheeseburger" in html  # human name, not only machine id
    # Prep
    assert "bbq_ribs" in html
    # Shortfalls
    assert "Mangler før service" in html and "Burgerkjøtt" in html
    # Orders
    assert "Bestillinger" in html and "Hamburgerbrød" in html and "BakeryCo" in html
    # Waste
    assert "svinn" in html.lower() and "b06" in html


def test_render_home_status_ok_when_no_fallback():
    plan = _plan()
    plan["forecast"]["forecast_source"] = "gemini"
    plan["briefing_source"] = "gemini"
    html = render_home(plan)
    assert "KLAR" in html
    assert "KLAR MED BEGRENSNINGER" not in html


def test_render_home_handles_no_plan():
    html = render_home(None)
    assert html.lower().startswith("<!doctype html")
    assert "Ingen plan" in html


def test_render_home_supports_english():
    html = render_home(_plan(), language="en")
    assert '<html lang="en">' in html
    assert "READY WITH LIMITATIONS" in html
    assert "Expected guests" in html
    assert "Forecast" in html
    assert "date_input_output_snapshot" in html
    assert "Forecast model unavailable" in html
    assert "Service shortfalls" in html
    assert "Order proposals" in html
    assert "Waste requiring attention" in html
    assert 'href="?lang=no"' in html


def test_render_home_english_empty_state():
    html = render_home(None, language="en")
    assert '<html lang="en">' in html
    assert "No plan has been published yet." in html


def test_norwegian_view_localizes_deterministic_reasoning():
    plan = _plan()
    plan["forecast"]["dishes"] = [
        {
            "dish_id": "classic_burger",
            "expected_qty": 42,
            "confidence": "medium",
            "reasoning": "Deterministic baseline: mean of the last four Fridays.",
        }
    ]
    html = render_home(plan, language="no")
    assert "Deterministisk baseline basert på" in html
    assert "mean of the last four Fridays" not in html


def test_render_home_shows_read_only_plan_history():
    plan = _plan()
    older = dict(plan, date="2026-08-13", expected_covers=76)
    html = render_home(plan, language="en", available_plans=[plan, older])
    assert "Plan history" in html
    assert "2026-08-13 · 76 guests" in html
    assert "?lang=en&amp;date=2026-08-13" in html


def test_render_home_exposes_agent_briefing_and_human_approval_boundary():
    html = render_home(_plan(), language="en")
    assert "Approval and recommendations" in html
    assert "Review before taking external action" in html
    assert "80 guests expected. One shortfall needs attention." in html
    assert "Source 31 patties before service." in html
    assert "Approval required" in html
    assert "Discard expired batch b06." in html


def test_render_home_explains_the_autonomous_run_with_plan_evidence():
    html = render_home(_plan(), language="en")
    assert "Autonomous run" in html
    assert "Trace from operational inputs to the published plan" in html
    assert "bookings_csv" in html
    assert "deterministic_fallback" in html
    assert "Fallback activated" in html
    assert "fallback:model_unavailable:test" in html
    assert "FEFO · 1 batch uses" in html
    assert "today_consumption_plus_par" in html


def test_render_home_has_judge_focused_hero_and_navigation():
    html = render_home(_plan(), language="en")
    assert "/assets/food-hero.webp" in html
    assert "Today’s kitchen plan" in html
    assert "Action required: Source 31 pcs Beef Patty" in html
    assert "Review order" in html and "Review approval" in html
    assert "11 Aug 2026 · 07:00" in html
    assert 'datetime="2026-08-11T07:00:00+02:00"' in html
    assert 'href="#critical-actions"' in html
    assert 'href="#traceability"' in html
    assert 'href="#prep-plan"' in html
    assert 'href="#orders"' in html
    assert 'href="#forecast"' in html
    assert 'id="agent-run"' in html
    assert 'id="prep-plan"' in html
    assert 'id="orders"' in html
    assert 'id="forecast"' in html


def test_render_home_uses_natural_operational_numbers_and_dates():
    html = render_home(_plan(), language="no")
    assert "Behov: 71 stk" in html
    assert "Mangler 31 stk" in html
    assert "1 t 16 min" in html
    assert "71.0" not in html
    assert "−31.0" not in html
    assert '<time datetime="2026-08-13">13 aug.</time>' in html


def test_render_home_keeps_technical_information_collapsed():
    html = render_home(_plan(), language="no")
    assert '<details class="trace-details" id="traceability">' in html
    assert "Sporbarhet og tekniske detaljer" in html
    assert "Ingen prognosedrivere er tilgjengelige fordi reservemodellen ble brukt." in html


def test_render_home_only_shows_mutating_controls_in_private_mode():
    public_html = render_home(_plan(), language="no")
    private_html = render_home(_plan(), language="no", interactive=True)
    assert 'method="post"' not in public_html
    assert "Se bestillingsforslag" in public_html
    assert 'method="post"' in private_html
    assert "/actions/beef_patty/approved?lang=no" in private_html
    assert "Marker som løst" in private_html


def test_render_home_marks_successful_forecast_validation():
    plan = _plan()
    plan["forecast"]["forecast_source"] = "gemini"
    plan["forecast"]["dishes"] = [{"dish_id": "classic_burger", "expected_qty": 42}]
    plan["forecast_note"] = "gemini_ok"
    plan["briefing_source"] = "gemini"
    html = render_home(plan, language="en")
    assert "Proposal accepted" in html
    assert "gemini_ok" in html
    assert "1 dish predictions" in html


def test_render_home_escapes_agent_briefing_content():
    plan = _plan()
    plan["briefing"]["summary"] = '<script>alert("x")</script>'
    plan["briefing"]["shortfall_actions"][0]["recommended_action"] = "<b>unsafe</b>"
    html = render_home(plan, language="en")
    assert "<script>" not in html
    assert "<b>unsafe</b>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;unsafe&lt;/b&gt;" in html
