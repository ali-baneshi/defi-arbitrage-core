"""Project-specific exceptions with safe, non-secret-bearing messages."""


class ArbCoreError(Exception):
    """Base class for all expected arbcore errors."""


class ConfigurationError(ArbCoreError):
    """Raised when configuration is invalid."""


class SnapshotError(ArbCoreError):
    """Raised when a market snapshot cannot be loaded or validated."""


class PolicyError(ArbCoreError):
    """Raised when risk policy settings are invalid."""


class AnalysisLimitError(ArbCoreError):
    """Raised when a snapshot exceeds the deterministic search budget."""

