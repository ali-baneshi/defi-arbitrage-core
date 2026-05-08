from __future__ import annotations

import json
from dataclasses import asdict
from typing import Protocol

from arbcore.models import Opportunity


class Reporter(Protocol):
    """Extension point for rendering analysis results."""

    def render(self, opportunities: list[Opportunity]) -> str:
        """Return a complete string representation of opportunities."""


class JsonReporter:
    """Machine-readable JSON output."""

    def render(self, opportunities: list[Opportunity]) -> str:
        return json.dumps([asdict(item) for item in opportunities], indent=2)


class TextReporter:
    """Human-readable command-line output."""

    def render(self, opportunities: list[Opportunity]) -> str:
        if not opportunities:
            return "No opportunities passed the configured policy."
        lines = []
        for item in opportunities:
            route = " -> ".join(item.path)
            venues = ", ".join(item.venues)
            lines.append(
                f"[{item.network}] {route} | {item.profit_bps:.2f} bps | "
                f"capacity: {item.estimated_capacity:.4g} | venues: {venues}"
            )
        return "\n".join(lines)
