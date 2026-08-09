"""Pydantic models for test data outputs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TestDataRecord(BaseModel):
    id: str = Field(description="Stable test data id, e.g. TD-products-001")
    test_case_id: str = Field(description="Target test case id")
    table: str = Field(description="Table this data targets")
    scenario_id: str = Field(description="Source business scenario id")
    category: Literal["normal", "boundary", "exception"]
    data_type: Literal["valid", "invalid", "boundary"]
    operation: Literal["insert", "update", "delete", "query"] = Field(
        default="insert", description="Intended database operation"
    )
    fields: dict[str, Any] = Field(
        description="Concrete field values for the record"
    )
    expected_result: str = Field(
        description="Expected behavior when this data is used"
    )


class TestDataDocument(BaseModel):
    source_file: str = Field(description="Path of the test cases JSON used as input")
    tables: list[str] = Field(description="Tables covered by the test data")
    records: list[TestDataRecord] = Field(description="Generated test data records")
