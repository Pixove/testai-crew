"""Automation code generator agent definition."""

from __future__ import annotations

from crewai import Agent, LLM
from crewai.skills import load_skill

from config.settings import PROJECT_ROOT, get_settings
from tool.inspect_database import InspectDatabaseTool
from tool.read_scenario_rules import ReadScenarioRulesTool
from tool.read_test_cases import ReadTestCasesTool
from tool.read_test_data import ReadTestDataTool


def build_automation_code_generator() -> Agent:
    settings = get_settings()
    skill_path = PROJECT_ROOT / "skills" / "pytest-automation" / "SKILL.md"
    skills = load_skill(skill_path.read_text(encoding="utf-8"))
    return Agent(
        role="自动化代码生成员",
        goal="把测试用例和测试数据转换成可执行的 pytest 测试代码",
        backstory=(
            "你是通用的自动化测试工程师，不依赖特定业务系统。你擅长生成结构清晰、"
            "可独立运行的 pytest 代码，并通过数据库副本验证规则是否落地。"
        ),
        llm=LLM(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
        ),
        tools=[
            ReadScenarioRulesTool(),
            ReadTestCasesTool(),
            ReadTestDataTool(),
            InspectDatabaseTool(),
        ],
        skills=skills,
        verbose=True,
    )
