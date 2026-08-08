"""Project settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        env_file = PROJECT_ROOT / ".env"
        if not env_file.exists():
            return
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
    database_path: Path
    api_key: str
    model_name: str
    base_url: str | None


def get_settings() -> Settings:
    _load_dotenv()
    database_path = Path(os.getenv("DATABASE_PATH", "data/campus_trade.db"))
    if not database_path.is_absolute():
        database_path = PROJECT_ROOT / database_path
    return Settings(
        database_path=database_path,
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )
