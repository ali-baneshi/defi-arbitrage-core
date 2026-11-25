import json
import os
import subprocess
import sys
from pathlib import Path

from arbcore import engine as engine_module
from arbcore.cli import main
from arbcore.providers import JsonFileProvider


def test_json_provider_loads_edges(tmp_path):
    path = tmp_path / "snapshot.json"
    path.write_text(
        json.dumps(
            {
                "network": "optimism",
                "edges": [{"source": "x", "target": "y", "rate": 1.2}],
            }
        )
    )
    snapshot = JsonFileProvider(path).load_snapshot()
    assert snapshot.network == "optimism"
    assert snapshot.edges[0].source == "X"
    assert snapshot.edges[0].target == "Y"


def test_json_provider_accepts_absolute_path_outside_cwd(tmp_path, monkeypatch):
    snapshot_path = Path("examples/market_snapshot.json").resolve()
    monkeypatch.chdir(tmp_path)
    snapshot = JsonFileProvider(snapshot_path).load_snapshot()
    assert snapshot.network == "polygon"


def test_json_provider_uses_stable_local_source_default(tmp_path):
    path = tmp_path / "snapshot.json"
    path.write_text(
        json.dumps({"edges": [{"source": "x", "target": "y", "rate": 1.2}]})
    )
    assert JsonFileProvider(path).load_snapshot().source == "local"


def test_json_provider_rejects_missing_edges(tmp_path):
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps({"source": "bad"}))
    try:
        JsonFileProvider(path).load_snapshot()
    except Exception as exc:
        assert "edges" in str(exc)
    else:
        raise AssertionError("expected invalid snapshot to fail")


def test_cli_outputs_json(capsys):
    exit_code = main(["examples/market_snapshot.json", "--json"])
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output[0]["network"] == "polygon"
    assert output[0]["profit_bps"] > 0
    assert "estimated_capacity" in output[0]


def test_cli_returns_error_when_search_budget_is_exceeded(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(engine_module, "MAX_SEARCH_EXPANSIONS", 1)
    path = tmp_path / "cycle.json"
    path.write_text(
        json.dumps(
            {
                "edges": [
                    {"source": "A", "target": "B", "rate": 2.0},
                    {"source": "B", "target": "A", "rate": 0.6},
                ]
            }
        )
    )
    exit_code = main([str(path), "--min-profit-bps", "1"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "analysis budget" in captured.err


def test_cli_returns_error_for_missing_file(capsys):
    exit_code = main(["missing.json"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "does not exist" in captured.err


def test_cli_validate_only(capsys):
    exit_code = main(["examples/market_snapshot.json", "--validate-only"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Snapshot is valid" in captured.out


def test_module_entrypoint_outputs_json():
    completed = subprocess.run(
        [sys.executable, "-m", "arbcore", "examples/base_market_snapshot.json", "--json"],
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "PYTHONPATH": "src"},
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)[0]["network"] == "base"
