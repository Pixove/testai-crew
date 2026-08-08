"""Minimal CrewAI task used to validate the project skeleton."""

from __future__ import annotations

from crewai import Agent, Task


def build_minimal_task(agent: Agent) -> Task:
    return Task(
        description=(
            "使用 inspect_database 工具读取项目数据库，然后输出：\n"
            "1. 数据库包含哪些表；\n"
            "2. 每张表的行数；\n"
            "3. 用一句话概括这个数据库的业务场景。"
        ),
        expected_output=(
            "包含表名、行数和业务总结的清晰文本或 JSON 摘要。"
        ),
        agent=agent,
    )
