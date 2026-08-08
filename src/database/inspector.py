"""Read-only SQLite inspector for tables, columns and row counts."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class DatabaseInspector:
    """Opens a SQLite database read-only and exposes schema metadata."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path).resolve()
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        self._connection = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        self._connection.row_factory = sqlite3.Row

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "DatabaseInspector":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def list_tables(self) -> list[str]:
        rows = self._connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        return [str(row["name"]) for row in rows]

    def get_columns(self, table: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(f"PRAGMA table_info({self._quote(table)})")
        return [
            {
                "name": row["name"],
                "type": row["type"],
                "not_null": bool(row["notnull"]),
                "default": row["dflt_value"],
                "primary_key": bool(row["pk"]),
            }
            for row in rows
        ]

    def get_indexes(self, table: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(f"PRAGMA index_list({self._quote(table)})")
        indexes = []
        for row in rows:
            index_name = str(row["name"])
            index_columns = [
                str(column["name"])
                for column in self._connection.execute(
                    f"PRAGMA index_info({self._quote(index_name)})"
                )
            ]
            indexes.append(
                {
                    "name": index_name,
                    "unique": bool(row["unique"]),
                    "columns": index_columns,
                }
            )
        return indexes

    def get_foreign_keys(self, table: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            f"PRAGMA foreign_key_list({self._quote(table)})"
        )
        return [
            {
                "column": row["from"],
                "references_table": row["table"],
                "references_column": row["to"],
            }
            for row in rows
        ]

    def count_rows(self, table: str) -> int:
        row = self._connection.execute(
            f'SELECT COUNT(*) AS count FROM {self._quote(table)}'
        ).fetchone()
        return int(row["count"])

    def inspect_table(self, table: str) -> dict[str, Any]:
        if table not in self.list_tables():
            raise ValueError(f"Unknown table: {table}")
        return {
            "name": table,
            "row_count": self.count_rows(table),
            "columns": self.get_columns(table),
            "indexes": self.get_indexes(table),
            "foreign_keys": self.get_foreign_keys(table),
        }

    def inspect_all(self) -> list[dict[str, Any]]:
        return [self.inspect_table(table) for table in self.list_tables()]

    @staticmethod
    def _quote(identifier: str) -> str:
        return '"' + identifier.replace('"', '""') + '"'
