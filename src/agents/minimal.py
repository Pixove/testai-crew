"""Minimal CrewAI agent used to validate the project skeleton."""

from __future__ import annotations

from crewai import Agent, LLM

from config.settings import get_settings
from tool.inspect_database import InspectDatabaseTool


def build_minimal_agent() -> Agent:
    settings = get_settings()
    return Agent(
        role="数据库摘要助手",
        goal="读取项目数据库，并输出简洁清晰的中文摘要",
        backstory=(
            "你是校园二手交易平台的数据库分析助手。你善于读取表结构、行数和"
            "字段信息，并用简洁中文总结数据库的业务含义。"
        ),
        llm=LLM(
            model=settings.model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
        ),
        tools=[InspectDatabaseTool()],
        verbose=True,
    )
