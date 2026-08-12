"""Project settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        env_file = PROJECT_ROOT / ".env"
        if not env_file.exists():
            return
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
    database_path: Path
    schema_output_path: Path
    business_scenarios_path: Path
    test_cases_path: Path
    test_data_path: Path
    scenario_input_path: Path
    scenario_rules_path: Path
    automated_tests_dir: Path
    generated_test_suite_path: Path
    review_report_path: Path
    coverage_report_path: Path
    api_key: str
    model_name: str
    base_url: str | None


def get_settings() -> Settings:
    _load_dotenv()
    database_path = Path(os.getenv("DATABASE_PATH", "data/campus_trade.db"))
    if not database_path.is_absolute():
        database_path = PROJECT_ROOT / database_path
    schema_output_path = Path(
        os.getenv("SCHEMA_OUTPUT_PATH", "output/schema_descriptions.json")
    )
    if not schema_output_path.is_absolute():
        schema_output_path = PROJECT_ROOT / schema_output_path
    business_scenarios_path = Path(
        os.getenv("BUSINESS_SCENARIOS_PATH", "output/business_scenarios.json")
    )
    if not business_scenarios_path.is_absolute():
        business_scenarios_path = PROJECT_ROOT / business_scenarios_path
    test_cases_path = Path(
        os.getenv("TEST_CASES_PATH", "output/test_cases.json")
    )
    if not test_cases_path.is_absolute():
        test_cases_path = PROJECT_ROOT / test_cases_path
    test_data_path = Path(
        os.getenv("TEST_DATA_PATH", "output/test_data.json")
    )
    if not test_data_path.is_absolute():
        test_data_path = PROJECT_ROOT / test_data_path
    scenario_input_path = Path(
        os.getenv("SCENARIO_INPUT_PATH", "input/scenario.md")
    )
    if not scenario_input_path.is_absolute():
        scenario_input_path = PROJECT_ROOT / scenario_input_path
    scenario_rules_path = Path(
        os.getenv("SCENARIO_RULES_PATH", "output/scenario_rules.json")
    )
    if not scenario_rules_path.is_absolute():
        scenario_rules_path = PROJECT_ROOT / scenario_rules_path
    automated_tests_dir = Path(
        os.getenv("AUTOMATED_TESTS_DIR", "automated_tests")
    )
    if not automated_tests_dir.is_absolute():
        automated_tests_dir = PROJECT_ROOT / automated_tests_dir
    generated_test_suite_path = Path(
        os.getenv("GENERATED_TEST_SUITE_PATH", "output/generated_test_suite.json")
    )
    if not generated_test_suite_path.is_absolute():
        generated_test_suite_path = PROJECT_ROOT / generated_test_suite_path
    review_report_path = Path(
        os.getenv("REVIEW_REPORT_PATH", "output/review_report.md")
    )
    if not review_report_path.is_absolute():
        review_report_path = PROJECT_ROOT / review_report_path
    coverage_report_path = Path(
        os.getenv("COVERAGE_REPORT_PATH", "output/coverage_report.json")
    )
    if not coverage_report_path.is_absolute():
        coverage_report_path = PROJECT_ROOT / coverage_report_path
    return Settings(
        database_path=database_path,
        schema_output_path=schema_output_path,
        business_scenarios_path=business_scenarios_path,
        test_cases_path=test_cases_path,
        test_data_path=test_data_path,
        scenario_input_path=scenario_input_path,
        scenario_rules_path=scenario_rules_path,
        automated_tests_dir=automated_tests_dir,
        generated_test_suite_path=generated_test_suite_path,
        review_report_path=review_report_path,
        coverage_report_path=coverage_report_path,
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )
