"""Database analyst agent definition."""

from __future__ import annotations

from crewai import Agent, LLM
from crewai.skills import load_skill

from config.settings import PROJECT_ROOT, get_settings
from tool.inspect_database import InspectDatabaseTool


def build_database_analyst() -> Agent:
    settings = get_settings()
    skill_path = PROJECT_ROOT / "skills" / "db-schema-analysis" / "SKILL.md"
    skills = load_skill(skill_path.read_text(encoding="utf-8"))
    return Agent(
        role="数据库分析员",
        goal="分析任意数据库的表结构，并提炼正常、边界和异常业务场景",
        backstory=(
            "你是通用的数据库分析专家，不依赖特定业务系统。你擅长通过只读工具"
            "理解表、字段、外键和样本数据，并用结构化方式描述业务场景。"
        ),
        llm=LLM(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
        ),
        tools=[InspectDatabaseTool()],
        skills=skills,
        verbose=True,
    )
