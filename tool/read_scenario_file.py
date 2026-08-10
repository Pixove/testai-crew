"""CrewAI tool for reading the user scenario file."""

from __future__ import annotations

from typing import Any

from crewai.tools import BaseTool

from config.settings import get_settings


class ReadScenarioFileTool(BaseTool):
    name: str = "read_scenario_file"
    description: str = (
        "Read the user scenario file (markdown or txt) and return its content. "
        "No arguments are needed."
    )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        settings = get_settings()
        path = settings.scenario_input_path
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {path}")
        return path.read_text(encoding="utf-8")
