from pathlib import Path

from arbcore.cli import main

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "fixtures" / "golden_outputs" / "market_snapshot.json"
MARKET = ROOT / "examples" / "market_snapshot.json"


def _run_json(capsys):
    exit_code = main([str(MARKET), "--json"])
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_canonical_json_output_is_byte_identical_to_golden(capsys):
    exit_code, output, error = _run_json(capsys)
    assert exit_code == 0
    assert error == ""
    assert output == GOLDEN.read_text(encoding="utf-8")


def test_repeated_runs_are_byte_identical(capsys):
    first = _run_json(capsys)
    second = _run_json(capsys)
    assert first == second
