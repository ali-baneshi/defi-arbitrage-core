from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable

from arbcore.errors import AnalysisLimitError
from arbcore.models import (
    MAX_EDGE_DEGREE,
    MAX_SEARCH_EXPANSIONS,
    Edge,
    MarketSnapshot,
    Opportunity,
    RiskPolicy,
)


class AnalysisEngine:
    """Finds profitable exchange-rate cycles in a validated market snapshot."""

    def __init__(self, policy: RiskPolicy | None = None):
        self.policy = policy or RiskPolicy()
        self.policy.validate()

    def analyze(self, snapshot: MarketSnapshot) -> list[Opportunity]:
        snapshot = snapshot.normalized()
        snapshot.validate()
        graph: dict[str, list[Edge]] = defaultdict(list)
        for edge in snapshot.edges:
            if edge.liquidity is not None and edge.liquidity < self.policy.min_liquidity:
                continue
            graph[edge.source].append(edge)
        for node_edges in graph.values():
            if len(node_edges) > MAX_EDGE_DEGREE:
                raise ValueError(
                    f"Refusing to analyze snapshot with a node having more than "
                    f"{MAX_EDGE_DEGREE} outgoing edges"
                )

        opportunities: dict[tuple[str, ...], Opportunity] = {}
        budget = _SearchBudget(MAX_SEARCH_EXPANSIONS)
        for start in sorted(graph):
            self._walk(start, start, graph, [], 1.0, snapshot, opportunities, budget)
        ranked = sorted(opportunities.values(), key=lambda item: item.profit_bps, reverse=True)
        return ranked[: self.policy.max_results]

    def _walk(
        self,
        start: str,
        current: str,
        graph: dict[str, list[Edge]],
        route: list[Edge],
        gross_return: float,
        snapshot: MarketSnapshot,
        opportunities: dict[tuple[str, ...], Opportunity],
        budget: _SearchBudget,
    ) -> None:
        if len(route) >= self.policy.max_hops:
            return

        for edge in graph.get(current, []):
            budget.spend()
            next_return = gross_return * edge.effective_rate()
            if not math.isfinite(next_return):
                continue
            next_route = [*route, edge]
            if edge.target == start and len(next_route) >= 2:
                opportunity = self._to_opportunity(
                    snapshot,
                    start,
                    next_route,
                    next_return,
                )
                if not math.isfinite(opportunity.gross_return):
                    continue
                if self._passes_policy(opportunity):
                    key = self._canonical_key(opportunity.path)
                    existing = opportunities.get(key)
                    if existing is None or opportunity.profit_bps > existing.profit_bps:
                        opportunities[key] = opportunity
                continue
            visited_assets = {hop.source for hop in next_route}
            if edge.target not in visited_assets:
                self._walk(
                    start,
                    edge.target,
                    graph,
                    next_route,
                    next_return,
                    snapshot,
                    opportunities,
                    budget,
                )

    def _passes_policy(self, opportunity: Opportunity) -> bool:
        return (
            opportunity.profit_bps >= self.policy.min_profit_bps
            and opportunity.estimated_capacity >= self.policy.min_liquidity
        )

    def _to_opportunity(
        self,
        snapshot: MarketSnapshot,
        start: str,
        route: Iterable[Edge],
        gross_return: float,
    ) -> Opportunity:
        route_tuple = tuple(route)
        path = (start, *(edge.target for edge in route_tuple))
        liquidities = [edge.liquidity for edge in route_tuple if edge.liquidity is not None]
        limiting_liquidity = min(liquidities) if liquidities else None
        # Each edge's liquidity is denominated in that edge's source asset.
        # Convert each bound back into starting-asset units using the amount
        # accumulated before that hop; taking the raw minimum would compare
        # unrelated units such as USDC and WETH.
        capacity_bounds: list[float] = []
        prefix_return = 1.0
        capacity_known = True
        for edge in route_tuple:
            if edge.liquidity is None:
                capacity_known = False
            elif prefix_return > 0 and math.isfinite(prefix_return):
                capacity_bounds.append(edge.liquidity / prefix_return)
            prefix_return *= edge.effective_rate()
        estimated_capacity = min(
            self.policy.max_notional,
            min(capacity_bounds) if capacity_bounds else self.policy.max_notional,
        )
        return Opportunity(
            network=snapshot.network,
            path=path,
            venues=tuple(edge.venue for edge in route_tuple),
            gross_return=gross_return,
            profit_bps=(gross_return - 1.0) * 10_000.0,
            limiting_liquidity=limiting_liquidity,
            estimated_capacity=estimated_capacity,
            capacity_known=capacity_known,
            snapshot_source=snapshot.source,
            snapshot_timestamp=snapshot.timestamp,
        )

    @staticmethod
    def _canonical_key(path: tuple[str, ...]) -> tuple[str, ...]:
        cycle = path[:-1]
        rotations = [cycle[index:] + cycle[:index] for index in range(len(cycle))]
        canonical = min(rotations)
        return canonical + (canonical[0],)


class _SearchBudget:
    """Counts edge expansions so pathological snapshots fail deterministically."""

    def __init__(self, limit: int):
        self.remaining = limit

    def spend(self) -> None:
        self.remaining -= 1
        if self.remaining < 0:
            raise AnalysisLimitError(
                "snapshot search exceeds the analysis budget of "
                f"{MAX_SEARCH_EXPANSIONS} edge expansions; reduce --max-hops, "
                "raise --min-liquidity, or split the snapshot"
            )
