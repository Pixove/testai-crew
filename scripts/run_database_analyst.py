"""Run only the database analyst agent."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.agents.database_analyst import build_database_analyst
from src.crew.database_analyst import build_database_analysis_crew
from src.tasks.schema_analysis import build_schema_analysis_task


def main() -> None:
    settings = get_settings()
    agent = build_database_analyst()
    task = build_schema_analysis_task(agent)
    crew = build_database_analysis_crew(agent, task)
    result = crew.kickoff()
    print("\n=== DATABASE ANALYST RESULT ===")
    print(result)
    print(f"\nSaved: {settings.business_scenarios_path}")


if __name__ == "__main__":
    main()
