"""Minimal market opportunity analysis core."""

__version__ = "0.1.0"

from arbcore.contracts import (
    ContractArtifact,
    ContractFinding,
    ContractLanguageMetadata,
    ContractValidationReport,
    report_to_json,
    validate_contract_workspace,
)
from arbcore.diagnostics import collect_diagnostics, diagnostics_json
from arbcore.engine import AnalysisEngine
from arbcore.errors import (
    ArbCoreError,
    ConfigurationError,
    ContractValidationError,
    PolicyError,
    SnapshotError,
)
from arbcore.models import Edge, MarketSnapshot, Opportunity, RiskPolicy
from arbcore.providers import JsonFileProvider, MarketDataProvider
from arbcore.reporters import JsonReporter, Reporter, TextReporter
from arbcore.service import (
    RustAnalysisService,
    RustServiceUnavailable,
    analyze_snapshot,
    analyze_with_optional_rust,
)
from arbcore.validation import opportunities_to_dict, snapshot_to_dict, validate_snapshot_payload

__all__ = [
    "AnalysisEngine",
    "ArbCoreError",
    "ConfigurationError",
    "ContractArtifact",
    "ContractFinding",
    "ContractLanguageMetadata",
    "ContractValidationError",
    "ContractValidationReport",
    "Edge",
    "JsonFileProvider",
    "collect_diagnostics",
    "diagnostics_json",
    "JsonReporter",
    "MarketDataProvider",
    "MarketSnapshot",
    "Opportunity",
    "PolicyError",
    "Reporter",
    "RiskPolicy",
    "RustAnalysisService",
    "RustServiceUnavailable",
    "SnapshotError",
    "TextReporter",
    "__version__",
    "report_to_json",
    "opportunities_to_dict",
    "snapshot_to_dict",
    "analyze_snapshot",
    "analyze_with_optional_rust",
    "validate_contract_workspace",
    "validate_snapshot_payload",
]
