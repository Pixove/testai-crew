"""Generate a JSON schema document with LLM-generated table descriptions."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.database.inspector import DatabaseInspector
from src.llm.schema_annotator import SchemaAnnotator, build_table_prompt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build schema JSON with sample rows and LLM descriptions"
    )
    parser.add_argument(
        "--db",
        default=None,
        help="SQLite database path (default: DATABASE_PATH)",
    )
    parser.add_argument(
        "-t",
        "--table",
        default=None,
        help="Only process one table",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=3,
        help="Sample rows per table (default: 3)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="JSON output path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts without calling the LLM",
    )
    args = parser.parse_args()

    if args.sample_size < 1:
        parser.error("--sample-size must be >= 1")

    settings = get_settings()
    db_path = Path(args.db).resolve() if args.db else settings.database_path
    output_path = (
        Path(args.output).resolve() if args.output else settings.schema_output_path
    )

    annotator = None if args.dry_run else SchemaAnnotator(settings)
    annotated_tables = []

    with DatabaseInspector(db_path) as inspector:
        tables = [args.table] if args.table else inspector.list_tables()
        for table_name in tables:
            table_info = inspector.inspect_table(table_name)
            samples = inspector.get_sample_rows(table_name, args.sample_size)
            prompt = build_table_prompt(table_info, samples)

            if args.dry_run:
                print(f"===== {table_name} =====")
                print(prompt)
                print()
                continue

            description = annotator.describe_table(table_info, samples)
            annotated_tables.append(
                {**table_info, "description": description, "samples": samples}
            )
            print(f"{table_name}: {description}")

    if not args.dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "database": str(db_path),
            "tables": annotated_tables,
        }
        output_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
