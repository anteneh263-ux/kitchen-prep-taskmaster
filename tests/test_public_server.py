"""Security contract for the public, read-only Cloud Run surface."""
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from kitchen_prep import config  # noqa: E402


@pytest.fixture()
def empty_client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUT_DIR", tmp_path / "out")
    from kitchen_prep import public_server

    return TestClient(public_server.app)


def test_public_home_renders_without_a_plan(empty_client):
    response = empty_client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.text.lower().startswith("<!doctype html")


def test_public_latest_returns_empty_state(empty_client):
    response = empty_client.get("/plans/latest")
    assert response.status_code == 200
    assert response.json() == {"detail": "no plans yet"}


def test_public_health_is_ok(empty_client):
    response = empty_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("post", "/runs/daily"),
        ("get", "/docs"),
        ("get", "/redoc"),
        ("get", "/openapi.json"),
    ],
)
def test_public_surface_does_not_expose_private_or_schema_routes(
    empty_client, method, path
):
    response = getattr(empty_client, method)(path)
    assert response.status_code == 404
