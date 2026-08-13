"""Small contract tests for recording preflight result handling."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "recording_preflight.py"
SPEC = spec_from_file_location("recording_preflight", SCRIPT)
assert SPEC and SPEC.loader
preflight = module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


def test_result_preserves_safe_check_contract():
    assert preflight._result("viewer home", True, "HTTP 200") == (
        "viewer home", True, "HTTP 200"
    )


def test_preflight_uses_fixed_public_viewer_url():
    assert preflight.VIEWER_URL.startswith("https://kitchen-prep-viewer-")
    assert "@" not in preflight.VIEWER_URL
