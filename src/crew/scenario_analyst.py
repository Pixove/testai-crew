"""Crew for the scenario analyst step."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task


def build_scenario_analysis_crew(agent: Agent, task: Task) -> Crew:
    return Crew(
        name="scenario-analyst",
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
