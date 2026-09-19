"""Run pytest and parse the JUnit XML result into structured JSON."""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def _empty_result() -> dict[str, Any]:
    return {
        "available": False,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "pass_rate": 0.0,
        "failures": [],
        "rule_not_landed": [],
        "field_not_landed": [],
    }


def parse_junit_xml(junit_path: Path) -> dict[str, Any]:
    """Parse a pytest JUnit XML file into a compact result dict."""
    if not junit_path.exists():
        return _empty_result()

    root = ET.parse(junit_path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))

    total = failures = errors = skipped = 0
    failure_items: list[dict[str, str]] = []
    rule_not_landed: list[str] = []
    field_not_landed: list[str] = []

    for suite in suites:
        total += int(suite.get("tests") or 0)
        failures += int(suite.get("failures") or 0)
        errors += int(suite.get("errors") or 0)
        skipped += int(suite.get("skipped") or 0)

        for case in suite.findall("testcase"):
            for tag in ("failure", "error"):
                element = case.find(tag)
                if element is None:
                    continue
                message = " ".join(
                    (element.get("message") or element.text or "").split()
                )[:400]
                name = f"{case.get('classname', '')}::{case.get('name', '')}"
                failure_items.append(
                    {"name": name, "type": tag, "message": message}
                )
                if "规则未落地" in message:
                    rule_not_landed.append(name)
                if "字段未落地" in message:
                    field_not_landed.append(name)

    executable = max(total - skipped, 0)
    passed = max(total - failures - errors - skipped, 0)
    return {
        "available": total > 0,
        "total": total,
        "passed": passed,
        "failed": failures,
        "errors": errors,
        "skipped": skipped,
        "pass_rate": round(passed / executable, 4) if executable else 0.0,
        "failures": failure_items,
        "rule_not_landed": rule_not_landed,
        "field_not_landed": field_not_landed,
    }


def run_pytest(
    test_files: list[str],
    junit_path: Path,
    cwd: Path,
    timeout_seconds: int = 900,
) -> dict[str, Any]:
    """Run pytest on the given files and return parsed results."""
    if not test_files:
        return _empty_result()

    junit_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        *test_files,
        "-q",
        f"--junitxml={junit_path}",
    ]

    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
        exit_code: int | None = completed.returncode
        stdout_tail = (completed.stdout or "")[-4000:]
        stderr_tail = (completed.stderr or "")[-2000:]
        timed_out = False
    except subprocess.TimeoutExpired:
        exit_code = None
        stdout_tail = ""
        stderr_tail = f"pytest timed out after {timeout_seconds}s"
        timed_out = True

    result = parse_junit_xml(junit_path)
    result.update(
        {
            "command": " ".join(command),
            "exit_code": exit_code,
            "timed_out": timed_out,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
        }
    )
    return result


def save_result(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_result(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
