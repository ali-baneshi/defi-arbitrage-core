#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arbcore.models import (  # noqa: E402
    MAX_ASSET_SYMBOL_LENGTH,
    MAX_NETWORK_LENGTH,
    MAX_REASONABLE_HOPS,
    MAX_REASONABLE_RESULTS,
    MAX_VENUE_LENGTH,
)
from arbcore.validation import MAX_SNAPSHOT_EDGES  # noqa: E402


def main() -> int:
    errors: list[str] = []
    snapshot = _load("schemas/market_snapshot.schema.json")
    policy = _load("schemas/policy.schema.json")
    diagnostics = _load("schemas/diagnostics.schema.json")
    opportunity = _load("schemas/opportunity.schema.json")
    contract_manifest = _load("schemas/contract_manifest.schema.json")

    edge_props = snapshot["$defs"]["edge"]["properties"]
    _expect(
        errors, "source maxLength", edge_props["source"].get("maxLength"), MAX_ASSET_SYMBOL_LENGTH
    )
    _expect(
        errors, "target maxLength", edge_props["target"].get("maxLength"), MAX_ASSET_SYMBOL_LENGTH
    )
    _expect(errors, "venue maxLength", edge_props["venue"].get("maxLength"), MAX_VENUE_LENGTH)
    _expect(
        errors,
        "snapshot network maxLength",
        snapshot["properties"]["network"].get("maxLength"),
        MAX_NETWORK_LENGTH,
    )
    _expect(
        errors,
        "edges maxItems",
        snapshot["properties"]["edges"].get("maxItems"),
        MAX_SNAPSHOT_EDGES,
    )

    policy_props = policy["properties"]
    _expect(
        errors,
        "policy max_hops maximum",
        policy_props["max_hops"].get("maximum"),
        MAX_REASONABLE_HOPS,
    )
    _expect(
        errors,
        "policy max_results maximum",
        policy_props["max_results"].get("maximum"),
        MAX_REASONABLE_RESULTS,
    )
    limits = diagnostics["properties"]["limits"]["properties"]
    _expect(errors, "diagnostics max_hops", limits["max_hops"].get("const"), MAX_REASONABLE_HOPS)
    _expect(
        errors,
        "diagnostics max_results",
        limits["max_results"].get("const"),
        MAX_REASONABLE_RESULTS,
    )
    _expect(
        errors,
        "diagnostics max_snapshot_edges",
        limits["max_snapshot_edges"].get("const"),
        MAX_SNAPSHOT_EDGES,
    )

    opportunity_props = opportunity["items"]["properties"]
    _expect(
        errors,
        "opportunity path item maxLength",
        opportunity_props["path"]["items"].get("maxLength"),
        MAX_ASSET_SYMBOL_LENGTH,
    )
    _expect(
        errors,
        "opportunity network maxLength",
        opportunity_props["network"].get("maxLength"),
        MAX_NETWORK_LENGTH,
    )
    _expect(
        errors,
        "opportunity venues item maxLength",
        opportunity_props["venues"]["items"].get("maxLength"),
        MAX_VENUE_LENGTH,
    )

    artifact_props = contract_manifest["$defs"]["artifact"]["properties"]
    _expect(
        errors,
        "contract artifact role const",
        artifact_props["role"].get("const"),
        "template",
    )
    network_items = artifact_props["networks"]["items"]
    _expect(
        errors,
        "contract artifact networks enum",
        network_items.get("enum"),
        ["local"],
    )

    if errors:
        print("schema consistency validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("schema consistency validation passed")
    return 0


def _load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _expect(errors: list[str], label: str, actual: object, expected: object) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


if __name__ == "__main__":
    raise SystemExit(main())
