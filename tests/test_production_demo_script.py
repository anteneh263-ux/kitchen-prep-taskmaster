"""Tests for the judge-safe production demo output."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_production_demo.py"
SPEC = spec_from_file_location("run_production_demo", SCRIPT)
assert SPEC and SPEC.loader
demo = module_from_spec(SPEC)
SPEC.loader.exec_module(demo)


def test_evidence_contains_only_judge_safe_summary_fields():
    run = {
        "date": "2026-08-13",
        "expected_covers": 76,
        "prep_tasks": 6,
        "prep_shortfalls": 1,
        "replenishment_orders": 13,
        "waste_flagged": 0,
        "forecast_source": "gemini",
        "forecast_note": "gemini_ok",
        "unexpected_private_payload": {"batches": ["do not print"]},
    }
    plan = {
        "briefing_source": "gemini",
        "inventory_basis": "date_input_output_snapshot",
        "planning_basis": "today_consumption_plus_par",
        "remaining_stock": {"beef_patty": 0},
    }

    evidence = demo._evidence(run, plan)

    assert evidence["forecast_source"] == "gemini"
    assert evidence["inventory_basis"] == "date_input_output_snapshot"
    assert "unexpected_private_payload" not in evidence
    assert "remaining_stock" not in evidence


def test_demo_progress_messages_do_not_contain_credentials():
    source = SCRIPT.read_text()
    assert "agent running" in source
    assert 'print(token' not in source
    assert 'Authorization: Bearer' not in source
