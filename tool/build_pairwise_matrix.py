"""CrewAI tool: build a minimized pairwise combination matrix."""

from __future__ import annotations

import json
from typing import Any

from crewai.tools import BaseTool

from config.settings import get_settings
from src.models.scenario_rules import ScenarioRulesDocument
from src.quality.pairwise import build_pairwise_matrix


class BuildPairwiseMatrixTool(BaseTool):
    name: str = "build_pairwise_matrix"
    description: str = (
        "Read scenario_rules.json and return machine-readable field levels plus "
        "a minimized pairwise combination matrix. Use these combinations as the "
        "primary test case list instead of generating the full cartesian "
        "product. No arguments are needed."
    )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        settings = get_settings()
        path = settings.scenario_rules_path
        if not path.exists():
            return f"Scenario rules file not found: {path}"
        rules_doc = ScenarioRulesDocument.model_validate_json(
            path.read_text(encoding="utf-8")
        )
        matrix = build_pairwise_matrix(rules_doc)
        return json.dumps(matrix.to_dict(), ensure_ascii=False, indent=2)
