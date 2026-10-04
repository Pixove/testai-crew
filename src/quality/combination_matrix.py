"""Programmatic combination coverage for field-dependency rules.

The reviewer used to rely on the LLM to judge whether every meaningful
combination was covered. This module builds the expected combination list
from ``scenario_rules.json`` and checks it against generated test data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.models.scenario_rules import ScenarioRulesDocument
from src.models.test_case import TestCaseDocument

ValueSpec = tuple[str, ...]


@dataclass
class ExpectedCombination:
    rule_id: str
    trigger_field: str
    trigger_spec: ValueSpec
    trigger_optional: bool
    affected_field: str
    affected_spec: ValueSpec
    expectation: str
    description: str


@dataclass
class CombinationCoverage:
    total: int
    covered: int
    ratio: float
    uncovered: list[dict[str, Any]] = field(default_factory=list)
    unparsed: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "covered": self.covered,
            "ratio": self.ratio,
            "uncovered": self.uncovered,
            "unparsed": self.unparsed,
        }


def parse_value_spec(value: Any) -> ValueSpec | None:
    """Convert a raw rule value into a comparable literal or range spec."""
    if value is None:
        return ("literal", None)
    if isinstance(value, bool):
        return ("literal", value)
    if isinstance(value, (int, float)):
        return ("literal", value)
    if isinstance(value, str):
        text = value.strip()
        for op in (">=", "<=", ">", "<"):
            if text.startswith(op):
                rest = text[len(op) :].split("（")[0].split("(")[0].strip()
                try:
                    return ("range", op, float(rest))
                except ValueError:
                    return None
        if any(
            marker in text
            for marker in ("不等于", "任何", "任意", "范围", "必须", "值（")
        ):
            return None
        if len(text) <= 20 and "（" not in text and "(" not in text:
            return ("literal", text)
    return None


def _equal(actual: Any, expected: Any) -> bool:
    if actual is None or expected is None:
        return actual is None and expected is None
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return float(actual) == float(expected)
    return str(actual) == str(expected)


def matches_value(actual: Any, spec: ValueSpec) -> bool:
    kind = spec[0]
    if kind == "literal":
        return _equal(actual, spec[1])
    if kind == "range":
        if actual is None:
            return False
        try:
            number = float(actual)
        except (TypeError, ValueError):
            return False
        _, op, target = spec
        if op == ">":
            return number > target
        if op == "<":
            return number < target
        if op == ">=":
            return number >= target
        if op == "<=":
            return number <= target
    return False


def build_expected_combinations(
    rules_doc: ScenarioRulesDocument,
) -> tuple[list[ExpectedCombination], list[dict[str, Any]]]:
    expected: list[ExpectedCombination] = []
    unparsed: list[dict[str, Any]] = []

    for rule in rules_doc.rules:
        if not rule.dependencies:
            unparsed.append(
                {
                    "rule_id": rule.id,
                    "field": ",".join(rule.fields),
                    "value": rule.constraints,
                    "reason": (
                        "rule has no structured dependencies; constraints are "
                        "natural language only"
                    ),
                }
            )
            continue
        for dependency in rule.dependencies:
            trigger_spec = parse_value_spec(dependency.trigger_value)
            trigger_optional = trigger_spec == ("literal", None)
            if trigger_spec is None:
                unparsed.append(
                    {
                        "rule_id": rule.id,
                        "field": dependency.trigger_field,
                        "value": dependency.trigger_value,
                        "reason": "trigger_value is not machine-readable",
                    }
                )
                continue

            for expectation, values in (
                ("allowed", dependency.allowed_values),
                ("forbidden", dependency.forbidden_values),
            ):
                for raw_value in values or []:
                    affected_spec = parse_value_spec(raw_value)
                    if affected_spec is None:
                        unparsed.append(
                            {
                                "rule_id": rule.id,
                                "field": dependency.affected_field,
                                "value": raw_value,
                                "reason": f"{expectation}_value is not machine-readable",
                            }
                        )
                        continue
                    expected.append(
                        ExpectedCombination(
                            rule_id=rule.id,
                            trigger_field=dependency.trigger_field,
                            trigger_spec=trigger_spec,
                            trigger_optional=trigger_optional,
                            affected_field=dependency.affected_field,
                            affected_spec=affected_spec,
                            expectation=expectation,
                            description=dependency.description,
                        )
                    )
    return expected, unparsed


def evaluate_combination_coverage(
    rules_doc: ScenarioRulesDocument,
    cases_doc: TestCaseDocument,
) -> CombinationCoverage:
    expected, unparsed = build_expected_combinations(rules_doc)
    cases_by_rule: dict[str, list] = {}
    for case in cases_doc.test_cases:
        cases_by_rule.setdefault(case.rule_id, []).append(case)

    covered = 0
    uncovered: list[dict[str, Any]] = []
    for combination in expected:
        matched = False
        for case in cases_by_rule.get(combination.rule_id, []):
            data = case.test_data or {}
            if not data:
                continue
            trigger_ok = combination.trigger_optional or matches_value(
                data.get(combination.trigger_field), combination.trigger_spec
            )
            if not trigger_ok:
                continue
            if matches_value(
                data.get(combination.affected_field), combination.affected_spec
            ):
                matched = True
                break
        if matched:
            covered += 1
        else:
            uncovered.append(
                {
                    "rule_id": combination.rule_id,
                    "trigger_field": combination.trigger_field,
                    "trigger_spec": list(combination.trigger_spec),
                    "affected_field": combination.affected_field,
                    "affected_spec": list(combination.affected_spec),
                    "expectation": combination.expectation,
                }
            )

    total = len(expected)
    ratio = covered / total if total else 1.0
    return CombinationCoverage(
        total=total,
        covered=covered,
        ratio=round(ratio, 4),
        uncovered=uncovered,
        unparsed=unparsed,
    )
