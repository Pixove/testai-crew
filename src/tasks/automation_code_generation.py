"""Automation code generation task definition."""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import get_settings
from src.models.generated_suite import GeneratedTestSuite


def build_automation_code_generation_task(agent: Agent) -> Task:
    settings = get_settings()
    return Task(
        description=(
            "先使用 read_scenario_rules、read_test_cases、read_test_data "
            "工具读取规则、用例和测试数据。\n"
            "再使用 inspect_database 工具核对真实表结构。\n"
            "生成 conftest.py，必须通过 config.settings 的 DATABASE_PATH "
            "读取源数据库，不要用 glob 扫描目录。\n"
            "conftest 提供临时数据库副本 fixture，并开启外键约束。\n"
            "按表生成测试文件，例如 test_products.py。\n"
            "每个测试函数名对应 test_case_id，例如 test_tc_products_001。\n"
            "执行 SQL 前先检查字段是否存在，缺失时失败并输出“字段未落地”。\n"
            "按测试数据的 operation 执行 SQL，再按 expected_result 断言。\n"
            "规则要求拒绝但数据库接受时，失败并输出“规则未落地”。\n"
            "source_file 必须填写 test_cases.json。\n"
            "最终按 GeneratedTestSuite 结构输出 JSON。"
        ),
        expected_output=(
            "GeneratedTestSuite JSON：包含 source_file、summary 和 test_files，"
            "test_files 至少包含 conftest.py 和按表生成的测试文件。"
        ),
        agent=agent,
        output_pydantic=GeneratedTestSuite,
        output_file=str(settings.generated_test_suite_path),
        create_directory=True,
    )
