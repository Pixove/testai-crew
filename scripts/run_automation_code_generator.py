"""Run the automation code generator and write pytest files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.agents.automation_code_generator import build_automation_code_generator
from src.crew.automation_code_generator import build_automation_code_generation_crew
from src.models.generated_suite import GeneratedTestSuite
from src.tasks.automation_code_generation import build_automation_code_generation_task


def _to_suite(result: object) -> GeneratedTestSuite:
    if isinstance(result, GeneratedTestSuite):
        return result
    if isinstance(result, dict):
        if "raw" in result and "test_files" not in result:
            raw = result.get("raw")
            if isinstance(raw, str):
                return GeneratedTestSuite.model_validate_json(raw)
            if isinstance(raw, dict):
                return GeneratedTestSuite.model_validate(raw)
        return GeneratedTestSuite.model_validate(result)
    if hasattr(result, "model_dump"):
        data = result.model_dump()
        if "raw" in data and "test_files" not in data:
            raw = data.get("raw")
            if isinstance(raw, str):
                return GeneratedTestSuite.model_validate_json(raw)
            if isinstance(raw, dict):
                return GeneratedTestSuite.model_validate(raw)
        return GeneratedTestSuite.model_validate(data)
    return GeneratedTestSuite.model_validate_json(str(result))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate pytest files from the generated test suite"
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="Reuse the existing generated_test_suite.json without calling the LLM",
    )
    args = parser.parse_args()

    settings = get_settings()
    agent = build_automation_code_generator()
    task = build_automation_code_generation_task(agent)
    crew = build_automation_code_generation_crew(agent, task)
    if args.reuse and settings.generated_test_suite_path.exists():
        print(f"Reusing: {settings.generated_test_suite_path}")
        result = json.loads(settings.generated_test_suite_path.read_text(encoding="utf-8"))
    else:
        result = crew.kickoff()
    suite = _to_suite(result)

    base_dir = settings.automated_tests_dir.resolve()
    for test_file in suite.test_files:
        target = (base_dir / test_file.path).resolve()
        if not target.is_relative_to(base_dir):
            raise ValueError(f"Unsafe test file path: {test_file.path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(test_file.content, encoding="utf-8")
        print(f"Wrote: {target}")

    print(f"\n=== SUMMARY ===")
    print(suite.summary)
    print(f"\nGenerated suite saved to: {settings.generated_test_suite_path}")
    print(f"Tests directory: {settings.automated_tests_dir}")


if __name__ == "__main__":
    main()
