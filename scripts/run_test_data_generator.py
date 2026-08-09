"""Run only the test data generator agent."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.agents.test_data_generator import build_test_data_generator
from src.crew.test_data_generator import build_test_data_generation_crew
from src.tasks.test_data_generation import build_test_data_generation_task


def main() -> None:
    settings = get_settings()
    agent = build_test_data_generator()
    task = build_test_data_generation_task(agent)
    crew = build_test_data_generation_crew(agent, task)
    result = crew.kickoff()
    print("\n=== TEST DATA GENERATOR RESULT ===")
    print(result)
    print(f"\nSaved: {settings.test_data_path}")


if __name__ == "__main__":
    main()
