"""Run the full scenario-driven test generation pipeline."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.crew.full_pipeline import build_generation_crew, build_qa_crew
from src.models.generated_suite import GeneratedTestSuite
from src.models.review import QualityMetrics as QualityMetricsModel
from src.models.review import ReviewReport
from src.quality.scorer import score_suite
from src.testing.pytest_runner import load_result, run_pytest, save_result


def write_generated_tests(settings) -> list[str]:
    suite_path = settings.generated_test_suite_path
    if not suite_path.exists():
        raise FileNotFoundError(f"Generated test suite not found: {suite_path}")
    suite = GeneratedTestSuite.model_validate_json(
        suite_path.read_text(encoding="utf-8")
    )
    base_dir = settings.automated_tests_dir.resolve()
    written: list[str] = []
    for test_file in suite.test_files:
        target = (base_dir / test_file.path).resolve()
        if not target.is_relative_to(base_dir):
            raise ValueError(f"Unsafe test file path: {test_file.path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(test_file.content, encoding="utf-8")
        print(f"Wrote: {target}")
        written.append(str(target))
    return written


def review_to_markdown(
    report: ReviewReport, pytest_result: dict | None = None
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


def apply_deterministic_score(settings) -> int:
    """Replace the model-provided score with a deterministic score."""
    metrics = score_suite(
        settings.scenario_rules_path,
        settings.business_scenarios_path,
        settings.test_cases_path,
        settings.test_data_path,
        settings.pytest_result_path,
    )
    coverage_path = settings.coverage_report_path
    if not coverage_path.exists():
        raise FileNotFoundError(f"Coverage report not found: {coverage_path}")
    report = ReviewReport.model_validate_json(
        coverage_path.read_text(encoding="utf-8")
    )
    report.quality_score = metrics.total_score
    report.quality_metrics = QualityMetricsModel.model_validate(metrics.to_dict())
    coverage_path.write_text(
        json.dumps(report.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return metrics.total_score


def write_review_reports(settings) -> None:
    coverage_path = settings.coverage_report_path
    if not coverage_path.exists():
        raise FileNotFoundError(f"Coverage report not found: {coverage_path}")
    report = ReviewReport.model_validate_json(
        coverage_path.read_text(encoding="utf-8")
    )
    pytest_result = load_result(settings.pytest_result_path)
    settings.review_report_path.write_text(
        review_to_markdown(report, pytest_result), encoding="utf-8"
    )
    print(f"Wrote: {settings.review_report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the full scenario-driven test generation pipeline"
    )
    parser.add_argument(
        "--scenario-file",
        default=None,
        help="Path to the scenario file (default: SCENARIO_INPUT_PATH)",
    )
    parser.add_argument(
        "--reuse-generation",
        action="store_true",
        help="Skip the generation crew and reuse existing artifacts",
    )
    parser.add_argument(
        "--reuse-review",
        action="store_true",
        help="Skip the QA crew and reuse the existing coverage report",
    )
    args = parser.parse_args()

    if args.scenario_file:
        os.environ["SCENARIO_INPUT_PATH"] = str(Path(args.scenario_file).resolve())

    settings = get_settings()

    print("=== [1/4] GENERATION STAGE ===")
    if args.reuse_generation:
        print("Reusing existing generation artifacts.")
    else:
        generation_crew = build_generation_crew()
        generation_result = generation_crew.kickoff()
        print(generation_result)

    test_files = write_generated_tests(settings)

    print("\n=== [2/4] PYTEST EXECUTION ===")
    pytest_result = run_pytest(
        test_files, settings.pytest_junit_path, PROJECT_ROOT
    )
    save_result(settings.pytest_result_path, pytest_result)
    print(
        f"pytest: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, "
        f"{pytest_result['errors']} errors "
        f"(total {pytest_result['total']})"
    )
    if pytest_result.get("rule_not_landed"):
        print(
            "规则未落地 failures: "
            f"{len(pytest_result['rule_not_landed'])}"
        )

    print("\n=== [3/4] QA REVIEW STAGE ===")
    if args.reuse_review:
        print("Reusing existing coverage report.")
    else:
        qa_crew = build_qa_crew()
        qa_result = qa_crew.kickoff()
        print(qa_result)

    score = apply_deterministic_score(settings)
    write_review_reports(settings)
    print(f"\n=== [4/4] DETERMINISTIC QUALITY SCORE: {score}/100 ===")

    print("\nOutputs:")
    print(f"  {settings.scenario_rules_path}")
    print(f"  {settings.business_scenarios_path}")
    print(f"  {settings.test_cases_path}")
    print(f"  {settings.test_data_path}")
    print(f"  {settings.generated_test_suite_path}")
    print(f"  {settings.pytest_result_path}")
    print(f"  {settings.coverage_report_path}")
    print(f"  {settings.review_report_path}")


if __name__ == "__main__":
    main()
