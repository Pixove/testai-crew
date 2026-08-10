"""CrewAI tool for reading the schema description JSON file."""

from __future__ import annotations

from typing import Any

from crewai.tools import BaseTool

from config.settings import get_settings


class ReadSchemaJsonTool(BaseTool):
    name: str = "read_schema_json"
    description: str = (
        "Read the schema description JSON with field meanings and sample rows "
        "if it exists. If the file is missing, return a notice. No arguments "
        "are needed."
    )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        settings = get_settings()
        path = settings.schema_output_path
        if not path.exists():
            return f"Schema description file not found: {path}"
        return path.read_text(encoding="utf-8")
