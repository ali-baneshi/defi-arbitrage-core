"""Minimal market opportunity analysis core."""

__version__ = "0.1.0a1"

from arbcore.engine import AnalysisEngine
from arbcore.errors import (
    AnalysisLimitError,
    ArbCoreError,
    ConfigurationError,
    PolicyError,
    SnapshotError,
)
from arbcore.models import Edge, MarketSnapshot, Opportunity, RiskPolicy
from arbcore.providers import JsonFileProvider, MarketDataProvider
from arbcore.reporters import JsonReporter, Reporter, TextReporter
from arbcore.validation import opportunities_to_dict, snapshot_to_dict, validate_snapshot_payload

__all__ = [
    "AnalysisEngine",
    "AnalysisLimitError",
    "ArbCoreError",
    "ConfigurationError",
    "Edge",
    "JsonFileProvider",
    "JsonReporter",
    "MarketDataProvider",
    "MarketSnapshot",
    "Opportunity",
    "PolicyError",
    "Reporter",
    "RiskPolicy",
    "SnapshotError",
    "TextReporter",
    "__version__",
    "opportunities_to_dict",
    "snapshot_to_dict",
    "validate_snapshot_payload",
]
