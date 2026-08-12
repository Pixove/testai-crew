"""Pydantic models for QA review outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CoverageItem(BaseModel):
    rule_id: str = Field(description="Business rule id")
    rule_summary: str = Field(description="Short rule summary")
    scenario_count: int = Field(description="Scenarios linked to this rule")
    test_case_count: int = Field(description="Test cases linked to this rule")
    data_record_count: int = Field(description="Test data records linked to this rule")
    covered: bool = Field(description="Whether the rule is fully covered")
    notes: str = Field(description="Coverage notes or gaps")


class ReviewReport(BaseModel):
    source_files: list[str] = Field(description="Input artifacts used for review")
    summary: str = Field(description="Overall review summary")
    coverage_items: list[CoverageItem] = Field(
        description="Per-rule coverage matrix"
    )
    missing_combinations: list[str] = Field(
        description="Combinations that are missing from the test suite"
    )
    quality_score: int = Field(
        ge=0, le=100, description="Overall quality score from 0 to 100"
    )
    recommendations: list[str] = Field(
        description="Concrete improvement recommendations"
    )
    conclusion: str = Field(description="Final effect evaluation")
