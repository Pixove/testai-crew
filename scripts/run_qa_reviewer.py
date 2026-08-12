"""Run the QA reviewer and write markdown and JSON reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.agents.qa_reviewer import build_qa_reviewer
from src.crew.qa_reviewer import build_qa_review_crew
from src.models.review import ReviewReport
from src.tasks.qa_review import build_qa_review_task


def _extract_json(text: str) -> ReviewReport:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Could not locate JSON object in response: {text[:200]}")
    return ReviewReport.model_validate_json(text[start : end + 1])


def _to_report(result: object) -> ReviewReport:
    if isinstance(result, ReviewReport):
        return result
    if isinstance(result, dict):
        if "raw" in result and "quality_score" not in result:
            raw = result.get("raw")
            if isinstance(raw, str):
                return _extract_json(raw)
            if isinstance(raw, dict):
                return ReviewReport.model_validate(raw)
        return ReviewReport.model_validate(result)
    if hasattr(result, "model_dump"):
        data = result.model_dump()
        if "raw" in data and "quality_score" not in data:
            raw = data.get("raw")
            if isinstance(raw, str):
                return _extract_json(raw)
            if isinstance(raw, dict):
                return ReviewReport.model_validate(raw)
        return ReviewReport.model_validate(data)
    return _extract_json(str(result))


def _to_markdown(report: ReviewReport) -> str:
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate QA review reports from the review model"
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="Reuse the existing coverage_report.json without calling the LLM",
    )
    args = parser.parse_args()

    settings = get_settings()
    if args.reuse and settings.coverage_report_path.exists():
        print(f"Reusing: {settings.coverage_report_path}")
        result = json.loads(settings.coverage_report_path.read_text(encoding="utf-8"))
    else:
        agent = build_qa_reviewer()
        task = build_qa_review_task(agent)
        crew = build_qa_review_crew(agent, task)
        result = crew.kickoff()
    report = _to_report(result)

    settings.coverage_report_path.write_text(
        json.dumps(report.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    settings.review_report_path.write_text(
        _to_markdown(report), encoding="utf-8"
    )

    print(f"\nSaved: {settings.coverage_report_path}")
    print(f"Saved: {settings.review_report_path}")
    print(f"Quality Score: {report.quality_score}/100")


if __name__ == "__main__":
    main()
