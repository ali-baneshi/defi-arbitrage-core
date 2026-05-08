from arbcore import RiskPolicy
from arbcore.service import (
    RustAnalysisService,
    RustServiceUnavailable,
    _opportunity_from_dict,
    analyze_with_optional_rust,
)


def test_rust_service_reports_unavailable_for_missing_binary():
    service = RustAnalysisService("definitely-missing-defi-arbitrage-core-rs")
    assert service.available() is False


def test_auto_engine_falls_back_to_python_when_rust_missing():
    opportunities, engine = analyze_with_optional_rust(
        "examples/market_snapshot.json",
        RiskPolicy(min_profit_bps=1),
        rust_binary="definitely-missing-defi-arbitrage-core-rs",
    )
    assert engine == "python"
    assert opportunities[0].profit_bps > 0


def test_rust_response_rejects_open_path():
    try:
        _opportunity_from_dict(
            {
                "network": "polygon",
                "path": ["A", "B", "C"],
                "venues": ["one", "two"],
                "gross_return": 1.1,
                "profit_bps": 1000,
                "limiting_liquidity": 10,
                "estimated_capacity": 10,
            }
        )
    except RustServiceUnavailable as exc:
        assert "closed cycle" in str(exc)
    else:
        raise AssertionError("expected invalid Rust opportunity to fail")


def test_rust_response_rejects_venue_hop_mismatch():
    try:
        _opportunity_from_dict(
            {
                "network": "polygon",
                "path": ["A", "B", "A"],
                "venues": ["one"],
                "gross_return": 1.1,
                "profit_bps": 1000,
                "limiting_liquidity": 10,
                "estimated_capacity": 10,
            }
        )
    except RustServiceUnavailable as exc:
        assert "align with the number of hops" in str(exc)
    else:
        raise AssertionError("expected invalid Rust opportunity to fail")


def test_rust_response_rejects_invalid_numeric_fields():
    try:
        _opportunity_from_dict(
            {
                "network": "polygon",
                "path": ["A", "B", "A"],
                "venues": ["one", "two"],
                "gross_return": "not-a-number",
                "profit_bps": 1000,
                "limiting_liquidity": 10,
                "estimated_capacity": 10,
            }
        )
    except RustServiceUnavailable as exc:
        assert "invalid numeric fields" in str(exc)
    else:
        raise AssertionError("expected invalid Rust opportunity to fail")


def test_rust_response_rejects_blank_network():
    try:
        _opportunity_from_dict(
            {
                "network": "   ",
                "path": ["A", "B", "A"],
                "venues": ["one", "two"],
                "gross_return": 1.1,
                "profit_bps": 1000,
                "limiting_liquidity": 10,
                "estimated_capacity": 10,
            }
        )
    except RustServiceUnavailable as exc:
        assert "network" in str(exc)
    else:
        raise AssertionError("expected invalid Rust opportunity to fail")
