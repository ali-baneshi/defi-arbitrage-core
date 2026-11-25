import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DOCS = {
    "AUDIT.md",
    "PRODUCT.md",
    "DECISIONS.md",
    "ARCHITECTURE.md",
    "USAGE.md",
    "VALIDATION.md",
    "RELEASE_CHECKLIST.md",
    "FINAL_AUDIT.md",
}


def test_canonical_docs_exist():
    assert {path.name for path in (ROOT / "docs" / "en").glob("*.md")} == CANONICAL_DOCS


def test_readme_local_links_resolve():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        relative = target.split("#", 1)[0]
        assert (ROOT / relative).exists(), target


def test_readme_documents_the_supported_commands():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "defi-arbitrage-core examples/market_snapshot.json --json" in text
    assert "PYTHONPATH=src python -m arbcore.cli examples/market_snapshot.json --json" in text
    assert "PYTHONPATH=src python scripts/validate_all.py" in text
    assert "python scripts/benchmark.py" in text
