"""Test case design task definition."""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import get_settings
from src.models.test_case import TestCaseDocument


def build_test_case_design_task(agent: Agent) -> Task:
    settings = get_settings()
    return Task(
        description=(
            "先使用 read_business_scenarios 工具读取业务场景文件。\n"
            "然后为每个场景设计测试用例，保留 normal/boundary/exception 分类。\n"
            "每条用例必须包含 id、title、table、scenario_id、category、priority、"
            "preconditions、steps、test_data、expected_result、related_tables。\n"
            "测试数据必须具体并符合表字段类型，预期结果必须可验证。\n"
            "最终按 TestCaseDocument 结构输出 JSON。"
        ),
        expected_output=(
            "TestCaseDocument JSON：包含 source_file 和 test_cases，"
            "用例数量与业务场景一一对应。"
        ),
        agent=agent,
        output_pydantic=TestCaseDocument,
        output_file=str(settings.test_cases_path),
        create_directory=True,
    )
