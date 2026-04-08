"""CTO-level trace report generator for AegisAP (Day 14).

The CTO report aggregates all 17 acceptance gate results plus key
operational metrics into a single executive-ready JSON artifact
(`build/day14/cto_trace_report.json`).

This artifact is the final deliverable of Day 14 and the exit criterion
for the full 14-day programme.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class GateSummary:
    name: str
    passed: bool
    detail: str
    day: int


@dataclass
class CtoReport:
    generated_at: str
    programme_days: int
    gates_total: int
    gates_passed: int
    gates_failed: int
    operational_metrics: dict[str, Any]
    gate_details: list[GateSummary] = field(default_factory=list)
    breaking_changes_drills_passed: int = 0
    breaking_changes_drills_total: int = 10

    @property
    def overall_passed(self) -> bool:
        return self.gates_failed == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "programme_days": self.programme_days,
            "overall_passed": self.overall_passed,
            "gates": {
                "total": self.gates_total,
                "passed": self.gates_passed,
                "failed": self.gates_failed,
            },
            "breaking_changes_drills": {
                "passed": self.breaking_changes_drills_passed,
                "total": self.breaking_changes_drills_total,
            },
            "operational_metrics": self.operational_metrics,
            "gate_details": [
                {
                    "name": g.name,
                    "passed": g.passed,
                    "detail": g.detail,
                    "day": g.day,
                }
                for g in self.gate_details
            ],
        }


class CtoReportGenerator:
    """Aggregate gate results and metrics into a CTO report."""

    _GATE_DAYS: dict[str, int] = {
        # Original Day 10 gates
        "security_posture": 8,
        "eval_regression": 8,
        "budget": 9,
        "refusal_safety": 7,
        "resume_safety": 5,
        "aca_health": 10,
        # New Days 11-14 gates
        "delegated_identity": 11,
        "private_network_static": 12,
        "private_network_posture": 12,
        "trace_correlation": 14,
        "data_residency": 14,
        "dlq_drain_health": 13,
        "mcp_contract_integrity": 13,
        "obo_app_identity": 11,
        "obo_exchange": 11,
        "actor_binding": 11,
        "canary_regression": 14,
    }

    def generate(self, gate_results: list[dict[str, Any]]) -> CtoReport:
        """Build a CTO report from a list of gate result dicts.

        Each dict must have: ``name`` (str), ``passed`` (bool), ``detail`` (str).
        """
        summaries = [
            GateSummary(
                name=g["name"],
                passed=g["passed"],
                detail=g.get("detail", ""),
                day=self._GATE_DAYS.get(g["name"], 0),
            )
            for g in gate_results
        ]
        passed = [g for g in summaries if g.passed]
        failed = [g for g in summaries if not g.passed]

        # Load drilling metrics if available
        drills_passed = 0
        drills_total = 10
        drills_path = _ROOT / "build" / "day14" / "breaking_changes_drills.json"
        if drills_path.exists():
            try:
                drills_data = json.loads(drills_path.read_text())
                drills_passed = int(drills_data.get("passed", 0))
                drills_total = int(drills_data.get("total", 10))
            except Exception:
                pass

        # Gather operational metrics from existing day artifacts
        ops_metrics = self._collect_ops_metrics()

        return CtoReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            programme_days=14,
            gates_total=len(summaries),
            gates_passed=len(passed),
            gates_failed=len(failed),
            operational_metrics=ops_metrics,
            gate_details=summaries,
            breaking_changes_drills_passed=drills_passed,
            breaking_changes_drills_total=drills_total,
        )

    def _collect_ops_metrics(self) -> dict[str, Any]:
        metrics: dict[str, Any] = {}
        # Cost metric from Day 9
        budget_path = _ROOT / "build" / "day9" / "routing_report.json"
        if budget_path.exists():
            try:
                data = json.loads(budget_path.read_text())
                metrics["cost_per_invoice_gbp"] = data.get(
                    "avg_cost_per_invoice")
            except Exception:
                pass
        # Eval regression from Day 8
        regression_path = _ROOT / "build" / "day8" / "regression_baseline.json"
        if regression_path.exists():
            try:
                data = json.loads(regression_path.read_text())
                metrics["eval_baseline_accuracy"] = data.get("accuracy")
            except Exception:
                pass
        # Network posture from Day 12
        posture_path = _ROOT / "build" / "day12" / "private_network_posture.json"
        if posture_path.exists():
            try:
                data = json.loads(posture_path.read_text())
                metrics["private_network_all_passed"] = data.get("all_passed")
            except Exception:
                pass
        return metrics

    def write_artifact(self, report: CtoReport) -> Path:
        out_dir = _ROOT / "build" / "day14"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "cto_trace_report.json"
        out_path.write_text(json.dumps(report.to_dict(), indent=2))
        return out_path
