import json
from pathlib import Path

from scripts.release_readiness import _gate_is_satisfied, _load_evidence
from scripts.validate_release_evidence import validate


def test_release_evidence_example_has_valid_structure():
    path = Path("release/release-evidence.example.json")
    assert validate(path) == []
    evidence, error = _load_evidence(path)
    assert error is None
    assert evidence is not None


def test_blocked_example_does_not_satisfy_any_gate():
    payload = json.loads(Path("release/release-evidence.example.json").read_text())
    for gate_id, item in payload["gates"].items():
        assert _gate_is_satisfied(gate_id, item) is False


def test_history_scan_requires_passing_external_tool():
    assert _gate_is_satisfied(
        "independent_history_scan",
        {
            "status": "satisfied",
            "result": "pass",
            "tool": "gitleaks",
            "report_sha256": "a" * 64,
        },
    ) is True
    assert _gate_is_satisfied(
        "independent_history_scan",
        {
            "status": "satisfied",
            "result": "pass",
            "tool": "not-run",
            "report_sha256": "a" * 64,
        },
    ) is False


def test_passing_history_scan_requires_report_checksum():
    assert _gate_is_satisfied(
        "independent_history_scan",
        {"status": "satisfied", "result": "pass", "tool": "gitleaks"},
    ) is False
