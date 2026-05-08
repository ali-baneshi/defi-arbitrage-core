from __future__ import annotations

import argparse
import json
import sys

from arbcore import __version__
from arbcore.config import Settings
from arbcore.diagnostics import diagnostics_json
from arbcore.engine import AnalysisEngine
from arbcore.errors import ArbCoreError
from arbcore.models import RiskPolicy
from arbcore.providers import JsonFileProvider
from arbcore.reporters import JsonReporter, TextReporter
from arbcore.service import analyze_with_optional_rust


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a local market snapshot for bounded exchange-rate cycles.",
        epilog=(
            "This is offline analysis only: no private keys, no RPC, no signing, "
            "no deployment, and no trade execution."
        ),
    )
    parser.add_argument("snapshot", nargs="?", help="Path to a local JSON market snapshot")
    parser.add_argument("--version", action="version", version=f"defi-arbitrage-core {__version__}")
    parser.add_argument("--min-profit-bps", type=float, default=None)
    parser.add_argument("--max-hops", type=int, default=None)
    parser.add_argument("--min-liquidity", type=float, default=None)
    parser.add_argument("--max-notional", type=float, default=None)
    parser.add_argument("--max-results", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON results")
    parser.add_argument(
        "--error-json",
        action="store_true",
        help="Emit expected errors as machine-readable JSON on stderr",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the snapshot without running analysis",
    )
    parser.add_argument(
        "--engine",
        choices=["python", "auto"],
        default="python",
        help="Use Python only or optional Rust with Python fallback",
    )
    parser.add_argument(
        "--rust-binary",
        default="defi-arbitrage-core-rs",
        help="Path/name of optional Rust analyzer binary",
    )
    parser.add_argument(
        "--show-policy",
        action="store_true",
        help="Print resolved risk policy as JSON and exit without loading a snapshot",
    )
    parser.add_argument(
        "--diagnostics",
        "--self-check",
        action="store_true",
        help="Print non-secret environment, capability, and validation diagnostics as JSON and exit",  # noqa: E501
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.diagnostics:
            print(diagnostics_json())
            return 0
        settings = Settings.from_env()
        policy = _resolve_policy(args, settings)
        if args.show_policy:
            print(json.dumps(policy.__dict__, indent=2))
            return 0
        snapshot_path = args.snapshot or settings.provider_file
        snapshot = JsonFileProvider(snapshot_path).load_snapshot()
        if args.validate_only:
            if args.json:
                print(json.dumps({"ok": True, "snapshot": snapshot_path}, indent=2))
            else:
                print(f"Snapshot is valid: {snapshot_path}")
            return 0
        if args.engine == "auto":
            opportunities, engine_name = analyze_with_optional_rust(
                snapshot_path, policy, args.rust_binary
            )
        else:
            opportunities = AnalysisEngine(policy).analyze(snapshot)
            engine_name = "python"
        reporter = JsonReporter() if args.json else TextReporter()
        if not args.json and args.engine == "auto":
            print(f"Engine: {engine_name}")
        print(reporter.render(opportunities))
        return 0
    except ArbCoreError as exc:
        if args.error_json:
            print(_error_json(exc), file=sys.stderr)
        else:
            print(f"defi-arbitrage-core: {exc}", file=sys.stderr)
        return 2


def _resolve_policy(args: argparse.Namespace, settings: Settings) -> RiskPolicy:
    policy = RiskPolicy(
        min_profit_bps=(
            args.min_profit_bps
            if args.min_profit_bps is not None
            else settings.policy.min_profit_bps
        ),
        max_hops=args.max_hops if args.max_hops is not None else settings.policy.max_hops,
        min_liquidity=(
            args.min_liquidity if args.min_liquidity is not None else settings.policy.min_liquidity
        ),
        max_notional=(
            args.max_notional if args.max_notional is not None else settings.policy.max_notional
        ),
        max_results=(
            args.max_results if args.max_results is not None else settings.policy.max_results
        ),
    )
    policy.validate()
    return policy


def _error_json(exc: ArbCoreError) -> str:
    return json.dumps(
        {
            "ok": False,
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
        },
        indent=2,
    )


if __name__ == "__main__":
    raise SystemExit(main())
