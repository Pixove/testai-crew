"""Database analysis task definition."""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import get_settings
from src.models.schema import BusinessScenarioDocument


def build_schema_analysis_task(agent: Agent) -> Task:
    settings = get_settings()
    return Task(
        description=(
            "使用 inspect_database 工具读取数据库的表结构、字段、外键、索引和行数。\n"
            "然后为每张表提炼业务场景，必须覆盖正常流程(normal)、边界情况(boundary)"
            "和异常情况(exception)三类。\n"
            "最终按 BusinessScenarioDocument 结构输出 JSON。"
        ),
        expected_output=(
            "BusinessScenarioDocument JSON：database、tables、scenarios，"
            "其中 scenarios 至少覆盖每张表的正常/边界/异常场景。"
        ),
        agent=agent,
        output_pydantic=BusinessScenarioDocument,
        output_file=str(settings.business_scenarios_path),
        create_directory=True,
    )
