"""Minimal market opportunity analysis core."""

__version__ = "0.1.0a1"

from arbcore.engine import AnalysisEngine
from arbcore.errors import AnalysisLimitError, ArbCoreError, PolicyError, SnapshotError
from arbcore.models import Edge, MarketSnapshot, Opportunity, RiskPolicy
from arbcore.providers import JsonFileProvider
from arbcore.reporters import JsonReporter, TextReporter
from arbcore.validation import validate_snapshot_payload

__all__ = [
    "AnalysisEngine",
    "AnalysisLimitError",
    "ArbCoreError",
    "Edge",
    "JsonFileProvider",
    "JsonReporter",
    "MarketSnapshot",
    "Opportunity",
    "PolicyError",
    "RiskPolicy",
    "SnapshotError",
    "TextReporter",
    "__version__",
    "validate_snapshot_payload",
]
