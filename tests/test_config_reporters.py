import json

import pytest

from arbcore import ConfigurationError
from arbcore.config import Settings
from arbcore.models import Opportunity
from arbcore.reporters import JsonReporter, TextReporter


def test_settings_reject_invalid_env(monkeypatch):
    monkeypatch.setenv("ARBCORE_MAX_HOPS", "bad")
    with pytest.raises(ConfigurationError):
        Settings.from_env()


def test_reporters_render_outputs():
    opportunity = Opportunity(
        network="polygon",
        path=("A", "B", "A"),
        venues=("one", "two"),
        gross_return=1.1,
        profit_bps=1000,
        limiting_liquidity=50,
        estimated_capacity=25,
    )
    assert "[polygon] A -> B -> A" in TextReporter().render([opportunity])
    assert json.loads(JsonReporter().render([opportunity]))[0]["estimated_capacity"] == 25
