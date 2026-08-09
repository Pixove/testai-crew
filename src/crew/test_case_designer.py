"""Crew for the test case designer step."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task


def build_test_case_design_crew(agent: Agent, task: Task) -> Crew:
    return Crew(
        name="test-case-designer",
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
