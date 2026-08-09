"""Run only the test case designer agent."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.agents.test_case_designer import build_test_case_designer
from src.crew.test_case_designer import build_test_case_design_crew
from src.tasks.test_case_design import build_test_case_design_task


def main() -> None:
    settings = get_settings()
    agent = build_test_case_designer()
    task = build_test_case_design_task(agent)
    crew = build_test_case_design_crew(agent, task)
    result = crew.kickoff()
    print("\n=== TEST CASE DESIGNER RESULT ===")
    print(result)
    print(f"\nSaved: {settings.test_cases_path}")


if __name__ == "__main__":
    main()
