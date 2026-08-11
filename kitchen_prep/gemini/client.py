"""Gemini client abstraction.

Only two controlled steps ever call the model: demand forecast and briefing.
Real calls happen only when GOOGLE_API_KEY is set. Otherwise an OfflineClient
raises ``GeminiUnavailable`` so the orchestrator uses deterministic paths
(baseline forecast / deterministic briefing). The model never computes or mutates
authoritative quantities.
"""
from __future__ import annotations

from typing import Any

from .. import config


class GeminiUnavailable(Exception):
    """Transient model-side condition that MAY trigger a fallback: rate limit
    (429), request timeout (408), server error (5xx) or a network error.

    Everything else — auth (401), permission (403), not-found (404) and bad
    requests such as 400 API_KEY_INVALID — is fatal and must crash the run. So
    must any programming error.
    """


# Only these HTTP statuses are treated as transient/retryable.
_RETRYABLE_STATUS = {408, 429}

# Transport-level failures (httpx / stdlib) identified by type name or base class.
_NETWORK_ERROR_NAMES = {
    "ConnectError",
    "ConnectTimeout",
    "ReadTimeout",
    "WriteTimeout",
    "PoolTimeout",
    "TimeoutException",
    "TransportError",
    "RequestError",
    "ReadError",
    "NetworkError",
}


def _status_code(exc: Exception) -> int | None:
    """Best-effort HTTP status extraction across SDK/httpx error shapes."""
    for attr in ("code", "status_code"):
        v = getattr(exc, attr, None)
        if isinstance(v, int) and not isinstance(v, bool):
            return v
    resp = getattr(exc, "response", None)
    if resp is not None:
        v = getattr(resp, "status_code", None)
        if isinstance(v, int) and not isinstance(v, bool):
            return v
    return None


def _is_network_error(exc: Exception) -> bool:
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True
    return type(exc).__name__ in _NETWORK_ERROR_NAMES


def classify_model_error(exc: Exception):
    """Raise GeminiUnavailable for transient failures (429/408/5xx/network);
    re-raise the original exception for everything else (auth, permission,
    not-found, bad request, programming errors). Never converts all errors to
    fallback and never swallows a fatal error.
    """
    if _is_network_error(exc):
        raise GeminiUnavailable(f"network error: {exc!r}") from exc
    code = _status_code(exc)
    if code is not None and (code in _RETRYABLE_STATUS or 500 <= code <= 599):
        raise GeminiUnavailable(f"transient API error {code}") from exc
    # 400 API_KEY_INVALID, 401, 403, 404 and any other non-transient error crash.
    raise exc


class OfflineClient:
    """Used when no API key is configured (local dev / tests)."""

    def propose_forecast(self, context: dict[str, Any]) -> dict:
        raise GeminiUnavailable("offline: no GOOGLE_API_KEY configured")

    def propose_briefing(self, plan: dict[str, Any]) -> dict:
        raise GeminiUnavailable("offline: no GOOGLE_API_KEY configured")


class RealGeminiClient:  # pragma: no cover - requires network + credentials
    def __init__(self) -> None:
        from google import genai  # lazy import

        self._genai = genai
        self._client = genai.Client()

    def _generate_json(self, prompt: str) -> dict:
        import json

        import httpx
        from google.genai import errors as genai_errors

        # Only transport/timeout failures are transient here.
        transient_transport = (
            httpx.TransportError,
            httpx.TimeoutException,
            TimeoutError,
            ConnectionError,
            OSError,
        )
        try:
            resp = self._client.models.generate_content(
                model=config.MODEL_ID,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
        except genai_errors.APIError as exc:
            # 408/429/5xx -> GeminiUnavailable; 400/401/403/404 -> re-raised (crash).
            classify_model_error(exc)
            raise  # unreachable; classify_model_error always raises
        except transient_transport as exc:
            raise GeminiUnavailable(f"network error: {exc!r}") from exc
        # NOTE: no broad `except Exception` — client bugs and programming errors
        # propagate unchanged and crash the run.

        try:
            return json.loads(resp.text)
        except json.JSONDecodeError as exc:
            # Malformed model output counts as a rejected/unusable response.
            raise GeminiUnavailable("model returned non-JSON output") from exc

    def propose_forecast(self, context: dict[str, Any]) -> dict:
        prompt = (
            "You are a restaurant demand forecaster. Given covers, weather and "
            "recent same-weekday sales, propose expected_qty per dish. Return ONLY "
            "JSON matching: {forecast_date, expected_covers, dishes:[{dish_id, "
            "expected_qty(int), confidence, reasoning}], drivers:[...]}. "
            f"Context: {context}"
        )
        return self._generate_json(prompt)

    def propose_briefing(self, plan: dict[str, Any]) -> dict:
        prompt = (
            "Write a concise kitchen morning briefing. Do NOT change any numbers. "
            "Return ONLY JSON: {summary, priority_task_ids:[...], shortfall_actions:"
            "[{item_id, recommended_action, requires_human_approval(bool)}], "
            f"warnings:[...]}}. Authoritative plan: {plan}"
        )
        return self._generate_json(prompt)


def get_client():
    if config.gemini_enabled():
        return RealGeminiClient()
    return OfflineClient()
