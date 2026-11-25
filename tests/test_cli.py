import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from arbcore import SnapshotError
from arbcore import engine as engine_module
from arbcore.cli import main
from arbcore.providers import JsonFileProvider

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


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
    snapshot_path = (EXAMPLES / "market_snapshot.json").resolve()
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
    with pytest.raises(SnapshotError, match="edges"):
        JsonFileProvider(path).load_snapshot()


def test_cli_outputs_json_with_clean_stderr(capsys):
    exit_code = main([str(EXAMPLES / "market_snapshot.json"), "--json"])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exit_code == 0
    assert captured.err == ""
    assert output[0]["network"] == "polygon"
    assert output[0]["profit_bps"] > 0
    assert "estimated_capacity" in output[0]


def test_cli_text_output_contains_route(capsys):
    exit_code = main([str(EXAMPLES / "market_snapshot.json")])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "USDC -> WETH -> DAI -> USDC" in captured.out


def test_cli_accepts_absolute_path(capsys):
    exit_code = main([str((EXAMPLES / "base_market_snapshot.json").resolve()), "--json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out)[0]["network"] == "base"


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
    assert captured.out == ""
    assert "analysis budget" in captured.err


def test_cli_returns_error_for_missing_file(capsys):
    exit_code = main(["missing.json"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "does not exist" in captured.err


def test_cli_returns_error_for_directory(tmp_path, capsys):
    exit_code = main([str(tmp_path)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "not a file" in captured.err


def test_cli_validate_only_text(capsys):
    exit_code = main([str(EXAMPLES / "market_snapshot.json"), "--validate-only"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Snapshot is valid" in captured.out


def test_cli_validate_only_json(capsys):
    snapshot_path = str(EXAMPLES / "market_snapshot.json")
    exit_code = main([snapshot_path, "--validate-only", "--json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {"ok": True, "snapshot": snapshot_path}


def test_cli_rejects_unknown_flag(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([str(EXAMPLES / "market_snapshot.json"), "--nope"])
    assert exc_info.value.code == 2
    assert "unrecognized" in capsys.readouterr().err


def test_cli_requires_snapshot(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2
    assert "required" in capsys.readouterr().err


def test_cli_rejects_invalid_policy(capsys):
    exit_code = main([str(EXAMPLES / "market_snapshot.json"), "--max-hops", "99"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "max_hops" in captured.err


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert "defi-arbitrage-core" in capsys.readouterr().out


def test_module_entrypoint_outputs_json():
    completed = subprocess.run(
        [sys.executable, "-m", "arbcore", str(EXAMPLES / "base_market_snapshot.json"), "--json"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)[0]["network"] == "base"
