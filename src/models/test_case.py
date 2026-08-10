"""Pydantic models for test case outputs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    id: str = Field(description="Stable test case id, e.g. TC-products-001")
    title: str = Field(description="Short Chinese test case title")
    table: str = Field(description="Primary table under test")
    scenario_id: str = Field(description="Source business scenario id")
    rule_id: str = Field(
        default="", description="Source business rule id from scenario_rules.json"
    )
    category: Literal["normal", "boundary", "exception"]
    priority: Literal["high", "medium", "low"]
    fields: list[str] = Field(
        default_factory=list, description="Fields covered by this test case"
    )
    preconditions: list[str] = Field(
        default_factory=list, description="Conditions that must exist before the test"
    )
    steps: list[str] = Field(
        default_factory=list, description="Concrete execution steps"
    )
    test_data: dict[str, Any] = Field(
        default_factory=dict, description="Concrete input data for the test"
    )
    expected_result: str = Field(description="Verifiable expected result")
    related_tables: list[str] = Field(
        default_factory=list, description="Other tables involved in the test"
    )


class TestCaseDocument(BaseModel):
    source_file: str = Field(
        description="Path of the business scenarios JSON used as input"
    )
    test_cases: list[TestCase] = Field(description="Generated test cases")
