import json

from arbcore.cli import main
from arbcore.providers import JsonFileProvider
from defi_arbitrage_core.cli import main as renamed_main


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


def test_renamed_cli_package_outputs_json(capsys):
    exit_code = renamed_main(["examples/base_market_snapshot.json", "--json"])
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output[0]["network"] == "base"
