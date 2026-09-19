"""CrewAI tool for reading the pytest execution result."""

from __future__ import annotations

from typing import Any

from crewai.tools import BaseTool

from config.settings import get_settings


class ReadPytestResultTool(BaseTool):
    name: str = "read_pytest_result"
    description: str = (
        "Read the pytest execution result JSON, including pass/fail counts "
        "and failure messages such as 规则未落地 or 字段未落地. "
        "No arguments are needed."
    )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        settings = get_settings()
        path = settings.pytest_result_path
        if not path.exists():
            return (
                "pytest result file not found: "
                f"{path}. The tests may not have been executed yet."
            )
        return path.read_text(encoding="utf-8")
