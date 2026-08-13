#!/usr/bin/env python3
"""Read-only readiness check before recording the competition demo."""
from __future__ import annotations

import json
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT = "kitchen-prep-taskmaster-263"
RUN_REGION = "europe-north1"
SCHEDULER_REGION = "europe-west1"
WORKER = "kitchen-prep-taskmaster-web"
VIEWER = "kitchen-prep-viewer"
JOB = "kitchen-prep-daily"
VIEWER_URL = "https://kitchen-prep-viewer-373405758807.europe-north1.run.app"


def _gcloud(*args: str) -> str:
    result = subprocess.run(["gcloud", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _status(url: str, method: str = "GET") -> int:
    request = Request(url, method=method)
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310 - fixed production URL
            return response.status
    except HTTPError as exc:
        return exc.code


def _json(url: str) -> dict:
    with urlopen(url, timeout=20) as response:  # noqa: S310 - fixed production URL
        value = json.load(response)
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def _result(name: str, passed: bool, detail: str) -> tuple[str, bool, str]:
    return name, passed, detail


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    try:
        active = _gcloud("auth", "list", "--filter=status:ACTIVE", "--format=value(account)")
        checks.append(_result("gcloud authentication", bool(active), "active account available" if active else "no active account"))

        worker = _gcloud(
            "run", "services", "describe", WORKER, f"--project={PROJECT}", f"--region={RUN_REGION}",
            "--format=value(status.latestReadyRevisionName,status.traffic[0].percent)",
        ).split()
        checks.append(_result("private worker", len(worker) >= 2 and worker[1] == "100", f"{worker[0]} · {worker[1]}% traffic" if len(worker) >= 2 else "unavailable"))

        viewer = _gcloud(
            "run", "services", "describe", VIEWER, f"--project={PROJECT}", f"--region={RUN_REGION}",
            "--format=value(status.latestReadyRevisionName,status.traffic[0].percent)",
        ).split()
        checks.append(_result("public viewer", len(viewer) >= 2 and viewer[1] == "100", f"{viewer[0]} · {viewer[1]}% traffic" if len(viewer) >= 2 else "unavailable"))

        scheduler = _gcloud(
            "scheduler", "jobs", "describe", JOB, f"--project={PROJECT}", f"--location={SCHEDULER_REGION}",
            "--format=value(state,schedule,timeZone)",
        ).split()
        scheduler_ok = len(scheduler) >= 4 and scheduler[0] == "ENABLED" and scheduler[1:4] == ["0", "7", "*"]
        # The cron expression splits on spaces; check the stable beginning and timezone as well.
        scheduler_ok = scheduler_ok and "Europe/Oslo" in scheduler
        checks.append(_result("daily scheduler", scheduler_ok, " ".join(scheduler) if scheduler else "unavailable"))

        home_status = _status(f"{VIEWER_URL}/")
        checks.append(_result("viewer home", home_status == 200, f"HTTP {home_status}"))

        private_status = _status(f"{VIEWER_URL}/runs/daily", method="POST")
        checks.append(_result("public mutation boundary", private_status == 404, f"POST /runs/daily → HTTP {private_status}"))

        plan = _json(f"{VIEWER_URL}/plans/latest")
        sources_ok = plan.get("forecast", {}).get("forecast_source") == "gemini" and plan.get("briefing_source") == "gemini"
        checks.append(_result("production model path", sources_ok, f"forecast={plan.get('forecast', {}).get('forecast_source')} · briefing={plan.get('briefing_source')}"))
        checks.append(_result("forecast validation", plan.get("forecast_note") == "gemini_ok", str(plan.get("forecast_note"))))
        checks.append(_result("replay-safe inventory", plan.get("inventory_basis") == "date_input_output_snapshot", str(plan.get("inventory_basis"))))
    except (FileNotFoundError, subprocess.CalledProcessError, URLError, TimeoutError, ValueError) as exc:
        print(f"PREFLIGHT ERROR: {exc}", file=sys.stderr)
        return 2

    print("RECORDING PREFLIGHT")
    for name, passed, detail in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")
    failed = sum(not passed for _, passed, _ in checks)
    print(f"\n{'READY TO RECORD' if failed == 0 else f'NOT READY · {failed} CHECK(S) FAILED'}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
