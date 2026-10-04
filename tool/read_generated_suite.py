"""CrewAI tool for reading the current generated test suite."""

from __future__ import annotations

from typing import Any

from crewai.tools import BaseTool

from config.settings import get_settings


class ReadGeneratedSuiteTool(BaseTool):
    name: str = "read_generated_suite"
    description: str = (
        "Read the current generated test suite JSON "
        "(output/generated_test_suite.json) so broken files can be repaired. "
        "No arguments are needed."
    )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        settings = get_settings()
        path = settings.generated_test_suite_path
        if not path.exists():
            return f"Generated test suite not found: {path}"
        return path.read_text(encoding="utf-8")
