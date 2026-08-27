"""Pure HTML rendering of the home page (no web framework required)."""
import pytest

from kitchen_prep.data_access import menu as menu_da
from kitchen_prep.render.html import render_home
from kitchen_prep.units import UnitResolutionError, ingredient_unit, unit_label


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


# --- Units --------------------------------------------------------------
# The ingredient master is authoritative: bbq_sauce is litres, chicken_wings is
# kilograms. Every fixture above uses beef_patty/burger_bun (stk), which is why
# a hardcoded "pcs" went unnoticed; these plans exercise the non-piece units.


def _plan_non_piece_units():
    plan = _plan()
    plan["prep_tasks"] = [
        {"task_id": "prep_bbq_wings", "dish_id": "bbq_wings", "qty": 16,
         "prep_minutes": 32.0, "priority": 1},
    ]
    plan["prep_shortfalls"] = [
        {"item_id": "bbq_sauce", "required": 6.2, "available": 4.0, "shortfall": 2.2},
        {"item_id": "chicken_wings", "required": 11.5, "available": 9.0, "shortfall": 2.5},
    ]
    plan["replenishment_orders"] = [
        {"item_id": "bbq_sauce", "order_qty": 5, "unit": "l", "supplier": "DryGoods",
         "delivery_date": "2026-08-17"},
        {"item_id": "chicken_wings", "order_qty": 10, "unit": "kg", "supplier": "MeatCo",
         "delivery_date": "2026-08-16"},
    ]
    plan["waste_flagged"] = [
        {"batch_id": "b10", "item_id": "bbq_sauce", "qty": 1.5, "expiry_date": "2026-08-13"},
    ]
    plan["briefing"]["shortfall_actions"] = [
        {"item_id": "bbq_sauce", "recommended_action": "Source 2.2 l before service.",
         "requires_human_approval": True},
    ]
    return plan


def test_bbq_sauce_shortfall_uses_litres_on_every_html_surface():
    html = render_home(_plan_non_piece_units(), language="en")
    # Shortfall card: available, required, missing.
    assert "Available: 4 l · Required: 6.2 l" in html
    assert "Missing 2.2 l" in html
    # Critical-action hero banner (first shortfall).
    assert "Action required: Source 2.2 l Bbq Sauce" in html
    # Order table.
    assert "<td>5 l</td>" in html


def test_chicken_wings_shortfall_uses_kilograms_on_every_html_surface():
    html = render_home(_plan_non_piece_units(), language="en")
    assert "Available: 9 kg · Required: 11.5 kg" in html
    assert "Missing 2.5 kg" in html
    assert "<td>10 kg</td>" in html


def test_non_piece_plan_never_renders_a_piece_unit():
    for language in ("en", "no"):
        html = render_home(_plan_non_piece_units(), language=language)
        assert "pcs" not in html
        assert " stk" not in html


def test_norwegian_uses_litres_and_kilograms_for_these_ingredients():
    html = render_home(_plan_non_piece_units(), language="no")
    assert "Tilgjengelig: 4 l · Behov: 6.2 l" in html
    assert "Mangler 2.2 l" in html
    assert "Mangler 2.5 kg" in html
    assert "Skaff 2.2 l Bbq Sauce" in html          # hero banner
    assert "Skaff 2.2 l Bbq Sauce før service." in html  # Norwegian action text


def test_order_and_shortfall_agree_on_the_unit_for_the_same_ingredient():
    plan = _plan_non_piece_units()
    for language in ("en", "no"):
        html = render_home(plan, language=language)
        for order in plan["replenishment_orders"]:
            shortfall = next(
                s for s in plan["prep_shortfalls"] if s["item_id"] == order["item_id"]
            )
            unit = ingredient_unit(order["item_id"], language)
            assert unit == unit_label(order["unit"], language)
            missing = "Missing" if language == "en" else "Mangler"
            assert f'{missing} {shortfall["shortfall"]:g} {unit}' in html
            assert f'<td>{order["order_qty"]:g} {unit}</td>' in html


def test_waste_rows_carry_the_authoritative_unit():
    assert "1.5 l" in render_home(_plan_non_piece_units(), language="en")
    # pork_ribs is kilograms in the ingredient master.
    assert "7 kg" in render_home(_plan(), language="en")


def test_piece_ingredients_still_render_pcs_and_stk():
    # beef_patty is "stk": English "pcs", Norwegian "stk". Unchanged behaviour.
    en = render_home(_plan(), language="en")
    assert "Available: 40 pcs · Required: 71 pcs" in en
    assert "Missing 31 pcs" in en
    assert "Action required: Source 31 pcs Beef Patty" in en
    no = render_home(_plan(), language="no")
    assert "Tilgjengelig: 40 stk · Behov: 71 stk" in no
    assert "Mangler 31 stk" in no


def test_prep_task_quantities_are_portions_not_ingredient_pieces():
    en = render_home(_plan(), language="en")
    assert "19 portions" in en   # prep row
    assert "45 portions" in en
    no = render_home(_plan(), language="no")
    assert "19 porsjoner" in no
    assert "45 porsjoner" in no


def test_unknown_ingredient_id_fails_clearly():
    plan = _plan()
    plan["prep_shortfalls"] = [
        {"item_id": "unicorn_steak", "required": 1, "available": 0, "shortfall": 1}
    ]
    with pytest.raises(UnitResolutionError, match="unknown ingredient id 'unicorn_steak'"):
        render_home(plan, language="en")


def test_unsupported_unit_fails_clearly():
    with pytest.raises(UnitResolutionError, match="unsupported unit 'lbs'"):
        unit_label("lbs", "en")


def test_missing_unit_on_an_ingredient_fails_clearly(monkeypatch):
    broken = {k: dict(v) for k, v in menu_da.ingredients_by_id().items()}
    broken["bbq_sauce"].pop("unit")
    monkeypatch.setattr(menu_da, "ingredients_by_id", lambda: broken)
    with pytest.raises(UnitResolutionError, match="ingredient 'bbq_sauce'"):
        ingredient_unit("bbq_sauce", "en")
