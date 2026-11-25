import json

import pytest

from arbcore import (
    AnalysisEngine,
    AnalysisLimitError,
    Edge,
    MarketSnapshot,
    RiskPolicy,
    SnapshotError,
)
from arbcore.models import MAX_EDGE_DEGREE, MAX_SNAPSHOT_EDGES
from arbcore.providers import JsonFileProvider
from arbcore.validation import validate_snapshot_payload


def _write(tmp_path, payload, name="snapshot.json"):
    path = tmp_path / name
    path.write_text(json.dumps(payload))
    return path


def _single_edge(**overrides):
    edge = {"source": "A", "target": "B", "rate": 1.0}
    edge.update(overrides)
    return {"edges": [edge]}


def test_rejects_malformed_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{")
    with pytest.raises(SnapshotError, match="not valid JSON"):
        JsonFileProvider(path).load_snapshot()


def test_rejects_non_finite_rate(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"edges": [{"source": "A", "target": "B", "rate": NaN}]}')
    with pytest.raises(SnapshotError, match="finite positive"):
        JsonFileProvider(path).load_snapshot()


def test_rejects_non_finite_liquidity(tmp_path):
    path = _write(
        tmp_path,
        {"edges": [{"source": "A", "target": "B", "rate": 1.0, "liquidity": float("inf")}]},
    )
    with pytest.raises(SnapshotError, match="finite non-negative"):
        JsonFileProvider(path).load_snapshot()


@pytest.mark.parametrize("rate", [0, -1])
def test_rejects_zero_and_negative_rates(tmp_path, rate):
    with pytest.raises(SnapshotError, match="finite positive"):
        JsonFileProvider(_write(tmp_path, _single_edge(rate=rate))).load_snapshot()


@pytest.mark.parametrize("fee", [-1, 10000, 20000])
def test_rejects_fees_outside_bounds(tmp_path, fee):
    with pytest.raises(SnapshotError, match="fee_bps"):
        JsonFileProvider(_write(tmp_path, _single_edge(fee_bps=fee))).load_snapshot()


def test_accepts_fee_just_below_bound(tmp_path):
    snapshot = JsonFileProvider(_write(tmp_path, _single_edge(fee_bps=9999))).load_snapshot()
    assert snapshot.edges[0].fee_bps == 9999


def test_rejects_self_loop(tmp_path):
    payload = {"edges": [{"source": "A", "target": "A", "rate": 1.0}]}
    with pytest.raises(SnapshotError, match="must differ"):
        JsonFileProvider(_write(tmp_path, payload)).load_snapshot()


def test_rejects_removed_metadata_key():
    with pytest.raises(SnapshotError, match="unsupported keys"):
        validate_snapshot_payload(
            {"edges": [{"source": "A", "target": "B", "rate": 1.0, "metadata": {}}]}
        )


def test_rejects_empty_edges():
    with pytest.raises(SnapshotError, match="at least one edge"):
        validate_snapshot_payload({"edges": []})


def test_rejects_too_many_edges():
    with pytest.raises(SnapshotError, match=f"at most {MAX_SNAPSHOT_EDGES}"):
        validate_snapshot_payload(
            {
                "edges": [
                    {"source": "A", "target": "B", "rate": 1.0}
                    for _ in range(MAX_SNAPSHOT_EDGES + 1)
                ]
            }
        )


def test_rejects_oversized_symbol(tmp_path):
    with pytest.raises(SnapshotError, match="32 characters"):
        JsonFileProvider(_write(tmp_path, _single_edge(source="A" * 33))).load_snapshot()


def test_rejects_oversized_venue(tmp_path):
    with pytest.raises(SnapshotError, match="80 characters"):
        JsonFileProvider(_write(tmp_path, _single_edge(venue="v" * 81))).load_snapshot()


def test_oversized_degree_fails_with_analysis_limit():
    edges = tuple(Edge("A", f"B{index}", 1.0) for index in range(MAX_EDGE_DEGREE + 1))
    with pytest.raises(AnalysisLimitError, match="outgoing"):
        AnalysisEngine(RiskPolicy(max_hops=2)).analyze(MarketSnapshot(edges=edges))


def test_disconnected_graph_returns_empty():
    snapshot = MarketSnapshot(
        edges=(Edge("A", "B", 2.0), Edge("C", "D", 2.0)),
    )
    assert AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot) == []


def test_acyclic_graph_returns_empty():
    snapshot = MarketSnapshot(
        edges=(Edge("A", "B", 2.0), Edge("B", "C", 2.0), Edge("C", "D", 2.0)),
    )
    assert AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot) == []


def test_duplicate_parallel_edges_keep_best_cycle_only():
    snapshot = MarketSnapshot(
        edges=(
            Edge("A", "B", 2.0),
            Edge("A", "B", 3.0),
            Edge("B", "A", 0.6),
        )
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)
    assert len(opportunities) == 1
    assert opportunities[0].path == ("A", "B", "A")
    assert round(opportunities[0].profit_bps) == 8000


def test_overflowing_cycle_is_skipped_without_crash():
    snapshot = MarketSnapshot(
        edges=(Edge("A", "B", 1e308), Edge("B", "A", 1e308)),
    )
    assert AnalysisEngine(RiskPolicy(min_profit_bps=0)).analyze(snapshot) == []


def test_deeply_nested_json_is_reported_not_crashed(tmp_path):
    path = tmp_path / "deep.json"
    path.write_text("[" * 2000 + "0" + "]" * 2000)
    with pytest.raises(SnapshotError):
        JsonFileProvider(path).load_snapshot()


def test_non_utf8_file_is_reported(tmp_path):
    path = tmp_path / "bad.json"
    path.write_bytes(b"\xff\xfe\x00\x00")
    with pytest.raises(SnapshotError, match="UTF-8"):
        JsonFileProvider(path).load_snapshot()
