"""Persistence layer.

Local development uses a JSON-file store under ``out/`` (never committed). A
Firestore backend is provided for Cloud Run; it is lazily imported so the local
environment needs no google-cloud-firestore dependency or credentials.

Collections / concepts:
  - daily_plans/{date}   -> the authoritative plan incl. published markdown field
  - run_logs/{run_id}    -> step-by-step log, written even on failure
  - inventory            -> batches (seeded from data/inventory_batches.json)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .. import config


class BaseStore:
    def plan_exists(self, date: str) -> bool: ...
    def get_plan(self, date: str) -> dict | None: ...
    def save_plan(self, date: str, plan: dict, *, overwrite: bool = False) -> dict: ...
    def get_latest_plan(self) -> dict | None: ...
    def list_plans(self, limit: int = 14) -> list[dict]: ...
    def append_run_log(self, run_id: str, entry: dict) -> None: ...


class LocalJsonStore(BaseStore):
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base = Path(base_dir) if base_dir else config.OUT_DIR
        self.plans_dir = self.base / "daily_plans"
        self.logs_dir = self.base / "run_logs"
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _plan_path(self, date: str) -> Path:
        return self.plans_dir / f"{date}.json"

    def plan_exists(self, date: str) -> bool:
        return self._plan_path(date).exists()

    def get_plan(self, date: str) -> dict | None:
        p = self._plan_path(date)
        if not p.exists():
            return None
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)

    def save_plan(self, date: str, plan: dict, *, overwrite: bool = False) -> dict:
        # Idempotent: never overwrite an existing plan for the same date.
        existing = self.get_plan(date)
        if existing is not None and not overwrite:
            return existing
        with open(self._plan_path(date), "w", encoding="utf-8") as fh:
            json.dump(plan, fh, indent=2, ensure_ascii=False)
        # Also persist the published markdown next to it for convenience.
        md = plan.get("briefing_markdown")
        if md:
            with open(self.plans_dir / f"{date}.md", "w", encoding="utf-8") as fh:
                fh.write(md)
        return plan

    def get_latest_plan(self) -> dict | None:
        plans = sorted(self.plans_dir.glob("*.json"))
        if not plans:
            return None
        with open(plans[-1], encoding="utf-8") as fh:
            return json.load(fh)

    def list_plans(self, limit: int = 14) -> list[dict]:
        plans: list[dict] = []
        for path in sorted(self.plans_dir.glob("*.json"), reverse=True)[:limit]:
            with open(path, encoding="utf-8") as fh:
                plans.append(json.load(fh))
        return plans

    def append_run_log(self, run_id: str, entry: dict) -> None:
        with open(self.logs_dir / f"{run_id}.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


class FirestoreStore(BaseStore):  # pragma: no cover - requires cloud credentials
    def __init__(self, project: str | None = None) -> None:
        from google.cloud import firestore  # lazy import

        self.db = firestore.Client(project=project)

    def plan_exists(self, date: str) -> bool:
        return self.db.collection("daily_plans").document(date).get().exists

    def get_plan(self, date: str) -> dict | None:
        snap = self.db.collection("daily_plans").document(date).get()
        return snap.to_dict() if snap.exists else None

    def save_plan(self, date: str, plan: dict, *, overwrite: bool = False) -> dict:
        ref = self.db.collection("daily_plans").document(date)
        # Idempotent create; if it already exists, return the stored plan.
        existing = ref.get()
        if existing.exists and not overwrite:
            return existing.to_dict()
        if overwrite:
            ref.set(plan)
        else:
            ref.create(plan)  # create() fails if doc exists -> extra idempotency guard
        return plan

    def get_latest_plan(self) -> dict | None:
        from google.cloud import firestore  # lazy import

        q = (
            self.db.collection("daily_plans")
            .order_by("date", direction=firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )
        for doc in q:
            return doc.to_dict()
        return None

    def list_plans(self, limit: int = 14) -> list[dict]:
        from google.cloud import firestore  # lazy import

        query = (
            self.db.collection("daily_plans")
            .order_by("date", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [doc.to_dict() for doc in query]

    def append_run_log(self, run_id: str, entry: dict) -> None:
        self.db.collection("run_logs").document(run_id).collection("steps").add(entry)


def get_store() -> BaseStore:
    """Firestore when explicitly configured, otherwise the local JSON store."""
    import os

    if os.environ.get("KP_STORE") == "firestore":  # opt-in only
        return FirestoreStore(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
    return LocalJsonStore()


def load_seed_batches() -> list[dict[str, Any]]:
    with open(config.BATCHES_PATH, encoding="utf-8") as fh:
        return json.load(fh)["batches"]
