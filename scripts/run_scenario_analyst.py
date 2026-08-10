"""Run only the scenario analyst agent."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.agents.scenario_analyst import build_scenario_analyst
from src.crew.scenario_analyst import build_scenario_analysis_crew
from src.tasks.scenario_analysis import build_scenario_analysis_task


def main() -> None:
    settings = get_settings()
    agent = build_scenario_analyst()
    task = build_scenario_analysis_task(agent)
    crew = build_scenario_analysis_crew(agent, task)
    result = crew.kickoff()
    print("\n=== SCENARIO ANALYST RESULT ===")
    print(result)
    print(f"\nSaved: {settings.scenario_rules_path}")


if __name__ == "__main__":
    main()
