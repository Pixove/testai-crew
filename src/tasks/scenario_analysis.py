"""Scenario analysis task definition."""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import get_settings
from src.models.scenario_rules import ScenarioRulesDocument


def build_scenario_analysis_task(agent: Agent) -> Task:
    settings = get_settings()
    return Task(
        description=(
            "使用 read_scenario_file 工具读取用户场景文件。\n"
            "使用 inspect_database 工具确认真实表名和字段名。\n"
            "理解场景中的目标表、字段、条件和字段依赖关系。\n"
            "提取约束、允许值、禁止值、NULL 行为和边界情况。\n"
            "target_tables 和 BusinessRule.table 必须使用数据库真实表名，"
            "例如 products，不能使用“商品表”这类中文名称。\n"
            "不要编造场景文件中不存在的规则。\n"
            "只输出纯 JSON，不要 Markdown 代码块、标题或额外解释。\n"
            "最终按 ScenarioRulesDocument 结构输出 JSON。"
        ),
        expected_output=(
            "ScenarioRulesDocument JSON：包含 source_file、summary、"
            "target_tables 和 rules，规则覆盖场景中的所有字段关联。"
        ),
        agent=agent,
        output_pydantic=ScenarioRulesDocument,
        output_file=str(settings.scenario_rules_path),
        create_directory=True,
    )
