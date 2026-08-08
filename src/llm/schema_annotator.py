"""Annotate database tables with short LLM-generated descriptions."""

from __future__ import annotations

import json
import re
from typing import Any

from config.settings import Settings

SYSTEM_PROMPT = (
    "You are a database schema analyst. A user will give you the schema of one "
    "table and a few sample rows. Write one concise Chinese business description "
    "for that table, no more than 30 Chinese characters. Reply with JSON only, "
    'in this exact format: {"description": "..."}'
)


def build_table_prompt(
    table_info: dict[str, Any], samples: list[dict[str, Any]]
) -> str:
    """Combine table metadata and sample rows into a prompt for the LLM."""
    lines = [
        f"Table: {table_info['name']}",
        f"Row count: {table_info['row_count']}",
        "Columns:",
    ]
    for column in table_info["columns"]:
        parts = [f"- {column['name']} {column['type']}"]
        if column["primary_key"]:
            parts.append("PRIMARY KEY")
        if column["not_null"]:
            parts.append("NOT NULL")
        lines.append(" ".join(parts))

    if table_info.get("indexes"):
        lines.append("Indexes:")
        for index in table_info["indexes"]:
            lines.append(
                f"- {index['name']} ({', '.join(index['columns'])}) "
                f"unique={index['unique']}"
            )

    if table_info.get("foreign_keys"):
        lines.append("Foreign keys:")
        for fk in table_info["foreign_keys"]:
            lines.append(
                f"- {fk['column']} -> "
                f"{fk['references_table']}.{fk['references_column']}"
            )

    lines.append(f"Sample rows ({len(samples)}):")
    for index, sample in enumerate(samples, start=1):
        lines.append(f"{index}. {json.dumps(sample, ensure_ascii=False)}")
    return "\n".join(lines)


class SchemaAnnotator:
    """Uses an OpenAI-compatible chat API to describe tables."""

    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise ValueError("OPENAI_API_KEY is not set. Configure .env first.")
        from openai import OpenAI

        client_kwargs: dict[str, Any] = {"api_key": settings.api_key}
        if settings.base_url:
            client_kwargs["base_url"] = settings.base_url
        self._client = OpenAI(**client_kwargs)
        self.model_name = settings.model_name

    def describe_table(
        self, table_info: dict[str, Any], samples: list[dict[str, Any]]
    ) -> str:
        prompt = build_table_prompt(table_info, samples)
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        return self._parse_description(content)

    @staticmethod
    def _parse_description(content: str) -> str:
        cleaned = content.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        data = json.loads(cleaned)
        if isinstance(data, dict):
            if isinstance(data.get("description"), str) and data["description"].strip():
                return data["description"].strip()
            for value in data.values():
                if isinstance(value, str) and value.strip():
                    return value.strip()
        raise ValueError(f"Unexpected LLM response: {content}")
