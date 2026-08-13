"""Run the full scenario-driven test generation pipeline."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.crew.full_pipeline import build_full_pipeline_crew
from src.models.generated_suite import GeneratedTestSuite
from src.models.review import ReviewReport


def write_generated_tests(settings) -> None:
    suite_path = settings.generated_test_suite_path
    if not suite_path.exists():
        raise FileNotFoundError(f"Generated test suite not found: {suite_path}")
    suite = GeneratedTestSuite.model_validate_json(
        suite_path.read_text(encoding="utf-8")
    )
    base_dir = settings.automated_tests_dir.resolve()
    for test_file in suite.test_files:
        target = (base_dir / test_file.path).resolve()
        if not target.is_relative_to(base_dir):
            raise ValueError(f"Unsafe test file path: {test_file.path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(test_file.content, encoding="utf-8")
        print(f"Wrote: {target}")


def review_to_markdown(report: ReviewReport) -> str:
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


def write_review_reports(settings) -> None:
    coverage_path = settings.coverage_report_path
    if not coverage_path.exists():
        raise FileNotFoundError(f"Coverage report not found: {coverage_path}")
    report = ReviewReport.model_validate_json(
        coverage_path.read_text(encoding="utf-8")
    )
    settings.review_report_path.write_text(
        review_to_markdown(report), encoding="utf-8"
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
    args = parser.parse_args()

    if args.scenario_file:
        os.environ["SCENARIO_INPUT_PATH"] = str(Path(args.scenario_file).resolve())

    settings = get_settings()
    crew = build_full_pipeline_crew()
    result = crew.kickoff()
    print("\n=== FULL PIPELINE RESULT ===")
    print(result)

    write_generated_tests(settings)
    write_review_reports(settings)

    print("\nOutputs:")
    print(f"  {settings.scenario_rules_path}")
    print(f"  {settings.business_scenarios_path}")
    print(f"  {settings.test_cases_path}")
    print(f"  {settings.test_data_path}")
    print(f"  {settings.generated_test_suite_path}")
    print(f"  {settings.coverage_report_path}")
    print(f"  {settings.review_report_path}")
    print(f"\nRun tests with: python -m pytest {settings.automated_tests_dir} -v")


if __name__ == "__main__":
    main()
