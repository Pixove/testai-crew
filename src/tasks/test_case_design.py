"""Test case design task definition."""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import get_settings
from src.models.test_case import TestCaseDocument


def build_test_case_design_task(agent: Agent) -> Task:
    settings = get_settings()
    return Task(
        description=(
            "先使用 build_pairwise_matrix 工具获取最小 pairwise 组合矩阵。\n"
            "再使用 read_scenario_rules 工具读取字段依赖规则。\n"
            "再使用 read_business_scenarios 工具读取业务场景。\n"
            "再使用 inspect_database 工具核对真实字段名和类型。\n"
            "优先为 pairwise 矩阵中的每个组合生成一条用例，"
            "不要自行扩展成完整笛卡尔积。\n"
            "对没有结构化 dependencies 的规则，按业务语义补充边界和异常用例。\n"
            "组合用例要覆盖 allowed、forbidden、boundary 和 NULL 情况。\n"
            "每条用例保留 normal/boundary/exception 分类。\n"
            "每条用例必须包含 id、title、table、scenario_id、category、priority、"
            "rule_id、fields、preconditions、steps、test_data、expected_result、"
            "related_tables。\n"
            "source_file 必须填写 business_scenarios.json。\n"
            "测试数据必须具体并符合表字段类型，预期结果必须可验证。\n"
            "只输出纯 JSON，不要 Markdown 代码块、标题或额外解释。\n"
            "最终按 TestCaseDocument 结构输出 JSON。"
        ),
        expected_output=(
            "TestCaseDocument JSON：包含 source_file 和 test_cases，"
            "用例覆盖规则中的全部关键组合。"
        ),
        agent=agent,
        output_pydantic=TestCaseDocument,
        output_file=str(settings.test_cases_path),
        create_directory=True,
    )
