"""Scenario analyst agent definition."""

from __future__ import annotations

from crewai import Agent, LLM
from crewai.skills import load_skill

from config.settings import PROJECT_ROOT, get_settings
from tool.inspect_database import InspectDatabaseTool
from tool.read_scenario_file import ReadScenarioFileTool


def build_scenario_analyst() -> Agent:
    settings = get_settings()
    skill_path = PROJECT_ROOT / "skills" / "scenario-analysis" / "SKILL.md"
    skills = load_skill(skill_path.read_text(encoding="utf-8"))
    return Agent(
        role="场景解析员",
        goal="把用户提供的场景描述转换成结构化、可执行的业务规则",
        backstory=(
            "你是通用的业务规则分析专家，不依赖特定业务系统。你擅长从自然语言"
            "描述中提取目标表、字段、条件、约束和字段依赖关系。"
        ),
        llm=LLM(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
        ),
        tools=[ReadScenarioFileTool(), InspectDatabaseTool()],
        skills=skills,
        verbose=True,
    )
