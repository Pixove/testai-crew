"""Test data generator agent definition."""

from __future__ import annotations

from crewai import Agent, LLM
from crewai.skills import load_skill

from config.settings import PROJECT_ROOT, get_settings
from tool.inspect_database import InspectDatabaseTool
from tool.read_scenario_rules import ReadScenarioRulesTool
from tool.read_test_cases import ReadTestCasesTool


def build_test_data_generator() -> Agent:
    settings = get_settings()
    skill_path = PROJECT_ROOT / "skills" / "test-data-generation" / "SKILL.md"
    skills = load_skill(skill_path.read_text(encoding="utf-8"))
    return Agent(
        role="测试数据构造员",
        goal="为每条测试用例生成符合表结构、约束和业务语义的具体测试数据",
        backstory=(
            "你是通用的测试数据专家，不依赖特定业务系统。你擅长根据表结构和"
            "测试用例构造有效、无效和边界数据，并保证字段类型和引用关系正确。"
        ),
        llm=LLM(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
        ),
        tools=[
            ReadScenarioRulesTool(),
            ReadTestCasesTool(),
            InspectDatabaseTool(),
        ],
        skills=skills,
        verbose=True,
    )
