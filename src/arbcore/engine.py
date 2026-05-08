from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from arbcore.models import Edge, MarketSnapshot, Opportunity, RiskPolicy


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

        opportunities: dict[tuple[str, ...], Opportunity] = {}
        for start in sorted(graph):
            self._walk(start, start, graph, [], 1.0, snapshot.network, opportunities)
        ranked = sorted(opportunities.values(), key=lambda item: item.profit_bps, reverse=True)
        return ranked[: self.policy.max_results]

    def _walk(
        self,
        start: str,
        current: str,
        graph: dict[str, list[Edge]],
        route: list[Edge],
        gross_return: float,
        network: str,
        opportunities: dict[tuple[str, ...], Opportunity],
    ) -> None:
        if len(route) >= self.policy.max_hops:
            return

        for edge in graph.get(current, []):
            next_return = gross_return * edge.effective_rate()
            next_route = [*route, edge]
            if edge.target == start and len(next_route) >= 2:
                opportunity = self._to_opportunity(network, start, next_route, next_return)
                if self._passes_policy(opportunity):
                    key = self._canonical_key(opportunity.path)
                    existing = opportunities.get(key)
                    if existing is None or opportunity.profit_bps > existing.profit_bps:
                        opportunities[key] = opportunity
                continue
            visited_assets = {hop.source for hop in next_route}
            if edge.target not in visited_assets:
                self._walk(
                    start, edge.target, graph, next_route, next_return, network, opportunities
                )

    def _passes_policy(self, opportunity: Opportunity) -> bool:
        return (
            opportunity.profit_bps >= self.policy.min_profit_bps
            and opportunity.estimated_capacity >= self.policy.min_liquidity
        )

    def _to_opportunity(
        self,
        network: str,
        start: str,
        route: Iterable[Edge],
        gross_return: float,
    ) -> Opportunity:
        route_tuple = tuple(route)
        path = (start, *(edge.target for edge in route_tuple))
        liquidities = [edge.liquidity for edge in route_tuple if edge.liquidity is not None]
        limiting_liquidity = min(liquidities) if liquidities else None
        estimated_capacity = min(
            self.policy.max_notional,
            limiting_liquidity if limiting_liquidity is not None else self.policy.max_notional,
        )
        return Opportunity(
            network=network,
            path=path,
            venues=tuple(edge.venue for edge in route_tuple),
            gross_return=gross_return,
            profit_bps=(gross_return - 1.0) * 10_000.0,
            limiting_liquidity=limiting_liquidity,
            estimated_capacity=estimated_capacity,
        )

    @staticmethod
    def _canonical_key(path: tuple[str, ...]) -> tuple[str, ...]:
        cycle = path[:-1]
        rotations = [cycle[index:] + cycle[:index] for index in range(len(cycle))]
        canonical = min(rotations)
        return canonical + (canonical[0],)
