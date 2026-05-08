import pytest

from arbcore import AnalysisEngine, Edge, MarketSnapshot, RiskPolicy, SnapshotError


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


def test_snapshot_normalizes_network_name():
    snapshot = MarketSnapshot(
        edges=(Edge("A", "B", 2), Edge("B", "A", 0.6)),
        network="  Base  ",
    )
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)
    assert opportunities[0].network == "base"
