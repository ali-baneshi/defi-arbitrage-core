"""Minimal market opportunity analysis core."""

__version__ = "0.1.0a1"

from arbcore.contracts import (
    ContractArtifact,
    ContractFinding,
    ContractLanguageMetadata,
    ContractValidationReport,
    report_to_json,
    validate_contract_workspace,
)
from arbcore.engine import AnalysisEngine
from arbcore.errors import (
    AnalysisLimitError,
    ArbCoreError,
    ConfigurationError,
    ContractValidationError,
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
    "ContractArtifact",
    "ContractFinding",
    "ContractLanguageMetadata",
    "ContractValidationError",
    "ContractValidationReport",
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
    "report_to_json",
    "opportunities_to_dict",
    "snapshot_to_dict",
    "validate_contract_workspace",
    "validate_snapshot_payload",
]
