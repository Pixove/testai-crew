"""Crew for the test data generator step."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task


def build_test_data_generation_crew(agent: Agent, task: Task) -> Crew:
    return Crew(
        name="test-data-generator",
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
