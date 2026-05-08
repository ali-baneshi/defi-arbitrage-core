from __future__ import annotations

import json
import math
import shutil
import subprocess
from dataclasses import fields
from pathlib import Path

from arbcore.engine import AnalysisEngine
from arbcore.errors import ArbCoreError
from arbcore.models import MarketSnapshot, Opportunity, RiskPolicy
from arbcore.providers import JsonFileProvider
from arbcore.validation import snapshot_to_dict


class RustServiceUnavailable(ArbCoreError):
    """Raised when the optional Rust service cannot be used."""


class RustAnalysisService:
    """Process-boundary adapter for the optional Rust analyzer.

    The Rust binary reads a local snapshot JSON file and emits the same JSON
    opportunity contract as the Python reporter. If the service fails, callers
    should fall back to `AnalysisEngine`.
    """

    def __init__(self, binary: str | Path = "defi-arbitrage-core-rs", timeout_seconds: float = 5.0):
        self.binary = str(binary)
        self.timeout_seconds = timeout_seconds

    def available(self) -> bool:
        if Path(self.binary).exists():
            return True
        return shutil.which(self.binary) is not None

    def analyze_file(
        self, snapshot_path: str | Path, policy: RiskPolicy | None = None
    ) -> list[Opportunity]:
        policy = policy or RiskPolicy()
        policy.validate()
        if not self.available():
            raise RustServiceUnavailable(f"Rust analyzer is not available: {self.binary}")
        command = [
            self.binary,
            str(snapshot_path),
            "--min-profit-bps",
            str(policy.min_profit_bps),
            "--max-hops",
            str(policy.max_hops),
            "--min-liquidity",
            str(policy.min_liquidity),
            "--max-notional",
            str(policy.max_notional),
            "--max-results",
            str(policy.max_results),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RustServiceUnavailable("Rust analyzer execution failed") from exc
        if completed.returncode != 0:
            message = completed.stderr.strip() or "Rust analyzer returned a non-zero exit code"
            raise RustServiceUnavailable(message)
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RustServiceUnavailable("Rust analyzer returned invalid JSON") from exc
        if not isinstance(payload, list):
            raise RustServiceUnavailable("Rust analyzer returned an invalid top-level payload")
        return [_opportunity_from_dict(item) for item in payload]


def analyze_with_optional_rust(
    snapshot_path: str | Path,
    policy: RiskPolicy | None = None,
    rust_binary: str | Path = "defi-arbitrage-core-rs",
) -> tuple[list[Opportunity], str]:
    """Analyze with Rust when available, otherwise use Python.

    Returns `(opportunities, engine_name)` where `engine_name` is `rust` or
    `python`. This makes fallback behavior observable without making Rust a hard
    dependency.
    """

    policy = policy or RiskPolicy()
    service = RustAnalysisService(rust_binary)
    try:
        return service.analyze_file(snapshot_path, policy), "rust"
    except RustServiceUnavailable:
        snapshot = JsonFileProvider(snapshot_path).load_snapshot()
        return AnalysisEngine(policy).analyze(snapshot), "python"


def analyze_snapshot(
    snapshot: MarketSnapshot, policy: RiskPolicy | None = None
) -> list[Opportunity]:
    """Pure Python analysis helper for already-loaded snapshots."""

    return AnalysisEngine(policy).analyze(snapshot)


def snapshot_json(snapshot: MarketSnapshot) -> str:
    return json.dumps(snapshot_to_dict(snapshot), indent=2)


def _opportunity_from_dict(item: dict) -> Opportunity:
    if not isinstance(item, dict):
        raise RustServiceUnavailable("Rust analyzer response items must be objects")
    names = {field.name for field in fields(Opportunity)}
    missing = names - set(item)
    if missing:
        raise RustServiceUnavailable(
            f"Rust analyzer response missing fields: {', '.join(sorted(missing))}"
        )
    extra = set(item) - names
    if extra:
        raise RustServiceUnavailable(
            f"Rust analyzer response contains unsupported fields: {', '.join(sorted(extra))}"
        )

    if not isinstance(item["path"], (list, tuple)):
        raise RustServiceUnavailable("Rust analyzer response path must be a list")
    if not isinstance(item["venues"], (list, tuple)):
        raise RustServiceUnavailable("Rust analyzer response venues must be a list")
    network = str(item["network"]).strip().lower()
    if not network:
        raise RustServiceUnavailable("Rust analyzer response network must be a non-empty string")
    path = tuple(str(value).strip().upper() for value in item["path"])
    venues = tuple(str(value).strip() or "unknown" for value in item["venues"])
    if len(path) < 3 or path[0] != path[-1]:
        raise RustServiceUnavailable("Rust analyzer response path must describe a closed cycle")
    if len(venues) != len(path) - 1:
        raise RustServiceUnavailable(
            "Rust analyzer response venues must align with the number of hops"
        )
    try:
        gross_return = float(item["gross_return"])
        profit_bps = float(item["profit_bps"])
        limiting_liquidity = (
            None if item["limiting_liquidity"] is None else float(item["limiting_liquidity"])
        )
        estimated_capacity = float(item["estimated_capacity"])
    except (TypeError, ValueError) as exc:
        raise RustServiceUnavailable(
            "Rust analyzer response contains invalid numeric fields"
        ) from exc
    for value_name, value in (
        ("gross_return", gross_return),
        ("profit_bps", profit_bps),
        ("estimated_capacity", estimated_capacity),
    ):
        if not math.isfinite(value):
            raise RustServiceUnavailable(
                f"Rust analyzer response field '{value_name}' must be finite"
            )
    if gross_return <= 0:
        raise RustServiceUnavailable("Rust analyzer response gross_return must be positive")
    if limiting_liquidity is not None and (
        not math.isfinite(limiting_liquidity) or limiting_liquidity < 0
    ):
        raise RustServiceUnavailable(
            "Rust analyzer response limiting_liquidity must be finite and non-negative"
        )
    if estimated_capacity < 0:
        raise RustServiceUnavailable(
            "Rust analyzer response estimated_capacity must be non-negative"
        )
    return Opportunity(
        network=network,
        path=path,
        venues=venues,
        gross_return=gross_return,
        profit_bps=profit_bps,
        limiting_liquidity=limiting_liquidity,
        estimated_capacity=estimated_capacity,
    )
