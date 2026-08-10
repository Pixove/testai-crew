"""Database analyst agent definition."""

from __future__ import annotations

from crewai import Agent, LLM
from crewai.skills import load_skill

from config.settings import PROJECT_ROOT, get_settings
from tool.inspect_database import InspectDatabaseTool
from tool.read_scenario_rules import ReadScenarioRulesTool
from tool.read_schema_json import ReadSchemaJsonTool


def build_database_analyst() -> Agent:
    settings = get_settings()
    skill_path = PROJECT_ROOT / "skills" / "db-schema-analysis" / "SKILL.md"
    skills = load_skill(skill_path.read_text(encoding="utf-8"))
    return Agent(
        role="数据库分析员",
        goal="基于用户场景规则，分析相关数据库表结构并提炼业务场景",
        backstory=(
            "你是通用的数据库分析专家，不依赖特定业务系统。你擅长根据用户规则"
            "定位相关表和字段，并通过只读工具理解真实表结构，产出针对性的业务场景。"
        ),
        llm=LLM(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
        ),
        tools=[
            ReadScenarioRulesTool(),
            InspectDatabaseTool(),
            ReadSchemaJsonTool(),
        ],
        skills=skills,
        verbose=True,
    )
