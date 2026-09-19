"""Render QA review reports as Markdown."""

from __future__ import annotations

from typing import Any

from src.models.review import ReviewReport


def review_to_markdown(
    report: ReviewReport, pytest_result: dict[str, Any] | None = None
) -> str:
    lines = [
        "# QA Review Report",
        "",
        report.summary,
        "",
        "## Coverage Matrix",
        "",
        "| Rule | Scenarios | Test Cases | Data Records | Covered |",
        "|------|-----------|------------|--------------|---------|",
    ]
    for item in report.coverage_items:
        lines.append(
            f"| {item.rule_id} | {item.scenario_count} | "
            f"{item.test_case_count} | {item.data_record_count} | "
            f"{item.covered} |"
        )
    lines.append("")
    lines.append("## Missing Combinations")
    if report.missing_combinations:
        for combo in report.missing_combinations:
            lines.append(f"- {combo}")
    else:
        lines.append("- None")

    if pytest_result:
        lines.append("")
        lines.append("## pytest Execution")
        lines.append("")
        lines.append(f"- Total: {pytest_result.get('total', 0)}")
        lines.append(f"- Passed: {pytest_result.get('passed', 0)}")
        lines.append(f"- Failed: {pytest_result.get('failed', 0)}")
        lines.append(f"- Errors: {pytest_result.get('errors', 0)}")
        lines.append(
            f"- Pass rate: {float(pytest_result.get('pass_rate', 0.0)):.2%}"
        )
        rule_gaps = pytest_result.get("rule_not_landed") or []
        if rule_gaps:
            lines.append("")
            lines.append("### 规则未落地失败")
            for name in rule_gaps:
                lines.append(f"- {name}")

    metrics = report.quality_metrics
    if metrics:
        lines.append("")
        lines.append("## Deterministic Quality Metrics")
        lines.append("")
        lines.append(
            f"- Rule coverage: {metrics.rules_fully_covered}/"
            f"{metrics.rules_total} ({metrics.rule_coverage:.2%})"
        )
        lines.append(f"- Category coverage: {metrics.category_coverage:.2%}")
        lines.append(
            f"- Data completeness: {metrics.test_cases_with_data}/"
            f"{metrics.test_cases_total} ({metrics.data_completeness:.2%})"
        )
        if metrics.execution_available:
            lines.append(
                f"- Execution pass rate: {metrics.execution_pass_rate:.2%}"
            )
        else:
            lines.append("- Execution pass rate: not available")

    lines.append("")
    lines.append(f"## Quality Score: {report.quality_score}/100")
    lines.append("")
    lines.append("## Recommendations")
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.append("")
    lines.append("## Conclusion")
    lines.append(report.conclusion)
    return "\n".join(lines)
