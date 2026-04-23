from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

ALLOWED_VALIDATION_STATUSES = {"passed", "blocked"}
ALLOWED_FINDING_SEVERITIES = {"info", "warning", "blocked"}


class ValidationError(ValueError):
    def __init__(self, reason: str, issues: list[str] | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.issues = issues or [reason]


def _require_mapping(value: Any, reason: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(reason, [f"expected mapping, got {type(value).__name__}"])
    return value


def _decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValidationError("invalid-decimal", [f"unable to parse decimal: {value!r}"]) from exc


def _decimal_str(value: Decimal) -> str:
    return format(value.normalize() if value == value.to_integral() else value, "f")


@dataclass(frozen=True)
class ValidationConfig:
    check_golden_baseline: bool = False
    golden_baseline_root: Path | None = None
    report_annualization_factor: int = 252
    report_sharpe_risk_free_rate: Decimal = Decimal("0")
    allowed_runtime_metadata: tuple[str, ...] = ("validated_at",)
    allowed_completed_states: tuple[str, ...] = ("completed", "replay-ready")

    def __post_init__(self) -> None:
        if self.report_annualization_factor <= 0:
            raise ValidationError("invalid-report-annualization-factor", ["report_annualization_factor must be positive"])
        if self.check_golden_baseline and self.golden_baseline_root is None:
            raise ValidationError("missing-golden-baseline", ["golden_baseline_root is required when check_golden_baseline is true"])

    def to_record(self) -> dict[str, Any]:
        return {
            "check_golden_baseline": self.check_golden_baseline,
            "golden_baseline_root": str(self.golden_baseline_root) if self.golden_baseline_root is not None else None,
            "report_annualization_factor": self.report_annualization_factor,
            "report_sharpe_risk_free_rate": _decimal_str(self.report_sharpe_risk_free_rate),
            "allowed_runtime_metadata": list(self.allowed_runtime_metadata),
            "allowed_completed_states": list(self.allowed_completed_states),
        }


@dataclass(frozen=True)
class ValidationInput:
    run_id: str
    symbol: str
    market: str
    cadence: str
    asof_date: date
    artifact_root: Path
    manifest: Mapping[str, Any]
    status: Mapping[str, Any]
    config: ValidationConfig

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "symbol": self.symbol,
            "market": self.market,
            "cadence": self.cadence,
            "asof_date": self.asof_date.isoformat(),
            "artifact_root": str(self.artifact_root),
            "manifest": dict(self.manifest),
            "status": dict(self.status),
            "config": self.config.to_record(),
        }


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    severity: str
    message: str
    subject: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.severity not in ALLOWED_FINDING_SEVERITIES:
            raise ValidationError("invalid-finding-severity", [f"unsupported severity: {self.severity!r}"])

    def to_record(self) -> dict[str, Any]:
        record = {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "details": dict(self.details),
        }
        if self.subject is not None:
            record["subject"] = self.subject
        return record


@dataclass(frozen=True)
class ValidationArtifactIndex:
    validation_path: str
    manifest_path: str
    status_path: str
    report_md_path: str
    report_index_path: str
    report_summary_path: str
    snapshot_paths: tuple[str, ...]
    decision_paths: tuple[str, ...]
    execution_paths: tuple[str, ...]
    reports_paths: tuple[str, ...]
    meta_paths: tuple[str, ...]

    def to_record(self) -> dict[str, Any]:
        return {
            "validation_path": self.validation_path,
            "manifest_path": self.manifest_path,
            "status_path": self.status_path,
            "report_md_path": self.report_md_path,
            "report_index_path": self.report_index_path,
            "report_summary_path": self.report_summary_path,
            "snapshot_paths": list(self.snapshot_paths),
            "decision_paths": list(self.decision_paths),
            "execution_paths": list(self.execution_paths),
            "reports_paths": list(self.reports_paths),
            "meta_paths": list(self.meta_paths),
        }


@dataclass(frozen=True)
class ValidationResult:
    run_id: str
    symbol: str
    market: str
    cadence: str
    artifact_root: Path
    status: str
    summary: str
    validated_at: str
    checked_artifacts: tuple[str, ...]
    findings: tuple[ValidationFinding, ...]
    artifact_index: ValidationArtifactIndex
    config: ValidationConfig

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_VALIDATION_STATUSES:
            raise ValidationError("invalid-validation-status", [f"unsupported status: {self.status!r}"])

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "symbol": self.symbol,
            "market": self.market,
            "cadence": self.cadence,
            "artifact_root": str(self.artifact_root),
            "status": self.status,
            "summary": self.summary,
            "validated_at": self.validated_at,
            "checked_artifacts": list(self.checked_artifacts),
            "findings": [finding.to_record() for finding in self.findings],
            "artifact_index": self.artifact_index.to_record(),
            "config": self.config.to_record(),
        }
