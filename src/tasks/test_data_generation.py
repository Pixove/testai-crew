"""Test data generation task definition."""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import get_settings
from src.models.test_data import TestDataDocument


def build_test_data_generation_task(agent: Agent) -> Task:
    settings = get_settings()
    return Task(
        description=(
            "先使用 read_test_cases 工具读取测试用例文件。\n"
            "再使用 inspect_database 工具核对真实表结构和字段类型。\n"
            "为每个测试用例生成至少一条测试数据，覆盖 valid/invalid/boundary。\n"
            "字段名必须与表结构一致，主键不能冲突，外键引用要合理。\n"
            "source_file 必须填写 test_cases.json。\n"
            "最终按 TestDataDocument 结构输出 JSON。"
        ),
        expected_output=(
            "TestDataDocument JSON：包含 source_file、tables 和 records，"
            "每个测试用例至少对应一条测试数据。"
        ),
        agent=agent,
        output_pydantic=TestDataDocument,
        output_file=str(settings.test_data_path),
        create_directory=True,
    )
