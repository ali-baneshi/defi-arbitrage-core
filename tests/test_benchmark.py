import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_script_runs_one_case():
    completed = subprocess.run(
        [sys.executable, "scripts/benchmark.py", "--case", "3:3", "--timeout", "10"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "timeout" not in completed.stdout
    assert "error" not in completed.stdout
    assert "3" in completed.stdout
