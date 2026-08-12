"""Pydantic models for generated test suite outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GeneratedTestFile(BaseModel):
    path: str = Field(
        description="Relative file path under the automated tests directory"
    )
    content: str = Field(description="Full Python test file content")


class GeneratedTestSuite(BaseModel):
    source_file: str = Field(description="Source test cases JSON used as input")
    summary: str = Field(description="Short summary of the generated suite")
    test_files: list[GeneratedTestFile] = Field(
        description="Generated pytest files"
    )
