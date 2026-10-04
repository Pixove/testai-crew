"""Crew composition for the generation stage and the QA review stage."""

from __future__ import annotations

from crewai import Crew, Process

from src.agents.automation_code_generator import build_automation_code_generator
from src.agents.database_analyst import build_database_analyst
from src.agents.qa_reviewer import build_qa_reviewer
from src.agents.scenario_analyst import build_scenario_analyst
from src.agents.test_case_designer import build_test_case_designer
from src.agents.test_data_generator import build_test_data_generator
from src.tasks.automation_code_generation import build_automation_code_generation_task
from src.tasks.code_repair import build_code_repair_task
from src.tasks.qa_review import build_qa_review_task
from src.tasks.schema_analysis import build_schema_analysis_task
from src.tasks.scenario_analysis import build_scenario_analysis_task
from src.tasks.test_case_design import build_test_case_design_task
from src.tasks.test_data_generation import build_test_data_generation_task


def build_scenario_crew() -> Crew:
    """Build the scenario analyst stage."""
    scenario_agent = build_scenario_analyst()
    scenario_task = build_scenario_analysis_task(scenario_agent)
    return Crew(
        name="scenario-analysis",
        agents=[scenario_agent],
        tasks=[scenario_task],
        process=Process.sequential,
        verbose=True,
    )


def build_analysis_crew() -> Crew:
    """Build database analysis through pytest code generation."""
    database_agent = build_database_analyst()
    test_case_agent = build_test_case_designer()
    test_data_agent = build_test_data_generator()
    code_agent = build_automation_code_generator()

    schema_task = build_schema_analysis_task(database_agent)
    test_case_task = build_test_case_design_task(test_case_agent)
    test_data_task = build_test_data_generation_task(test_data_agent)
    code_task = build_automation_code_generation_task(code_agent)

    return Crew(
        name="analysis-generation",
        agents=[
            database_agent,
            test_case_agent,
            test_data_agent,
            code_agent,
        ],
        tasks=[
            schema_task,
            test_case_task,
            test_data_task,
            code_task,
        ],
        process=Process.sequential,
        verbose=True,
    )


def build_generation_crew() -> Crew:
    """Build the full generation stage: scenario rules to pytest code."""
    scenario = build_scenario_crew()
    analysis = build_analysis_crew()
    return Crew(
        name="generation-pipeline",
        agents=[*scenario.agents, *analysis.agents],
        tasks=[*scenario.tasks, *analysis.tasks],
        process=Process.sequential,
        verbose=True,
    )


def build_qa_crew() -> Crew:
    """Build the QA reviewer, which runs after pytest execution."""
    qa_agent = build_qa_reviewer()
    qa_task = build_qa_review_task(qa_agent)
    return Crew(
        name="qa-review",
        agents=[qa_agent],
        tasks=[qa_task],
        process=Process.sequential,
        verbose=True,
    )


def build_code_repair_crew(validation_report: dict) -> Crew:
    """Build a crew that repairs generated pytest files failing validation."""
    agent = build_automation_code_generator()
    task = build_code_repair_task(agent, validation_report)
    return Crew(
        name="code-repair",
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )


def build_full_pipeline_crew() -> Crew:
    """Legacy single-shot crew.

    Kept for compatibility. The recommended entry point is run_pipeline.py,
    which runs pytest between the generation and QA stages.
    """
    generation = build_generation_crew()
    qa = build_qa_crew()
    return Crew(
        name="full-pipeline",
        agents=[*generation.agents, *qa.agents],
        tasks=[*generation.tasks, *qa.tasks],
        process=Process.sequential,
        verbose=True,
    )
