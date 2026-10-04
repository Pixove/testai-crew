"""Per-stage run metrics: duration, token usage and retries."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class StageMetrics:
    stage: str
    duration_seconds: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_prompt_tokens: int = 0
    reasoning_tokens: int = 0
    successful_requests: int = 0
    retry_count: int = 0
    tasks: int = 0
    tools_used: int = 0
    tool_errors: int = 0
    skipped: bool = False
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _get_int(source: Any, name: str) -> int:
    if source is None:
        return 0
    if isinstance(source, dict):
        value = source.get(name)
    else:
        value = getattr(source, name, None)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _get_len(source: Any, name: str) -> int:
    if source is None:
        return 0
    value = source.get(name) if isinstance(source, dict) else getattr(
        source, name, None
    )
    try:
        return len(value or [])
    except TypeError:
        return 0


class MetricsCollector:
    """Collect stage-level metrics and write them to a JSON file."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.stages: list[StageMetrics] = []

    def record(
        self,
        stage: str,
        crew: Any = None,
        duration_seconds: float = 0.0,
        skipped: bool = False,
        error: str = "",
    ) -> StageMetrics:
        metrics = StageMetrics(
            stage=stage,
            duration_seconds=round(float(duration_seconds), 3),
            skipped=skipped,
            error=error,
        )

        usage = getattr(crew, "usage_metrics", None)
        if usage is None:
            usage = getattr(crew, "token_usage", None)

        metrics.prompt_tokens = _get_int(usage, "prompt_tokens")
        metrics.completion_tokens = _get_int(usage, "completion_tokens")
        metrics.total_tokens = _get_int(usage, "total_tokens")
        metrics.cached_prompt_tokens = _get_int(usage, "cached_prompt_tokens")
        metrics.reasoning_tokens = _get_int(usage, "reasoning_tokens")
        metrics.successful_requests = _get_int(usage, "successful_requests")

        tasks = getattr(crew, "tasks", None) or []
        metrics.tasks = len(tasks)
        for task in tasks:
            metrics.retry_count += _get_int(task, "retry_count")
            metrics.tools_used += _get_len(task, "used_tools")
            metrics.tool_errors += _get_len(task, "tools_errors")

        self.stages.append(metrics)
        return metrics

    @property
    def total_tokens(self) -> int:
        return sum(stage.total_tokens for stage in self.stages)

    @property
    def total_duration_seconds(self) -> float:
        return round(
            sum(stage.duration_seconds for stage in self.stages), 3
        )

    def save(self) -> Path:
        payload = {
            "started_at": self.started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "total_duration_seconds": self.total_duration_seconds,
            "total_tokens": self.total_tokens,
            "stages": [stage.to_dict() for stage in self.stages],
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self.output_path

    def summary(self) -> str:
        executed = sum(1 for stage in self.stages if not stage.skipped)
        skipped = sum(1 for stage in self.stages if stage.skipped)
        return (
            f"stages={len(self.stages)} (executed={executed}, skipped={skipped}), "
            f"tokens={self.total_tokens}, "
            f"duration={self.total_duration_seconds:.1f}s"
        )
