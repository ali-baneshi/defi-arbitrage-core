"""Runnable custom provider example.

Run from the repository root:

    PYTHONPATH=src python examples/custom_provider.py
"""

from __future__ import annotations

from defi_arbitrage_core import AnalysisEngine, Edge, MarketSnapshot, RiskPolicy
from defi_arbitrage_core.reporters import TextReporter


class InMemoryProvider:
    """Small provider that satisfies the MarketDataProvider protocol."""

    def load_snapshot(self) -> MarketSnapshot:
        return MarketSnapshot(
            source="in-memory-example",
            edges=(
                Edge("AAA", "BBB", 2.0, venue="local-a", liquidity=100),
                Edge("BBB", "CCC", 1.5, venue="local-b", liquidity=80),
                Edge("CCC", "AAA", 0.36, venue="local-c", liquidity=60),
            ),
        )


def main() -> int:
    snapshot = InMemoryProvider().load_snapshot()
    policy = RiskPolicy(min_profit_bps=1, max_notional=50)
    opportunities = AnalysisEngine(policy).analyze(snapshot)
    print(TextReporter().render(opportunities))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
