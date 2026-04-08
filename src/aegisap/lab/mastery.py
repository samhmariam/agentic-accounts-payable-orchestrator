from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .curriculum import (
    PHASE1_GATE_MODES,
    constraint_lineage_for_day,
    get_day,
    load_manifest,
    normalize_day,
    resolve_repo_root,
)


PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"


@dataclass(frozen=True, slots=True)
class GateResult:
    gate_id: str
    mode: str
    status: str
    command: str
    detail: str
    success_marker: str | None = None


def _parse_payload(output: str) -> dict[str, Any] | None:
    text = output.strip()
    if not text.startswith("{") or not text.endswith("}"):
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _classify_success(command_output: str, success_marker: str | None) -> tuple[str, str]:
    payload = _parse_payload(command_output)
    if payload is not None and (
        payload.get("training_artifact") is True
        or payload.get("authoritative_evidence") is False
        or payload.get("status") == "preview"
    ):
        return SKIP, payload.get("note") or "Command completed in preview mode."
    if "[SKIP]" in command_output:
        return SKIP, "Command reported a preview-only or skipped verification."
    if success_marker and success_marker not in command_output:
        return FAIL, f"Missing success marker `{success_marker}`."
    return PASS, success_marker or "Command completed successfully."


def _run_gate(
    *,
    gate_id: str,
    mode: str,
    command: str,
    success_marker: str | None,
    repo_root: Path,
) -> GateResult:
    completed = subprocess.run(
        ["/bin/bash", "-lc", command],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    combined_output = "\n".join(
        part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
    )
    if completed.returncode != 0:
        detail = combined_output or "Command failed."
        return GateResult(gate_id=gate_id, mode=mode, status=FAIL, command=command, detail=detail, success_marker=success_marker)

    status, detail = _classify_success(combined_output, success_marker)
    return GateResult(
        gate_id=gate_id,
        mode=mode,
        status=status,
        command=command,
        detail=detail,
        success_marker=success_marker,
    )


def _day0_gates(track: str) -> list[dict[str, str]]:
    return [
        {
            "id": f"bootstrap_env_{track}",
            "mode": PHASE1_GATE_MODES["00"],
            "command": f"uv run python scripts/verify_env.py --track {track}",
            "success_marker": "[PASS] FDE Environment Validated",
        }
    ]


def run_mastery(
    *,
    day: str | int,
    strict: bool = False,
    repo_root: str | Path | None = None,
    track: str = "core",
) -> dict[str, Any]:
    root = resolve_repo_root(repo_root)
    day_id = normalize_day(day)
    lineage_path: str | None = None
    if day_id == "00":
        gates = _day0_gates(track)
        title = f"Bootstrap {track.title()} Environment"
        lineage = {"day": day_id, "title": title, "active_constraints": []}
    else:
        manifest = load_manifest(root)
        day_entry = get_day(manifest, day_id)
        gates = day_entry.get("mastery_gates", [])
        title = day_entry.get("title", f"Day {day_id}")
        lineage = constraint_lineage_for_day(manifest, day_id)
        target = root / "build" / f"day{day_id}" / "constraint_lineage.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(lineage, indent=2, sort_keys=True), encoding="utf-8")
        lineage_path = str(target)

    results = [
        _run_gate(
            gate_id=gate["id"],
            mode=gate["mode"],
            command=gate["command"],
            success_marker=gate.get("success_marker"),
            repo_root=root,
        )
        for gate in gates
    ]

    blocking_failures = [
        result for result in results if result.mode == "blocking" and result.status == FAIL
    ]
    strict_failures = [result for result in results if result.status in {FAIL, SKIP}]
    overall_ok = not blocking_failures and (not strict or not strict_failures)
    return {
        "day": day_id,
        "title": title,
        "strict": strict,
        "overall_ok": overall_ok,
        "constraint_lineage_path": lineage_path,
        "constraint_lineage": lineage,
        "results": [
            {
                "gate_id": result.gate_id,
                "mode": result.mode,
                "status": result.status,
                "command": result.command,
                "detail": result.detail,
                "success_marker": result.success_marker,
            }
            for result in results
        ],
    }
