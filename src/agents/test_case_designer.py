"""Test case designer agent definition."""

from __future__ import annotations

from crewai import Agent, LLM
from crewai.skills import load_skill

from config.settings import PROJECT_ROOT, get_settings
from tool.inspect_database import InspectDatabaseTool
from tool.read_business_scenarios import ReadBusinessScenariosTool
from tool.read_scenario_rules import ReadScenarioRulesTool


def build_test_case_designer() -> Agent:
    settings = get_settings()
    skill_path = PROJECT_ROOT / "skills" / "test-case-design" / "SKILL.md"
    skills = load_skill(skill_path.read_text(encoding="utf-8"))
    return Agent(
        role="测试用例设计师",
        goal="基于业务场景生成完整、具体、可执行的测试用例",
        backstory=(
            "你是通用的测试设计专家，不依赖特定业务系统。你擅长把业务场景"
            "转化为结构清晰、数据具体、预期结果可验证的测试用例。"
        ),
        llm=LLM(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
        ),
        tools=[
            ReadScenarioRulesTool(),
            ReadBusinessScenariosTool(),
            InspectDatabaseTool(),
        ],
        skills=skills,
        verbose=True,
    )
