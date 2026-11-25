import pytest

from arbcore import (
    AnalysisEngine,
    AnalysisLimitError,
    Edge,
    MarketSnapshot,
    PolicyError,
    RiskPolicy,
    SnapshotError,
)
from arbcore import engine as engine_module


def test_detects_profitable_cycle_after_fees():
    snapshot = MarketSnapshot(
        edges=(
            Edge("A", "B", 2.0, fee_bps=0, venue="one"),
            Edge("B", "C", 2.0, fee_bps=0, venue="two"),
            Edge("C", "A", 0.26, fee_bps=0, venue="three"),
        ),
        network="arbitrum",
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1, max_hops=3)).analyze(snapshot)
    assert len(opportunities) == 1
    assert opportunities[0].network == "arbitrum"
    assert opportunities[0].path == ("A", "B", "C", "A")
    assert round(opportunities[0].profit_bps, 2) == 400.0


def test_fees_can_remove_apparent_profit():
    snapshot = MarketSnapshot(
        edges=(
            Edge("A", "B", 1.01, fee_bps=100),
            Edge("B", "A", 1.01, fee_bps=100),
        )
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1, max_hops=2)).analyze(snapshot)
    assert opportunities == []


def test_policy_filters_low_liquidity_edges():
    snapshot = MarketSnapshot(
        edges=(
            Edge("A", "B", 2.0, liquidity=5),
            Edge("B", "A", 0.6, liquidity=5),
        )
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1, min_liquidity=10)).analyze(snapshot)
    assert opportunities == []


def test_max_notional_caps_estimated_capacity():
    snapshot = MarketSnapshot(
        edges=(
            Edge("A", "B", 2.0, liquidity=500),
            Edge("B", "A", 0.6, liquidity=300),
        )
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1, max_notional=100)).analyze(snapshot)
    assert opportunities[0].limiting_liquidity == 300
    assert opportunities[0].estimated_capacity == 100


def test_capacity_is_converted_back_to_starting_asset_units():
    snapshot = MarketSnapshot(
        edges=(
            Edge("A", "B", 2.0, liquidity=1000),
            Edge("B", "A", 0.6, liquidity=300),
        )
    )
    opportunity = AnalysisEngine(RiskPolicy(min_profit_bps=1, max_notional=1000)).analyze(
        snapshot
    )[0]
    # The second edge allows 300 B, which is 150 A at the quoted 2 A->B rate.
    assert opportunity.estimated_capacity == 150
    assert opportunity.capacity_known is True


def test_unknown_liquidity_is_explicit():
    snapshot = MarketSnapshot(
        edges=(Edge("A", "B", 2.0), Edge("B", "A", 0.6, liquidity=300))
    )
    opportunity = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)[0]
    assert opportunity.capacity_known is False


def test_max_results_limits_output():
    snapshot = MarketSnapshot(
        edges=(
            Edge("A", "B", 2.0),
            Edge("B", "A", 0.6),
            Edge("C", "D", 2.0),
            Edge("D", "C", 0.6),
        )
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1, max_results=1)).analyze(snapshot)
    assert len(opportunities) == 1


def test_normalizes_asset_symbols():
    snapshot = MarketSnapshot(edges=(Edge(" usdc ", " weth ", 2), Edge("WETH", "USDC", 0.6)))
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)
    assert opportunities[0].path == ("USDC", "WETH", "USDC")


def test_invalid_edge_is_rejected():
    snapshot = MarketSnapshot(edges=(Edge("A", "B", -1.0),))
    with pytest.raises(SnapshotError, match="rate must be"):
        AnalysisEngine().analyze(snapshot)


def test_direct_model_normalization_handles_non_string_symbols():
    snapshot = MarketSnapshot(edges=(Edge(123, "B", 2), Edge("B", 123, 0.6)))
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)
    assert opportunities[0].path == ("123", "B", "123")


def test_search_budget_aborts_dense_graph(monkeypatch):
    monkeypatch.setattr(engine_module, "MAX_SEARCH_EXPANSIONS", 5)
    names = ["A", "B", "C", "D", "E"]
    snapshot = MarketSnapshot(
        tuple(Edge(source, target, 1.0) for source in names for target in names if source != target)
    )
    with pytest.raises(AnalysisLimitError, match="analysis budget"):
        AnalysisEngine(RiskPolicy(min_profit_bps=999999, max_hops=5)).analyze(snapshot)


def test_search_budget_does_not_reject_small_graphs():
    snapshot = MarketSnapshot(edges=(Edge("A", "B", 2.0), Edge("B", "A", 0.6)))
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)
    assert len(opportunities) == 1


def test_direct_edge_rejects_non_numeric_rate():
    with pytest.raises(SnapshotError, match="numeric fields"):
        Edge("A", "B", "not-a-number").validate()


def test_direct_snapshot_normalizes_non_string_source_and_network():
    snapshot = MarketSnapshot(
        edges=(Edge("A", "B", 2), Edge("B", "A", 0.6)),
        source=123,
        network=456,
    )
    opportunity = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)[0]
    assert opportunity.snapshot_source == "123"
    assert opportunity.network == "456"


def test_direct_snapshot_rejects_non_edge_items():
    snapshot = MarketSnapshot(edges=({"source": "A"},))
    with pytest.raises(SnapshotError, match="Edge objects"):
        AnalysisEngine().analyze(snapshot)


def test_policy_rejects_non_integer_hop_and_result_limits():
    with pytest.raises(PolicyError, match="max_hops must be an integer"):
        RiskPolicy(max_hops=3.5).validate()
    with pytest.raises(PolicyError, match="max_results must be an integer"):
        RiskPolicy(max_results=2.5).validate()


def test_policy_rejects_non_numeric_profit_floor():
    with pytest.raises(PolicyError, match="min_profit_bps"):
        RiskPolicy(min_profit_bps="5").validate()


def test_snapshot_normalizes_network_name():
    snapshot = MarketSnapshot(
        edges=(Edge("A", "B", 2), Edge("B", "A", 0.6)),
        network="  Base  ",
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)
    assert opportunities[0].network == "base"
