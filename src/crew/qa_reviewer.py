"""Crew for the QA reviewer step."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task


def build_qa_review_crew(agent: Agent, task: Task) -> Crew:
    return Crew(
        name="qa-reviewer",
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
