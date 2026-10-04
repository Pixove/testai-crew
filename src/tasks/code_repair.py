"""Task for repairing generated pytest files that failed static validation."""

from __future__ import annotations

import json
from typing import Any

from crewai import Agent, Task

from config.settings import get_settings
from src.models.generated_suite import GeneratedTestSuite


def build_code_repair_task(
    agent: Agent, validation_report: dict[str, Any]
) -> Task:
    settings = get_settings()
    report_text = json.dumps(
        validation_report, ensure_ascii=False, indent=2
    )
    return Task(
        description=(
            "上一次生成的 pytest 代码未通过静态校验。\n"
            "先使用 read_generated_suite 工具读取当前测试套件。\n"
            "再使用 read_test_cases 和 read_test_data 工具核对用例与数据。\n"
            "根据以下校验问题修复代码：\n"
            f"{report_text}\n"
            "必须输出完整的测试套件内容，不能只输出差异片段。\n"
            "只输出纯 JSON，不要 Markdown 代码块、标题或额外解释。\n"
            "最终按 GeneratedTestSuite 结构输出 JSON。"
        ),
        expected_output=(
            "修复后的 GeneratedTestSuite JSON，包含完整的 conftest.py 和"
            "测试文件内容，且不再出现校验问题。"
        ),
        agent=agent,
        output_pydantic=GeneratedTestSuite,
        output_file=str(settings.generated_test_suite_path),
        create_directory=True,
    )
