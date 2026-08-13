"""Inventory snapshots carry stock forward without double-consuming on replay."""
import json

from kitchen_prep import config
from kitchen_prep.data_access.store import LocalJsonStore
from kitchen_prep.gemini.client import OfflineClient
from kitchen_prep.orchestrator import run_daily_prep


def _snapshot(store: LocalJsonStore, date: str) -> dict:
    return json.loads((store.inventory_dir / f"{date}.json").read_text())


def test_next_day_starts_from_previous_output(tmp_store):
    first = run_daily_prep(config.DEMO_DATE, store=tmp_store, client=OfflineClient())
    assert first["inventory_basis"] == "date_input_output_snapshot"
    next_date = "2026-08-15"
    run_daily_prep(next_date, store=tmp_store, client=OfflineClient())

    first_snapshot = _snapshot(tmp_store, config.DEMO_DATE)
    next_snapshot = _snapshot(tmp_store, next_date)
    assert next_snapshot["input_batches"] == first_snapshot["output_batches"]
    assert sum(first["remaining_stock"].values()) == sum(
        batch["qty"] for batch in next_snapshot["input_batches"]
    )


def test_force_replays_same_input_and_does_not_double_consume(tmp_store):
    original = run_daily_prep(config.DEMO_DATE, store=tmp_store, client=OfflineClient())
    before = _snapshot(tmp_store, config.DEMO_DATE)

    replayed = run_daily_prep(
        config.DEMO_DATE,
        store=tmp_store,
        client=OfflineClient(),
        force=True,
    )
    after = _snapshot(tmp_store, config.DEMO_DATE)

    assert after["input_batches"] == before["input_batches"]
    assert after["output_batches"] == before["output_batches"]
    assert replayed["remaining_stock"] == original["remaining_stock"]
    assert replayed["fefo_consumption"] == original["fefo_consumption"]


def test_idempotent_hit_does_not_change_inventory_snapshot(tmp_store):
    plan = run_daily_prep(config.DEMO_DATE, store=tmp_store, client=OfflineClient())
    before = _snapshot(tmp_store, config.DEMO_DATE)
    returned = run_daily_prep(config.DEMO_DATE, store=tmp_store, client=OfflineClient())
    after = _snapshot(tmp_store, config.DEMO_DATE)
    assert returned == plan
    assert after == before


def test_empty_previous_output_is_not_reseeded(tmp_store):
    date1 = "2026-08-14"
    date2 = "2026-08-15"
    tmp_store.get_or_create_inventory_input(date1, [{"batch_id": "x"}])
    tmp_store.save_inventory_output(date1, [])
    assert tmp_store.get_or_create_inventory_input(date2, [{"batch_id": "seed"}]) == []
