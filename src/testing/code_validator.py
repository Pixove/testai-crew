"""Static validation for generated pytest files.

Validation runs before pytest so that syntax errors or structurally broken
files can be repaired by the code generator instead of failing at runtime.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationIssue:
    path: str
    kind: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "kind": self.kind,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass
class ValidationReport:
    valid: bool
    checked_files: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "checked_files": self.checked_files,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def _test_function_count(tree: ast.AST) -> int:
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )


def validate_generated_files(files: dict[str, str]) -> ValidationReport:
    """Validate generated Python files by path and content."""
    issues: list[ValidationIssue] = []
    checked = sorted(files)

    if "conftest.py" not in files:
        issues.append(
            ValidationIssue(
                path="conftest.py",
                kind="missing_file",
                severity="error",
                message="生成的测试套件缺少 conftest.py",
            )
        )

    for path, content in sorted(files.items()):
        if not content or not content.strip():
            issues.append(
                ValidationIssue(
                    path=path,
                    kind="empty_file",
                    severity="error",
                    message="文件内容为空",
                )
            )
            continue

        try:
            tree = ast.parse(content, filename=path)
        except SyntaxError as exc:
            issues.append(
                ValidationIssue(
                    path=path,
                    kind="syntax_error",
                    severity="error",
                    message=(
                        f"第 {exc.lineno} 行语法错误: {exc.msg}"
                        if exc.lineno
                        else f"语法错误: {exc.msg}"
                    ),
                )
            )
            continue

        name = path.rsplit("/", 1)[-1]
        if name.startswith("test_") and _test_function_count(tree) == 0:
            issues.append(
                ValidationIssue(
                    path=path,
                    kind="missing_test_function",
                    severity="error",
                    message="测试文件没有任何 test_* 函数",
                )
            )

    return ValidationReport(
        valid=not any(issue.severity == "error" for issue in issues),
        checked_files=checked,
        issues=issues,
    )
