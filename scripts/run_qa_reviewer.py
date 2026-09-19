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
from src.models.review import QualityMetrics as QualityMetricsModel
from src.models.review import ReviewReport
from src.quality.report import review_to_markdown
from src.quality.scorer import score_suite
from src.tasks.qa_review import build_qa_review_task
from src.testing.pytest_runner import load_result


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

    artifacts = [
        settings.scenario_rules_path,
        settings.business_scenarios_path,
        settings.test_cases_path,
        settings.test_data_path,
    ]
    if all(path.exists() for path in artifacts):
        metrics = score_suite(
            settings.scenario_rules_path,
            settings.business_scenarios_path,
            settings.test_cases_path,
            settings.test_data_path,
            settings.pytest_result_path,
        )
        report.quality_score = metrics.total_score
        report.quality_metrics = QualityMetricsModel.model_validate(
            metrics.to_dict()
        )

    settings.coverage_report_path.write_text(
        json.dumps(report.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    pytest_result = load_result(settings.pytest_result_path)
    settings.review_report_path.write_text(
        review_to_markdown(report, pytest_result), encoding="utf-8"
    )

    print(f"\nSaved: {settings.coverage_report_path}")
    print(f"Saved: {settings.review_report_path}")
    print(f"Quality Score: {report.quality_score}/100")


if __name__ == "__main__":
    main()
