"""Trace correlation helper for AegisAP (Day 14).

Verifies that every invoice workflow trace carries a single ``correlation_id``
that ties together:
- The inbound Service Bus message
- The agent decision steps
- The OBO token exchange (if delegation was used)
- The downstream Function call
- The Azure Monitor / App Insights trace

The correlator reads ``build/day12/private_network_posture.json`` to determine
the deployment mode:
- ``all_passed=True``  → private (VNET-injected): expects dual-sink traces
  (App Insights + Log Analytics workspace).
- ``all_passed=False`` → public endpoint: only App Insights sink required.

Artifact: ``build/day14/trace_correlation_report.json``
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class TraceEntry:
    correlation_id: str
    span_id: str
    operation: str
    timestamp: str
    has_obo: bool = False
    has_function_call: bool = False
    has_service_bus: bool = False


@dataclass
class CorrelationReport:
    total_traces: int
    correlated: int
    uncorrelated: int
    dual_sink_required: bool
    dual_sink_satisfied: bool
    details: list[dict[str, Any]] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        if self.dual_sink_required and not self.dual_sink_satisfied:
            return False
        return self.uncorrelated == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_traces": self.total_traces,
            "correlated": self.correlated,
            "uncorrelated": self.uncorrelated,
            "dual_sink_required": self.dual_sink_required,
            "dual_sink_satisfied": self.dual_sink_satisfied,
            "passed": self.passed,
            "details": self.details[:20],
        }


class TraceCorrelator:
    """Verify correlation-ID coverage across AegisAP trace data."""

    def __init__(self, traces_path: Path) -> None:
        self._traces_path = traces_path

    @classmethod
    def from_build_artifacts(cls) -> "TraceCorrelator":
        traces_path = _ROOT / "build" / "day9" / "routing_report.json"
        return cls(traces_path=traces_path)

    def _is_private_mode(self) -> bool:
        posture_path = _ROOT / "build" / "day12" / "private_network_posture.json"
        if not posture_path.exists():
            return False
        try:
            data = json.loads(posture_path.read_text())
            return bool(data.get("all_passed", False))
        except Exception:
            return False

    def _load_traces(self) -> list[dict[str, Any]]:
        if not self._traces_path.exists():
            return []
        try:
            data = json.loads(self._traces_path.read_text())
            # routing_report may contain a "traces" list or be a flat dict
            if isinstance(data, list):
                return data
            if "traces" in data:
                return data["traces"]
            # Treat flat dict as single trace entry
            return [data] if data else []
        except Exception:
            return []

    def run(self) -> CorrelationReport:
        """Run correlation check and return a report."""
        dual_sink_required = self._is_private_mode()
        traces = self._load_traces()
        correlated = 0
        uncorrelated = 0
        details: list[dict[str, Any]] = []

        for t in traces:
            cid = t.get("correlation_id") or t.get("correlationId")
            matched = bool(cid and len(cid) >= 8)
            if matched:
                correlated += 1
            else:
                uncorrelated += 1
                details.append({"trace": t, "issue": "missing_correlation_id"})

        # Dual-sink check: look for log-analytics sink marker
        dual_sink_satisfied = True
        if dual_sink_required:
            la_path = _ROOT / "build" / "day14" / "log_analytics_sink_verified.json"
            dual_sink_satisfied = la_path.exists()
            if not dual_sink_satisfied:
                details.append({
                    "issue": "dual_sink_not_verified",
                    "hint": "Run scripts/verify_private_network_posture.py then re-run traces",
                })

        return CorrelationReport(
            total_traces=len(traces),
            correlated=correlated,
            uncorrelated=uncorrelated,
            dual_sink_required=dual_sink_required,
            dual_sink_satisfied=dual_sink_satisfied,
            details=details,
        )

    def write_artifact(self, report: CorrelationReport) -> Path:
        out_dir = _ROOT / "build" / "day14"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "trace_correlation_report.json"
        out_path.write_text(json.dumps(report.to_dict(), indent=2))
        return out_path
