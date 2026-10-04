"""Pairwise combination minimization for rule field values.

Full cartesian products grow quickly as more fields are involved. Pairwise
coverage keeps every pair of field values covered while using far fewer
cases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from math import prod
from typing import Any

from src.models.scenario_rules import ScenarioRulesDocument
from src.quality.combination_matrix import ValueSpec, parse_value_spec


@dataclass
class PairwiseMatrix:
    fields: list[str] = field(default_factory=list)
    levels: dict[str, list[Any]] = field(default_factory=dict)
    combinations: list[dict[str, Any]] = field(default_factory=list)
    full_cartesian_size: int = 0
    reduction_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "fields": self.fields,
            "levels": self.levels,
            "combinations": self.combinations,
            "combination_count": len(self.combinations),
            "full_cartesian_size": self.full_cartesian_size,
            "reduction_ratio": self.reduction_ratio,
        }


def sample_spec(spec: ValueSpec) -> Any:
    """Pick one representative value from a literal or range spec."""
    if spec[0] == "literal":
        return spec[1]
    if spec[0] == "range":
        _, op, target = spec
        if op == ">":
            return 1.0 if target == 0 else target + 1
        if op == "<":
            return -1.0 if target == 0 else target - 1
        if op in (">=", "<="):
            return target
    return None


def extract_field_levels(
    rules_doc: ScenarioRulesDocument,
) -> dict[str, list[Any]]:
    """Extract machine-readable value levels per field."""
    levels: dict[str, list[Any]] = {}

    def add(field_name: str, value: Any) -> None:
        bucket = levels.setdefault(field_name, [])
        if value not in bucket:
            bucket.append(value)

    for rule in rules_doc.rules:
        for dependency in rule.dependencies:
            trigger_spec = parse_value_spec(dependency.trigger_value)
            trigger_optional = trigger_spec == ("literal", None)
            if trigger_spec is not None and not trigger_optional:
                add(dependency.trigger_field, sample_spec(trigger_spec))

            for expectation_values in (
                dependency.allowed_values,
                dependency.forbidden_values,
            ):
                for raw_value in expectation_values or []:
                    spec = parse_value_spec(raw_value)
                    if spec is not None:
                        add(dependency.affected_field, sample_spec(spec))

    return levels


def generate_pairwise(
    levels: dict[str, list[Any]],
) -> list[dict[str, Any]]:
    """Greedy pairwise coverage: cover every value pair with fewer cases."""
    fields = [name for name, values in levels.items() if values]
    if not fields:
        return []
    if len(fields) == 1:
        return [{fields[0]: value} for value in levels[fields[0]]]

    uncovered: set[tuple[str, Any, str, Any]] = set()
    for left, right in combinations(fields, 2):
        for left_value in levels[left]:
            for right_value in levels[right]:
                uncovered.add((left, left_value, right, right_value))

    cases: list[dict[str, Any]] = []
    while uncovered:
        left, left_value, right, right_value = next(iter(uncovered))
        case: dict[str, Any] = {left: left_value, right: right_value}

        for name in fields:
            if name in case:
                continue
            best_value = levels[name][0]
            best_gain = -1
            for value in levels[name]:
                gain = 0
                for other, other_value in case.items():
                    if (
                        name,
                        value,
                        other,
                        other_value,
                    ) in uncovered or (
                        other,
                        other_value,
                        name,
                        value,
                    ) in uncovered:
                        gain += 1
                if gain > best_gain:
                    best_gain = gain
                    best_value = value
            case[name] = best_value

        cases.append(case)
        for index, first in enumerate(fields):
            for second in fields[index + 1 :]:
                uncovered.discard(
                    (first, case[first], second, case[second])
                )

    return cases


def build_pairwise_matrix(
    rules_doc: ScenarioRulesDocument,
) -> PairwiseMatrix:
    levels = extract_field_levels(rules_doc)
    cases = generate_pairwise(levels)
    fields = [name for name, values in levels.items() if values]
    full_size = prod(len(levels[name]) for name in fields) if fields else 0
    reduction = (
        round(1 - len(cases) / full_size, 4) if full_size > 0 else 0.0
    )
    return PairwiseMatrix(
        fields=fields,
        levels=levels,
        combinations=cases,
        full_cartesian_size=full_size,
        reduction_ratio=reduction,
    )
