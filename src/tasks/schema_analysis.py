"""Database analysis task definition."""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import get_settings
from src.models.schema import BusinessScenarioDocument


def build_schema_analysis_task(agent: Agent) -> Task:
    settings = get_settings()
    return Task(
        description=(
            "先使用 read_scenario_rules 工具读取场景规则。\n"
            "再使用 inspect_database 工具读取相关表的真实结构。\n"
            "如果 schema 描述 JSON 存在，也可以参考字段业务含义。\n"
            "只分析规则涉及的表和字段，不要全库生成场景。\n"
            "为每条规则生成 normal/boundary/exception 三类场景。\n"
            "每个 scenario 必须填写 rule_id 和 fields。\n"
            "最终按 BusinessScenarioDocument 结构输出 JSON。"
        ),
        expected_output=(
            "BusinessScenarioDocument JSON：database、tables、scenarios，"
            "其中 scenarios 只覆盖规则相关表，且每条都关联 rule_id。"
        ),
        agent=agent,
        output_pydantic=BusinessScenarioDocument,
        output_file=str(settings.business_scenarios_path),
        create_directory=True,
    )
