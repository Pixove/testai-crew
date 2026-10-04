"""Content fingerprints and cache state for incremental generation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.settings import Settings
from src.database.inspector import DatabaseInspector

CACHE_VERSION = "v1"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    if not path.exists():
        return ""
    return sha256_text(path.read_text(encoding="utf-8"))


def scenario_fingerprint(settings: Settings) -> str:
    """Hash the user scenario file."""
    return sha256_file(settings.scenario_input_path)


def schema_fingerprint(settings: Settings) -> str:
    """Hash the database schema, ignoring row data and row counts."""
    if not settings.database_path.exists():
        return ""
    with DatabaseInspector(settings.database_path) as inspector:
        payload: list[dict[str, Any]] = []
        for table in inspector.inspect_all():
            payload.append(
                {
                    "name": table["name"],
                    "columns": table["columns"],
                    "indexes": table["indexes"],
                    "foreign_keys": table["foreign_keys"],
                }
            )
    return sha256_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
    )


def build_run_key(scenario_hash: str, schema_hash: str) -> str:
    return sha256_text(f"{CACHE_VERSION}:{scenario_hash}:{schema_hash}")


def scenario_artifacts_exist(settings: Settings) -> bool:
    return settings.scenario_rules_path.exists()


def analysis_artifacts_exist(settings: Settings) -> bool:
    return all(
        path.exists()
        for path in (
            settings.business_scenarios_path,
            settings.test_cases_path,
            settings.test_data_path,
            settings.generated_test_suite_path,
        )
    )


@dataclass
class CacheState:
    scenario_hash: str = ""
    schema_hash: str = ""
    run_key: str = ""
    scenario_rules_hash: str = ""
    updated_at: str = ""

    @classmethod
    def load(cls, path: Path) -> "CacheState":
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        return cls(
            scenario_hash=str(data.get("scenario_hash", "")),
            schema_hash=str(data.get("schema_hash", "")),
            run_key=str(data.get("run_key", "")),
            scenario_rules_hash=str(data.get("scenario_rules_hash", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def save(self, path: Path) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
