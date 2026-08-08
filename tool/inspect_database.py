"""Read-only database inspection tool for CrewAI agents."""

from __future__ import annotations

import json
from typing import Any

from crewai.tools import BaseTool

from config.settings import get_settings
from src.database.inspector import DatabaseInspector


class InspectDatabaseTool(BaseTool):
    name: str = "inspect_database"
    description: str = (
        "Read the project SQLite database and return tables, columns, row counts, "
        "indexes and foreign keys as JSON. No arguments are needed."
    )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        settings = get_settings()
        with DatabaseInspector(settings.database_path) as inspector:
            return json.dumps(inspector.inspect_all(), ensure_ascii=False, indent=2)
