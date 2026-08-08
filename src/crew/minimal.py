"""Minimal Crew used to validate the skeleton."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task


def build_minimal_crew(agent: Agent, task: Task) -> Crew:
    return Crew(
        name="minimal-skeleton",
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
