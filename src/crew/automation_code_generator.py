"""Crew for the automation code generator step."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task


def build_automation_code_generation_crew(agent: Agent, task: Task) -> Crew:
    return Crew(
        name="automation-code-generator",
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
