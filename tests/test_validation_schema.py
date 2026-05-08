import json
from pathlib import Path

import pytest

from arbcore import SnapshotError
from arbcore.providers import JsonFileProvider
from arbcore.validation import load_json_payload, validate_snapshot_payload


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


def test_load_json_payload_rejects_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{")
    with pytest.raises(SnapshotError, match="not valid JSON"):
        load_json_payload(path)


def test_load_json_payload_rejects_missing_file(tmp_path):
    path = tmp_path / "missing.json"
    with pytest.raises(SnapshotError, match="does not exist"):
        load_json_payload(path)


def test_load_json_payload_rejects_directory(tmp_path):
    with pytest.raises(SnapshotError, match="not a file"):
        load_json_payload(tmp_path)


def test_json_provider_rejects_non_utf8_file(tmp_path):
    path = tmp_path / "bad.json"
    path.write_bytes(b"\xff\xfe\x00\x00")
    with pytest.raises(SnapshotError, match="UTF-8"):
        JsonFileProvider(path).load_snapshot()
