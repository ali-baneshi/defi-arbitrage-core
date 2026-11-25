import json
from pathlib import Path

import pytest

from arbcore import SnapshotError
from arbcore.providers import JsonFileProvider
from arbcore.validation import validate_snapshot_payload


def test_schema_files_are_valid_json():
    for path in Path("schemas").glob("*.json"):
        payload = json.loads(path.read_text())
        assert payload["$schema"].startswith("https://json-schema.org")
        assert payload["title"]


def test_rejects_unknown_snapshot_keys(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"edges": [], "unexpected": True}))
    with pytest.raises(SnapshotError, match="unsupported keys"):
        JsonFileProvider(path).load_snapshot()


def test_rejects_unknown_edge_keys():
    with pytest.raises(SnapshotError, match="unsupported keys"):
        validate_snapshot_payload({"edges": [{"source": "A", "target": "B", "rate": 1, "bad": 1}]})


def test_rejects_string_numeric_values():
    with pytest.raises(SnapshotError, match="rate must be a number"):
        validate_snapshot_payload(
            {"edges": [{"source": "A", "target": "B", "rate": "1.0"}]}
        )


def test_rejects_explicit_null_optional_fields():
    for key in ("source", "network", "timestamp"):
        with pytest.raises(SnapshotError, match=rf"{key} must not be null"):
            validate_snapshot_payload(
                {key: None, "edges": [{"source": "A", "target": "B", "rate": 1}]}
            )


def test_json_provider_rejects_non_utf8_file(tmp_path):
    path = tmp_path / "bad.json"
    path.write_bytes(b"\xff\xfe\x00\x00")
    with pytest.raises(SnapshotError, match="UTF-8"):
        JsonFileProvider(path).load_snapshot()
