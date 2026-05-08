#!/usr/bin/env python3
"""Dependency-free unit checks for environments without pytest.

This does not replace pytest in CI, but it gives contributors a runnable baseline
with only the Python standard library.
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path

from arbcore import AnalysisEngine, Edge, MarketSnapshot, PolicyError, RiskPolicy, SnapshotError
from arbcore.cli import main as cli_main
from arbcore.contracts import validate_contract_workspace
from arbcore.contracts.registry import load_contract_manifest
from arbcore.diagnostics import collect_diagnostics
from arbcore.providers import JsonFileProvider
from arbcore.reporters import JsonReporter, TextReporter
from arbcore.service import analyze_with_optional_rust


def check_engine_cycle() -> None:
    snapshot = MarketSnapshot(
        edges=(
            Edge("A", "B", 2.0, venue="one"),
            Edge("B", "C", 2.0, venue="two"),
            Edge("C", "A", 0.26, venue="three"),
        )
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1, max_hops=3)).analyze(snapshot)
    assert len(opportunities) == 1
    assert opportunities[0].path == ("A", "B", "C", "A")


def check_policy_and_validation() -> None:
    low_liquidity = MarketSnapshot(
        (Edge("A", "B", 2, liquidity=1), Edge("B", "A", 0.6, liquidity=1))
    )
    assert AnalysisEngine(RiskPolicy(min_liquidity=10)).analyze(low_liquidity) == []
    try:
        AnalysisEngine().analyze(MarketSnapshot((Edge("A", "B", -1),)))
    except SnapshotError:
        pass
    else:
        raise AssertionError("invalid edge was accepted")


def check_fail_closed_limits() -> None:
    try:
        RiskPolicy(max_hops=99).validate()
    except PolicyError:
        pass
    else:
        raise AssertionError("unbounded max_hops was accepted")
    try:
        Edge("A" * 33, "B", 1).validate()
    except SnapshotError:
        pass
    else:
        raise AssertionError("oversized asset symbol was accepted")
    try:
        Edge("A", "B", 1, metadata=[("bad", "shape")]).validate()
    except SnapshotError:
        pass
    else:
        raise AssertionError("non-object metadata was accepted")


def check_diagnostics() -> None:
    diagnostics = collect_diagnostics()
    assert diagnostics["arbcore_version"]
    assert "validation_commands" in diagnostics
    assert diagnostics["capabilities"]["multi_network_snapshots"] is True
    assert diagnostics["limits"]["max_hops"] == 8


def check_provider_and_cli() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "snapshot.json"
        path.write_text(json.dumps({"edges": [{"source": "x", "target": "y", "rate": 1.2}]}))
        snapshot = JsonFileProvider(path).load_snapshot()
        assert snapshot.edges[0].source == "X"
    with contextlib.redirect_stdout(io.StringIO()):
        assert cli_main(["examples/market_snapshot.json", "--validate-only"]) == 0
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert cli_main(["examples/market_snapshot.json", "--validate-only", "--json"]) == 0
    assert json.loads(stdout.getvalue())["ok"] is True
    with contextlib.redirect_stderr(io.StringIO()):
        assert cli_main(["missing.json"]) == 2


def check_optional_rust_fallback() -> None:
    opportunities, engine = analyze_with_optional_rust(
        "examples/market_snapshot.json", rust_binary="missing-defi-arbitrage-core-rs"
    )
    assert engine == "python"
    assert opportunities[0].profit_bps > 0


def check_contract_validation() -> None:
    report = validate_contract_workspace("contracts/contract-manifest.json")
    assert report.ok, [finding.to_dict() for finding in report.findings]
    assert set(report.languages) == {"solidity", "vyper"}
    assert report.artifacts_checked == 2
    artifacts, metadata = load_contract_manifest("contracts/contract-manifest.json")
    assert {artifact.artifact_type for artifact in artifacts} == {"source-template"}
    assert metadata["solidity"].file_extension == ".sol"
    assert metadata["vyper"].file_extension == ".vy"


def check_reporters() -> None:
    opportunities = AnalysisEngine().analyze(
        JsonFileProvider("examples/market_snapshot.json").load_snapshot()
    )
    assert "USDC" in TextReporter().render(opportunities)
    assert json.loads(JsonReporter().render(opportunities))[0]["estimated_capacity"] > 0


def main() -> int:
    check_engine_cycle()
    check_policy_and_validation()
    check_fail_closed_limits()
    check_diagnostics()
    check_provider_and_cli()
    check_optional_rust_fallback()
    check_reporters()
    check_contract_validation()
    print("dependency-free unit checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
