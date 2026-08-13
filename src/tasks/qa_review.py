"""QA review task definition."""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import get_settings
from src.models.review import ReviewReport


def build_qa_review_task(agent: Agent) -> Task:
    settings = get_settings()
    return Task(
        description=(
            "先使用 read_scenario_rules、read_business_scenarios、read_test_cases "
            "和 read_test_data 工具读取所有产物。\n"
            "再使用 inspect_database 工具核对真实表结构。\n"
            "为每条规则统计关联的场景数、用例数和数据记录数。\n"
            "检查组合矩阵是否覆盖 allowed、forbidden、boundary 和 NULL。\n"
            "列出缺失或覆盖不完整的组合。\n"
            "按 0 到 100 分给出质量评分，并给出改进建议和最终结论。\n"
            "只输出纯 JSON，不要 Markdown 代码块、标题或额外解释。\n"
            "最终按 ReviewReport 结构输出 JSON。"
        ),
        expected_output=(
            "ReviewReport JSON：包含 source_files、summary、coverage_items、"
            "missing_combinations、quality_score、recommendations、conclusion。"
        ),
        agent=agent,
        output_pydantic=ReviewReport,
        output_file=str(settings.coverage_report_path),
        create_directory=True,
    )
