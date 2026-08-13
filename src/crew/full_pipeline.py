"""Full Crew pipeline definition."""

from __future__ import annotations

from crewai import Crew, Process

from src.agents.automation_code_generator import build_automation_code_generator
from src.agents.database_analyst import build_database_analyst
from src.agents.qa_reviewer import build_qa_reviewer
from src.agents.scenario_analyst import build_scenario_analyst
from src.agents.test_case_designer import build_test_case_designer
from src.agents.test_data_generator import build_test_data_generator
from src.tasks.automation_code_generation import build_automation_code_generation_task
from src.tasks.qa_review import build_qa_review_task
from src.tasks.schema_analysis import build_schema_analysis_task
from src.tasks.scenario_analysis import build_scenario_analysis_task
from src.tasks.test_case_design import build_test_case_design_task
from src.tasks.test_data_generation import build_test_data_generation_task


def build_full_pipeline_crew() -> Crew:
    scenario_agent = build_scenario_analyst()
    database_agent = build_database_analyst()
    test_case_agent = build_test_case_designer()
    test_data_agent = build_test_data_generator()
    code_agent = build_automation_code_generator()
    qa_agent = build_qa_reviewer()

    scenario_task = build_scenario_analysis_task(scenario_agent)
    schema_task = build_schema_analysis_task(database_agent)
    test_case_task = build_test_case_design_task(test_case_agent)
    test_data_task = build_test_data_generation_task(test_data_agent)
    code_task = build_automation_code_generation_task(code_agent)
    qa_task = build_qa_review_task(qa_agent)

    return Crew(
        name="full-pipeline",
        agents=[
            scenario_agent,
            database_agent,
            test_case_agent,
            test_data_agent,
            code_agent,
            qa_agent,
        ],
        tasks=[
            scenario_task,
            schema_task,
            test_case_task,
            test_data_task,
            code_task,
            qa_task,
        ],
        process=Process.sequential,
        verbose=True,
    )
