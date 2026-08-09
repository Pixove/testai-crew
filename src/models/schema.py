"""Pydantic models for database analysis outputs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BusinessScenario(BaseModel):
    id: str = Field(description="Stable scenario id, e.g. products-normal-001")
    title: str = Field(description="Short Chinese scenario title")
    table: str = Field(description="Primary table this scenario targets")
    category: Literal["normal", "boundary", "exception"]
    priority: Literal["high", "medium", "low"]
    description: str = Field(description="What the scenario covers and why")
    related_tables: list[str] = Field(
        default_factory=list, description="Tables involved in this scenario"
    )


class BusinessScenarioDocument(BaseModel):
    database: str = Field(description="Database file path or name")
    tables: list[str] = Field(description="All analyzed tables")
    scenarios: list[BusinessScenario] = Field(description="All extracted scenarios")
