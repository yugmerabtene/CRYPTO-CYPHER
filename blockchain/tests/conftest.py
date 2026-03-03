from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure project root is importable even when pytest is launched outside the repo.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_TEST_OUTCOMES: dict[str, str] = {}


def pytest_runtest_logreport(report: Any) -> None:
    nodeid = report.nodeid

    if report.when == "call":
        _TEST_OUTCOMES[nodeid] = report.outcome.upper()
        return

    if report.when == "setup" and report.skipped:
        _TEST_OUTCOMES[nodeid] = "SKIPPED"
        return

    if report.when in {"setup", "teardown"} and report.failed:
        _TEST_OUTCOMES[nodeid] = "ERROR"


def pytest_terminal_summary(terminalreporter: Any, exitstatus: int, config: Any) -> None:
    terminalreporter.write_sep("-", "Statut par test")
    for nodeid in sorted(_TEST_OUTCOMES):
        terminalreporter.write_line(f"{nodeid}: {_TEST_OUTCOMES[nodeid]}")
