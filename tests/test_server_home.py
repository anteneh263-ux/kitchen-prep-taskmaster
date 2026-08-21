"""Route-level checks for GET / and GET /plans/latest.

Requires FastAPI + a test client. Skipped where FastAPI is not installed (e.g. an
offline sandbox); it runs unchanged wherever the project's declared dependencies
are present.
"""
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from kitchen_prep import config  # noqa: E402
from kitchen_prep.gemini.client import OfflineClient  # noqa: E402
from kitchen_prep.orchestrator import run_daily_prep  # noqa: E402


@pytest.fixture()
def client_with_plan(tmp_path, monkeypatch):
    # Point the default store at a temp dir, then publish one plan.
    monkeypatch.setattr(config, "OUT_DIR", tmp_path / "out")
    run_daily_prep(config.DEMO_DATE, client=OfflineClient())
    from kitchen_prep import server

    return TestClient(server.app)


def test_home_returns_200_and_html(client_with_plan):
    resp = client_with_plan.get("/")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    body = resp.text
    assert body.lower().startswith("<!doctype html")


def test_home_shows_prep_shortfalls_orders_waste(client_with_plan):
    body = client_with_plan.get("/").text
    assert "Dagens prep" in body
    assert "Mangler før service" in body
    assert "Bestillingsforslag" in body
    assert "Svinn som krever kontroll" in body
    # Real data from the demo run.
    assert "b06" in body  # expired pork_ribs batch
    assert "Burgerkjøtt" in body


def test_plans_latest_is_json(client_with_plan):
    resp = client_with_plan.get("/plans/latest")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json()["date"] == config.DEMO_DATE
