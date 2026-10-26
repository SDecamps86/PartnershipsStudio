"""Run offline evaluations and write a reviewable local report."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "evals", "-q"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    report = root / "evals/reports/latest.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text(
        "# Offline fixture evaluation\n\n"
        "Scope: schema, grounding references, capabilities, risks, tailoring, ranking and "
        "precomputed context reversibility. No live model call or M3 recomputation.\n\n"
        f"Result: {'PASS' if result.returncode == 0 else 'FAIL'}\n\n"
        f"```text\n{result.stdout}{result.stderr}\n```\n"
    )
    print(result.stdout, end="")
    print(f"Report: {report.relative_to(root)}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
