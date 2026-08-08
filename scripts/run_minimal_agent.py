"""Run the minimal CrewAI agent to validate the skeleton."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.minimal import build_minimal_agent
from src.crew.minimal import build_minimal_crew
from src.tasks.minimal import build_minimal_task


def main() -> None:
    agent = build_minimal_agent()
    task = build_minimal_task(agent)
    crew = build_minimal_crew(agent, task)
    result = crew.kickoff()
    print("\n=== MINIMAL AGENT RESULT ===")
    print(result)


if __name__ == "__main__":
    main()
