from __future__ import annotations

from pathlib import Path

from .contracts import ValidationInput, ValidationResult
from .engine import validate_run
from .persistence import persist_validation_result


def run_validation(input_: ValidationInput) -> ValidationResult:
    result = validate_run(input_)
    persist_validation_result(Path(input_.artifact_root), result)
    return result

