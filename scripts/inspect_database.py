"""Command line entry point for inspecting the SQLite database."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.database.inspector import DatabaseInspector


def _format_columns(columns: list[dict]) -> str:
    lines = []
    for column in columns:
        flags = []
        if column["primary_key"]:
            flags.append("PK")
        if column["not_null"]:
            flags.append("NOT NULL")
        suffix = f" ({', '.join(flags)})" if flags else ""
        lines.append(f"  - {column['name']} {column['type']}{suffix}")
    return "\n".join(lines)


def _format_inspection(data: dict | list[dict], db_path: str) -> str:
    lines = [f"Database: {db_path}"]
    if isinstance(data, list):
        lines.append(f"Tables: {len(data)}")
        for table in data:
            lines.append(f"\n[{table['name']}] rows={table['row_count']}")
            lines.append(_format_columns(table["columns"]))
            if table["indexes"]:
                for index in table["indexes"]:
                    lines.append(
                        f"  index: {index['name']} ({', '.join(index['columns'])})"
                    )
            for fk in table["foreign_keys"]:
                lines.append(
                    f"  FK: {fk['column']} -> "
                    f"{fk['references_table']}.{fk['references_column']}"
                )
    else:
        lines.append(f"[{data['name']}] rows={data['row_count']}")
        lines.append(_format_columns(data["columns"]))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect SQLite tables, columns and row counts"
    )
    parser.add_argument(
        "--db",
        default=None,
        help="SQLite database path (default: DATABASE_PATH from .env)",
    )
    parser.add_argument(
        "-t",
        "--table",
        default=None,
        help="Inspect only one table",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args()

    db_path = Path(args.db).resolve() if args.db else get_settings().database_path
    with DatabaseInspector(db_path) as inspector:
        data = inspector.inspect_table(args.table) if args.table else inspector.inspect_all()

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(_format_inspection(data, str(db_path)))


if __name__ == "__main__":
    main()
