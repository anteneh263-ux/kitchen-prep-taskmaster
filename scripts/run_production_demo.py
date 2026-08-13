#!/usr/bin/env python3
"""Run the private production agent and print only judge-safe evidence fields."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_WORKER = "https://kitchen-prep-taskmaster-web-373405758807.europe-north1.run.app"
DEFAULT_VIEWER = "https://kitchen-prep-viewer-373405758807.europe-north1.run.app"


def _json_request(url: str, *, token: str | None = None, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, data=body, headers=headers, method="POST" if body is not None else "GET")
    with urlopen(request, timeout=320) as response:  # noqa: S310 - explicit production URLs/CLI overrides
        result = json.load(response)
    if not isinstance(result, dict):
        raise ValueError("expected a JSON object")
    return result


def _identity_token() -> str:
    result = subprocess.run(
        ["gcloud", "auth", "print-identity-token"],
        check=True,
        capture_output=True,
        text=True,
    )
    token = result.stdout.strip()
    if not token:
        raise RuntimeError("gcloud returned an empty identity token")
    return token


def _evidence(run: dict, plan: dict) -> dict:
    return {
        "date": run.get("date"),
        "expected_covers": run.get("expected_covers"),
        "forecast_source": run.get("forecast_source"),
        "forecast_note": run.get("forecast_note"),
        "briefing_source": plan.get("briefing_source"),
        "inventory_basis": plan.get("inventory_basis"),
        "planning_basis": plan.get("planning_basis"),
        "prep_tasks": run.get("prep_tasks"),
        "prep_shortfalls": run.get("prep_shortfalls"),
        "replenishment_orders": run.get("replenishment_orders"),
        "waste_flagged": run.get("waste_flagged"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", default=DEFAULT_WORKER)
    parser.add_argument("--viewer", default=DEFAULT_VIEWER)
    parser.add_argument("--date", help="Optional YYYY-MM-DD; defaults to today in Europe/Oslo")
    parser.add_argument("--no-force", action="store_true", help="Use the idempotent saved plan instead of a forced replay")
    args = parser.parse_args()

    payload: dict[str, object] = {"force": not args.no_force}
    if args.date:
        payload["date"] = args.date

    try:
        token = _identity_token()
        run = _json_request(f"{args.worker.rstrip('/')}/runs/daily", token=token, payload=payload)
        plan = _json_request(f"{args.viewer.rstrip('/')}/plans/latest")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ERROR: gcloud authentication failed. Run `gcloud auth login` first.", file=sys.stderr)
        return 2
    except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as exc:
        print(f"ERROR: production demo failed: {exc}", file=sys.stderr)
        return 1

    print("PRODUCTION AGENT EVIDENCE")
    print(json.dumps(_evidence(run, plan), indent=2, sort_keys=False))
    print(f"viewer_url: {args.viewer.rstrip('/')}/?lang=en")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
