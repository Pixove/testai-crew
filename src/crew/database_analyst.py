"""Crew for the database analyst step."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task


def build_database_analysis_crew(agent: Agent, task: Task) -> Crew:
    return Crew(
        name="database-analyst",
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
