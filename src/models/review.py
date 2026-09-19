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


class QualityMetrics(BaseModel):
    """Deterministic metrics computed from generated artifacts."""

    rule_coverage: float = Field(description="Ratio of fully covered rules")
    category_coverage: float = Field(
        description="Average normal/boundary/exception coverage ratio"
    )
    data_completeness: float = Field(
        description="Ratio of test cases that have test data"
    )
    execution_pass_rate: float = Field(
        description="pytest pass rate, 0 when execution data is unavailable"
    )
    rule_coverage_score: float = Field(description="Weighted rule coverage score")
    category_coverage_score: float = Field(
        description="Weighted category coverage score"
    )
    data_completeness_score: float = Field(
        description="Weighted data completeness score"
    )
    execution_score: float = Field(description="Weighted execution score")
    total_score: int = Field(ge=0, le=100, description="Final deterministic score")
    rules_total: int = Field(description="Total number of business rules")
    rules_fully_covered: int = Field(
        description="Rules that have scenarios, test cases and test data"
    )
    test_cases_total: int = Field(description="Total number of test cases")
    test_cases_with_data: int = Field(
        description="Test cases that have at least one data record"
    )
    tests_total: int = Field(description="Total pytest cases executed")
    tests_passed: int = Field(description="Passed pytest cases")
    tests_failed: int = Field(description="Failed pytest cases")
    tests_errors: int = Field(description="Errored pytest cases")
    execution_available: bool = Field(
        description="Whether pytest execution data was available"
    )


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
    quality_metrics: QualityMetrics | None = Field(
        default=None,
        description="Deterministic quality metrics computed by the pipeline",
    )
    recommendations: list[str] = Field(
        description="Concrete improvement recommendations"
    )
    conclusion: str = Field(description="Final effect evaluation")
