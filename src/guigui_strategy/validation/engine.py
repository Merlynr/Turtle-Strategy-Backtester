from __future__ import annotations

import json
from datetime import datetime, timezone
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from guigui_strategy.reporting.contracts import ReportConfig, ReportInput, ReportValidationError
from guigui_strategy.reporting.engine import generate_report

from .contracts import (
    ValidationArtifactIndex,
    ValidationConfig,
    ValidationError,
    ValidationFinding,
    ValidationInput,
    ValidationResult,
)


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        return handle.read()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _artifact_index(artifact_root: Path) -> ValidationArtifactIndex:
    return ValidationArtifactIndex(
        validation_path=str(artifact_root / "meta" / "validation.json"),
        manifest_path=str(artifact_root / "manifest.json"),
        status_path=str(artifact_root / "status.json"),
        report_md_path=str(artifact_root / "report.md"),
        report_index_path=str(artifact_root / "reports" / "report-index.json"),
        report_summary_path=str(artifact_root / "reports" / "report-summary.json"),
        snapshot_paths=(str(artifact_root / "snapshots"),),
        decision_paths=(str(artifact_root / "decisions"),),
        execution_paths=(str(artifact_root / "execution"),),
        reports_paths=(str(artifact_root / "reports"),),
        meta_paths=(str(artifact_root / "meta"),),
    )


def _blocked(
    input_: ValidationInput,
    summary: str,
    findings: list[ValidationFinding],
) -> ValidationResult:
    validated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return ValidationResult(
        run_id=input_.run_id,
        symbol=input_.symbol,
        market=input_.market,
        cadence=input_.cadence,
        artifact_root=input_.artifact_root,
        status="blocked",
        summary=summary,
        validated_at=validated_at,
        checked_artifacts=(
            "manifest.json",
            "status.json",
            "report.md",
            "snapshots/",
            "decisions/",
            "execution/",
            "reports/",
            "meta/",
        ),
        findings=tuple(findings),
        artifact_index=_artifact_index(input_.artifact_root),
        config=input_.config,
    )


def _info(code: str, message: str, subject: str | None = None, **details: Any) -> ValidationFinding:
    return ValidationFinding(code=code, severity="info", message=message, subject=subject, details=details)


def _blocked_finding(code: str, message: str, subject: str | None = None, **details: Any) -> ValidationFinding:
    return ValidationFinding(code=code, severity="blocked", message=message, subject=subject, details=details)


def _validate_layout(artifact_root: Path) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    required_paths = [
        artifact_root / "manifest.json",
        artifact_root / "status.json",
        artifact_root / "report.md",
        artifact_root / "snapshots",
        artifact_root / "decisions",
        artifact_root / "execution",
        artifact_root / "reports",
        artifact_root / "meta",
    ]
    for path in required_paths:
        if not path.exists():
            kind = "directory" if path.suffix == "" and not path.name.endswith(".json") and path.name not in {"report.md"} else "file"
            findings.append(_blocked_finding("missing-artifact", f"missing required {kind}: {path.name}", str(path)))
    return findings


def _validate_identity(input_: ValidationInput, manifest: Any, status: Any) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    manifest_run_id = str(manifest.get("run_id"))
    status_run_id = str(status.get("run_id"))
    manifest_root = str(manifest.get("artifact_root"))
    if manifest_run_id != input_.run_id:
        findings.append(_blocked_finding("run-id-mismatch", "manifest run_id does not match validation input", "manifest.json", expected=input_.run_id, observed=manifest_run_id))
    if status_run_id != input_.run_id:
        findings.append(_blocked_finding("status-run-id-mismatch", "status run_id does not match validation input", "status.json", expected=input_.run_id, observed=status_run_id))
    if manifest_root != str(input_.artifact_root):
        findings.append(_blocked_finding("artifact-root-mismatch", "manifest artifact_root does not match validation input", "manifest.json", expected=str(input_.artifact_root), observed=manifest_root))
    if str(input_.status.get("run_id")) != input_.run_id:
        findings.append(_blocked_finding("input-status-mismatch", "validation input status run_id does not match validation input", "status input", expected=input_.run_id, observed=str(input_.status.get("run_id"))))
    if str(input_.manifest.get("run_id")) != input_.run_id:
        findings.append(_blocked_finding("input-manifest-mismatch", "validation input manifest run_id does not match validation input", "manifest input", expected=input_.run_id, observed=str(input_.manifest.get("run_id"))))
    return findings


def _validate_status_fields(status: Any, config: ValidationConfig) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    state = str(status.get("state"))
    if state not in config.allowed_completed_states:
        findings.append(
            _blocked_finding(
                "unexpected-status-state",
                "status state is not in the allowed completed states",
                "status.json",
                allowed=list(config.allowed_completed_states),
                observed=state,
            )
        )
    if str(status.get("current_node")) != "report-node":
        findings.append(_blocked_finding("unexpected-current-node", "current_node must remain report-node for a completed run", "status.json", observed=str(status.get("current_node"))))
    if str(status.get("last_completed_node")) != "report-node":
        findings.append(_blocked_finding("unexpected-last-node", "last_completed_node must be report-node", "status.json", observed=str(status.get("last_completed_node"))))
    if status.get("resume_from") is not None:
        findings.append(_blocked_finding("unexpected-resume-from", "resume_from must be null after report completion", "status.json", observed=status.get("resume_from")))
    return findings


def _validate_execution_artifacts(input_: ValidationInput, manifest: Any) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    artifact_root = input_.artifact_root
    execution_dir = artifact_root / "execution"
    nav_path = execution_dir / "nav.json"
    fills_path = execution_dir / "fills.jsonl"
    ledger_path = execution_dir / "ledger.jsonl"
    for path in (nav_path, fills_path, ledger_path):
        if not path.exists():
            findings.append(_blocked_finding("missing-execution-artifact", "missing required execution artifact", str(path)))
    if findings:
        return findings

    nav_rows = _read_json(nav_path)
    fills = _read_jsonl(fills_path)
    ledger_rows = _read_jsonl(ledger_path)
    if not isinstance(nav_rows, list) or not nav_rows:
        findings.append(_blocked_finding("invalid-nav", "execution/nav.json must contain a non-empty list", str(nav_path)))
        return findings

    for idx, row in enumerate(nav_rows):
        if not isinstance(row, dict):
            findings.append(_blocked_finding("invalid-nav-row", "nav rows must be objects", str(nav_path), row_index=idx))
            continue
        if "nav" not in row:
            findings.append(_blocked_finding("missing-nav-field", "nav row missing nav field", str(nav_path), row_index=idx))
    expected_run_id = str(input_.run_id)
    expected_symbol = str(input_.symbol)
    for idx, fill in enumerate(fills):
        if str(fill.get("run_id")) != expected_run_id:
            findings.append(_blocked_finding("fill-run-id-mismatch", "fill run_id does not match validation input", str(fills_path), row_index=idx, expected=expected_run_id, observed=str(fill.get("run_id"))))
        if str(fill.get("symbol")) != expected_symbol:
            findings.append(_blocked_finding("fill-symbol-mismatch", "fill symbol does not match validation input", str(fills_path), row_index=idx, expected=expected_symbol, observed=str(fill.get("symbol"))))
    for idx, row in enumerate(ledger_rows):
        if str(row.get("run_id")) != expected_run_id:
            findings.append(_blocked_finding("ledger-run-id-mismatch", "ledger run_id does not match validation input", str(ledger_path), row_index=idx, expected=expected_run_id, observed=str(row.get("run_id"))))
        if str(row.get("symbol")) != expected_symbol:
            findings.append(_blocked_finding("ledger-symbol-mismatch", "ledger symbol does not match validation input", str(ledger_path), row_index=idx, expected=expected_symbol, observed=str(row.get("symbol"))))
    return findings


def _report_result(input_: ValidationInput, manifest: Any, status: Any) -> tuple[list[ValidationFinding], str | None]:
    report_path = input_.artifact_root / "report.md"
    report_index_path = input_.artifact_root / "reports" / "report-index.json"
    report_summary_path = input_.artifact_root / "reports" / "report-summary.json"
    findings: list[ValidationFinding] = []
    for path in (report_path, report_index_path, report_summary_path):
        if not path.exists():
            findings.append(_blocked_finding("missing-report-artifact", "missing required report artifact", str(path)))
    if findings:
        return findings, None

    report_text = _read_text(report_path)
    actual_report_index = _read_json(report_index_path)
    actual_report_summary = _read_json(report_summary_path)

    report_input = ReportInput(
        run_id=input_.run_id,
        symbol=input_.symbol,
        market=input_.market,
        cadence=input_.cadence,
        asof_date=input_.asof_date,
        artifact_root=input_.artifact_root,
        manifest=manifest,
        status=status,
        config=ReportConfig(
            annualization_factor=input_.config.report_annualization_factor,
            sharpe_risk_free_rate=input_.config.report_sharpe_risk_free_rate,
        ),
    )
    try:
        expected_report = generate_report(report_input)
    except ReportValidationError as exc:
        findings.append(_blocked_finding("report-regeneration-failed", "report synthesis could not be regenerated", str(report_path), reason=exc.reason, issues=list(exc.issues)))
        return findings, None

    if report_text != expected_report.report_markdown:
        findings.append(_blocked_finding("report-markdown-mismatch", "stored report.md does not match regenerated report", str(report_path)))
    if actual_report_index != expected_report.report_index.to_record():
        findings.append(_blocked_finding("report-index-mismatch", "stored report index does not match regenerated report", str(report_index_path)))
    if actual_report_summary != expected_report.to_record():
        findings.append(_blocked_finding("report-summary-mismatch", "stored report summary does not match regenerated report", str(report_summary_path)))
    return findings, expected_report.report_markdown


def _golden_baseline(input_: ValidationInput, expected_report_markdown: str | None) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    if not input_.config.check_golden_baseline:
        return findings

    baseline_root = input_.config.golden_baseline_root
    assert baseline_root is not None
    if not baseline_root.exists():
        findings.append(_blocked_finding("missing-golden-baseline", "configured golden baseline root does not exist", str(baseline_root)))
        return findings

    baseline_manifest = _read_json(baseline_root / "manifest.json")
    baseline_status = _read_json(baseline_root / "status.json")
    baseline_report_input = ReportInput(
        run_id=str(baseline_manifest.get("run_id")),
        symbol=str(baseline_manifest.get("symbol")),
        market=str(baseline_manifest.get("market")),
        cadence=str(baseline_manifest.get("cadence")),
        asof_date=input_.asof_date,
        artifact_root=baseline_root,
        manifest=baseline_manifest,
        status=baseline_status,
        config=ReportConfig(
            annualization_factor=input_.config.report_annualization_factor,
            sharpe_risk_free_rate=input_.config.report_sharpe_risk_free_rate,
        ),
    )
    try:
        baseline_report = generate_report(baseline_report_input)
    except ReportValidationError as exc:
        findings.append(_blocked_finding("golden-baseline-invalid", "configured golden baseline could not be regenerated", str(baseline_root), reason=exc.reason, issues=list(exc.issues)))
        return findings

    if expected_report_markdown is not None and expected_report_markdown != baseline_report.report_markdown:
        findings.append(_blocked_finding("golden-baseline-mismatch", "current report markdown does not match the golden baseline", str(baseline_root)))
    if _read_json(baseline_root / "reports" / "report-index.json") != baseline_report.report_index.to_record():
        findings.append(_blocked_finding("golden-baseline-report-index-mismatch", "golden baseline report index is inconsistent", str(baseline_root / "reports" / "report-index.json")))
    if _read_json(baseline_root / "reports" / "report-summary.json") != baseline_report.to_record():
        findings.append(_blocked_finding("golden-baseline-report-summary-mismatch", "golden baseline report summary is inconsistent", str(baseline_root / "reports" / "report-summary.json")))
    return findings


def validate_run(input_: ValidationInput) -> ValidationResult:
    artifact_root = Path(input_.artifact_root)
    layout_findings = _validate_layout(artifact_root)
    if layout_findings:
        return _blocked(input_, "layout-incomplete", layout_findings)

    manifest = _read_json(artifact_root / "manifest.json")
    status = _read_json(artifact_root / "status.json")

    findings: list[ValidationFinding] = []
    findings.extend(_validate_identity(input_, manifest, status))
    findings.extend(_validate_status_fields(status, input_.config))
    findings.extend(_validate_execution_artifacts(input_, manifest))
    report_findings, expected_report_markdown = _report_result(input_, manifest, status)
    findings.extend(report_findings)
    findings.extend(_golden_baseline(input_, expected_report_markdown))

    if findings:
        validated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        summary = f"blocked: {len(findings)} finding(s)"
        return ValidationResult(
            run_id=input_.run_id,
            symbol=input_.symbol,
            market=input_.market,
            cadence=input_.cadence,
            artifact_root=input_.artifact_root,
            status="blocked",
            summary=summary,
            validated_at=validated_at,
            checked_artifacts=(
                "manifest.json",
                "status.json",
                "report.md",
                "snapshots/",
                "decisions/",
                "execution/",
                "reports/",
                "meta/",
            ),
            findings=tuple(findings),
            artifact_index=_artifact_index(input_.artifact_root),
            config=input_.config,
        )

    summary = "passed: run container, report outputs, and golden baseline are consistent"
    validated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return ValidationResult(
        run_id=input_.run_id,
        symbol=input_.symbol,
        market=input_.market,
        cadence=input_.cadence,
        artifact_root=input_.artifact_root,
        status="passed",
        summary=summary,
        validated_at=validated_at,
        checked_artifacts=(
            "manifest.json",
            "status.json",
            "report.md",
            "snapshots/",
            "decisions/",
            "execution/",
            "reports/",
            "meta/",
        ),
        findings=(
            _info("layout-checked", "required run container layout is present"),
            _info("identity-checked", "run identity and artifact root are consistent"),
            _info("execution-checked", "execution artifacts are internally consistent"),
            _info("report-checked", "report outputs match deterministic regeneration"),
            _info("baseline-checked", "golden baseline validation completed"),
        ),
        artifact_index=_artifact_index(input_.artifact_root),
        config=input_.config,
    )
