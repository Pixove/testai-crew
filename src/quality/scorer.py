"""Deterministic quality scoring for generated test suites.

The score is computed from the generated artifacts only, so the same inputs
always produce the same score. The LLM reviewer no longer decides the number.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.quality.combination_matrix import evaluate_combination_coverage
from src.models.scenario_rules import ScenarioRulesDocument
from src.models.schema import BusinessScenarioDocument
from src.models.test_case import TestCaseDocument
from src.models.test_data import TestDataDocument

WEIGHT_RULE_COVERAGE = 30.0
WEIGHT_COMBINATION_COVERAGE = 20.0
WEIGHT_CATEGORY_COVERAGE = 20.0
WEIGHT_DATA_COMPLETENESS = 15.0
WEIGHT_EXECUTION_PASS_RATE = 15.0
CATEGORIES = {"normal", "boundary", "exception"}


@dataclass
class QualityMetrics:
    rule_coverage: float
    combination_coverage: float
    category_coverage: float
    data_completeness: float
    execution_pass_rate: float
    rule_coverage_score: float
    combination_coverage_score: float
    category_coverage_score: float
    data_completeness_score: float
    execution_score: float
    total_score: int
    rules_total: int
    rules_fully_covered: int
    combinations_total: int
    combinations_covered: int
    combinations_unparsed: int
    test_cases_total: int
    test_cases_with_data: int
    tests_total: int
    tests_passed: int
    tests_failed: int
    tests_errors: int
    execution_available: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _pytest_stats(pytest_result_path: Path | None) -> dict[str, Any]:
    if pytest_result_path is None or not pytest_result_path.exists():
        return {
            "available": False,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "pass_rate": 0.0,
        }
    data = _load_json(pytest_result_path)
    total = int(data.get("total") or 0)
    skipped = int(data.get("skipped") or 0)
    passed = int(data.get("passed") or 0)
    failed = int(data.get("failed") or 0)
    errors = int(data.get("errors") or 0)
    executable = max(total - skipped, 0)
    return {
        "available": total > 0,
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": _ratio(passed, executable),
    }


def score_suite(
    scenario_rules_path: Path,
    business_scenarios_path: Path,
    test_cases_path: Path,
    test_data_path: Path,
    pytest_result_path: Path | None = None,
) -> QualityMetrics:
    """Compute a deterministic quality score from generated artifacts."""
    rules_doc = ScenarioRulesDocument.model_validate(
        _load_json(scenario_rules_path)
    )
    scenarios_doc = BusinessScenarioDocument.model_validate(
        _load_json(business_scenarios_path)
    )
    cases_doc = TestCaseDocument.model_validate(_load_json(test_cases_path))
    data_doc = TestDataDocument.model_validate(_load_json(test_data_path))

    rule_ids = [rule.id for rule in rules_doc.rules]
    scenarios_by_rule: dict[str, list] = defaultdict(list)
    cases_by_rule: dict[str, list] = defaultdict(list)
    categories_by_rule: dict[str, set[str]] = defaultdict(set)
    data_by_case: dict[str, list] = defaultdict(list)

    for scenario in scenarios_doc.scenarios:
        scenarios_by_rule[scenario.rule_id].append(scenario)
        if scenario.category in CATEGORIES:
            categories_by_rule[scenario.rule_id].add(scenario.category)

    for case in cases_doc.test_cases:
        cases_by_rule[case.rule_id].append(case)
        if case.category in CATEGORIES:
            categories_by_rule[case.rule_id].add(case.category)

    for record in data_doc.records:
        data_by_case[record.test_case_id].append(record)

    rules_fully_covered = 0
    category_ratios: list[float] = []
    for rule_id in rule_ids:
        has_scenario = bool(scenarios_by_rule[rule_id])
        has_case = bool(cases_by_rule[rule_id])
        has_data = any(
            data_by_case[case.id] for case in cases_by_rule[rule_id]
        )
        if has_scenario and has_case and has_data:
            rules_fully_covered += 1
        category_ratios.append(
            len(categories_by_rule[rule_id] & CATEGORIES) / len(CATEGORIES)
        )

    rule_coverage = _ratio(rules_fully_covered, len(rule_ids))
    combination = evaluate_combination_coverage(rules_doc, cases_doc)
    combination_coverage = combination.ratio
    category_coverage = (
        sum(category_ratios) / len(category_ratios) if category_ratios else 0.0
    )

    test_cases_total = len(cases_doc.test_cases)
    test_cases_with_data = sum(
        1 for case in cases_doc.test_cases if data_by_case[case.id]
    )
    data_completeness = _ratio(test_cases_with_data, test_cases_total)

    pytest_stats = _pytest_stats(pytest_result_path)
    execution_pass_rate = float(pytest_stats["pass_rate"])
    execution_available = bool(pytest_stats["available"])

    components: list[tuple[float, float]] = [
        (rule_coverage, WEIGHT_RULE_COVERAGE),
        (category_coverage, WEIGHT_CATEGORY_COVERAGE),
        (data_completeness, WEIGHT_DATA_COMPLETENESS),
    ]
    if combination.total > 0:
        components.append((combination_coverage, WEIGHT_COMBINATION_COVERAGE))
    if execution_available:
        components.append((execution_pass_rate, WEIGHT_EXECUTION_PASS_RATE))

    available_weight = sum(weight for _, weight in components)
    total = (
        sum(ratio * weight for ratio, weight in components)
        / available_weight
        * 100
        if available_weight
        else 0.0
    )

    rule_score = rule_coverage * WEIGHT_RULE_COVERAGE
    combination_score = (
        combination_coverage * WEIGHT_COMBINATION_COVERAGE
        if combination.total > 0
        else 0.0
    )
    category_score = category_coverage * WEIGHT_CATEGORY_COVERAGE
    data_score = data_completeness * WEIGHT_DATA_COMPLETENESS
    execution_score = (
        execution_pass_rate * WEIGHT_EXECUTION_PASS_RATE
        if execution_available
        else 0.0
    )

    return QualityMetrics(
        rule_coverage=round(rule_coverage, 4),
        combination_coverage=round(combination_coverage, 4),
        category_coverage=round(category_coverage, 4),
        data_completeness=round(data_completeness, 4),
        execution_pass_rate=round(execution_pass_rate, 4),
        rule_coverage_score=round(rule_score, 2),
        combination_coverage_score=round(combination_score, 2),
        category_coverage_score=round(category_score, 2),
        data_completeness_score=round(data_score, 2),
        execution_score=round(execution_score, 2),
        total_score=int(round(total)),
        rules_total=len(rule_ids),
        rules_fully_covered=rules_fully_covered,
        combinations_total=combination.total,
        combinations_covered=combination.covered,
        combinations_unparsed=len(combination.unparsed),
        test_cases_total=test_cases_total,
        test_cases_with_data=test_cases_with_data,
        tests_total=int(pytest_stats["total"]),
        tests_passed=int(pytest_stats["passed"]),
        tests_failed=int(pytest_stats["failed"]),
        tests_errors=int(pytest_stats["errors"]),
        execution_available=execution_available,
    )
