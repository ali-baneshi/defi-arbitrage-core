import json

from scripts import validate_contracts


def test_validate_contracts_json_output(capsys):
    exit_code = validate_contracts.main(["contracts/contract-manifest.json", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["artifacts_checked"] == 2
