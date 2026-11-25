import json
from dataclasses import fields
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from arbcore import (
    AnalysisEngine,
    Edge,
    JsonFileProvider,
    JsonReporter,
    RiskPolicy,
    SnapshotError,
)
from arbcore.models import (
    BPS_DENOMINATOR,
    MAX_ASSET_SYMBOL_LENGTH,
    MAX_NETWORK_LENGTH,
    MAX_SNAPSHOT_EDGES,
    MAX_SOURCE_LENGTH,
    MAX_VENUE_LENGTH,
    MarketSnapshot,
    Opportunity,
)
from arbcore.validation import validate_snapshot_payload

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_SCHEMA_PATH = ROOT / "schemas" / "market_snapshot.schema.json"
OPPORTUNITY_SCHEMA_PATH = ROOT / "schemas" / "opportunity.schema.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_published_schemas_are_valid_draft_2020_12():
    for path in (SNAPSHOT_SCHEMA_PATH, OPPORTUNITY_SCHEMA_PATH):
        schema = _load(path)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)


def test_snapshot_schema_matches_model_fields_and_limits():
    schema = _load(SNAPSHOT_SCHEMA_PATH)
    properties = schema["properties"]
    assert set(properties) == {field.name for field in fields(MarketSnapshot)}
    assert schema["required"] == ["edges"]
    assert properties["source"]["maxLength"] == MAX_SOURCE_LENGTH
    assert properties["network"]["maxLength"] == MAX_NETWORK_LENGTH
    assert properties["edges"]["maxItems"] == MAX_SNAPSHOT_EDGES

    edge = schema["$defs"]["edge"]
    edge_properties = edge["properties"]
    assert set(edge_properties) == {field.name for field in fields(Edge)}
    assert set(edge["required"]) == {"source", "target", "rate"}
    assert edge["additionalProperties"] is False
    assert edge_properties["source"]["maxLength"] == MAX_ASSET_SYMBOL_LENGTH
    assert edge_properties["target"]["maxLength"] == MAX_ASSET_SYMBOL_LENGTH
    assert edge_properties["venue"]["maxLength"] == MAX_VENUE_LENGTH
    assert edge_properties["fee_bps"]["exclusiveMaximum"] == BPS_DENOMINATOR
    assert edge_properties["rate"]["exclusiveMinimum"] == 0


def test_opportunity_schema_matches_output_fields_and_limits():
    schema = _load(OPPORTUNITY_SCHEMA_PATH)
    item = schema["items"]
    properties = item["properties"]
    assert set(properties) == {field.name for field in fields(Opportunity)}
    assert set(item["required"]) == {field.name for field in fields(Opportunity)}
    assert item["additionalProperties"] is False
    assert properties["network"]["maxLength"] == MAX_NETWORK_LENGTH
    assert properties["path"]["minItems"] == 3
    assert properties["path"]["items"]["maxLength"] == MAX_ASSET_SYMBOL_LENGTH
    assert properties["venues"]["minItems"] == 2
    assert properties["venues"]["items"]["maxLength"] == MAX_VENUE_LENGTH
    assert properties["snapshot_source"]["maxLength"] == MAX_SOURCE_LENGTH


def test_example_snapshots_validate_against_schema():
    schema = _load(SNAPSHOT_SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for path in sorted((ROOT / "examples").glob("*.json")):
        validator.validate(json.loads(path.read_text(encoding="utf-8")))


def test_runtime_accepted_boundary_payload_validates_against_schema():
    payload = {
        "source": "s" * MAX_SOURCE_LENGTH,
        "network": "n" * MAX_NETWORK_LENGTH,
        "timestamp": "2026-05-05T00:00:00Z",
        "edges": [
            {
                "source": "A" * MAX_ASSET_SYMBOL_LENGTH,
                "target": "B" * MAX_ASSET_SYMBOL_LENGTH,
                "rate": 1.0,
                "venue": "v" * MAX_VENUE_LENGTH,
                "fee_bps": 9999,
                "liquidity": 0,
            }
        ],
    }
    validate_snapshot_payload(payload)
    Draft202012Validator(_load(SNAPSHOT_SCHEMA_PATH)).validate(payload)


def test_runtime_and_schema_both_reject_null_and_unknown_keys():
    schema = _load(SNAPSHOT_SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for payload in (
        {"source": None, "edges": [{"source": "A", "target": "B", "rate": 1.0}]},
        {"edges": [{"source": "A", "target": "B", "rate": 1.0}], "unknown": True},
        {"edges": [{"source": "A", "target": "B", "rate": 1.0, "metadata": {}}]},
    ):
        with pytest.raises(SnapshotError):
            validate_snapshot_payload(payload)
        with pytest.raises(ValidationError):
            validator.validate(payload)


def test_cli_output_validates_against_opportunity_schema():
    validator = Draft202012Validator(_load(OPPORTUNITY_SCHEMA_PATH))
    snapshot = JsonFileProvider(ROOT / "examples" / "market_snapshot.json").load_snapshot()
    opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1)).analyze(snapshot)
    payload = json.loads(JsonReporter().render(opportunities))
    validator.validate(payload)
