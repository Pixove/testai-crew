"""Pydantic models for scenario rule outputs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FieldDependency(BaseModel):
    trigger_field: str = Field(description="Field that controls the rule")
    trigger_value: Any = Field(
        default=None, description="Value of the trigger field that activates the rule"
    )
    affected_field: str = Field(description="Field affected by the rule")
    allowed_values: list[Any] | None = Field(
        default=None, description="Allowed values for the affected field"
    )
    forbidden_values: list[Any] | None = Field(
        default=None, description="Forbidden values for the affected field"
    )
    null_behavior: str | None = Field(
        default=None, description="Expected behavior when fields are NULL"
    )
    description: str = Field(description="Rule description in Chinese")


class BusinessRule(BaseModel):
    id: str = Field(description="Stable rule id, e.g. RULE-products-001")
    summary: str = Field(description="Short Chinese rule summary")
    table: str = Field(description="Target table")
    fields: list[str] = Field(description="Fields involved in this rule")
    dependencies: list[FieldDependency] = Field(
        default_factory=list, description="Field dependency rules"
    )
    constraints: list[str] = Field(
        default_factory=list, description="Constraint statements"
    )
    boundary_notes: list[str] = Field(
        default_factory=list, description="Boundary or edge case notes"
    )
    expected_behavior: str = Field(
        description="Expected behavior when the rule is followed or violated"
    )


class ScenarioRulesDocument(BaseModel):
    source_file: str = Field(description="User scenario file path")
    summary: str = Field(description="Overall scenario summary")
    target_tables: list[str] = Field(description="Tables involved in the scenario")
    rules: list[BusinessRule] = Field(description="Extracted business rules")
