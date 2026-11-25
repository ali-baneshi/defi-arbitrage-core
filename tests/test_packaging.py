import re
from pathlib import Path

from arbcore import __version__

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")


def test_version_matches_pyproject():
    match = re.search(r'(?m)^version = "([^"]+)"', PYPROJECT)
    assert match is not None
    assert __version__ == match.group(1)


def test_one_console_script_and_one_import_package():
    assert 'defi-arbitrage-core = "arbcore.cli:main"' in PYPROJECT
    assert 'arbcore = "arbcore.cli:main"' not in PYPROJECT
    assert (ROOT / "src" / "arbcore" / "__main__.py").is_file()
    assert not (ROOT / "src" / "defi_arbitrage_core").exists()


def test_only_two_published_schemas():
    assert {path.name for path in (ROOT / "schemas").glob("*.json")} == {
        "market_snapshot.schema.json",
        "opportunity.schema.json",
    }


def test_validation_scripts_exist():
    assert (ROOT / "scripts" / "validate_all.py").is_file()
    assert (ROOT / "scripts" / "benchmark.py").is_file()
