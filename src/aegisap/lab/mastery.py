from __future__ import annotations

import json
import re
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

_NATIVE_COMMAND_KEYS = ("command", "purpose", "expected_signal", "observed_excerpt")
_NATIVE_QUERY_KEYS = ("query", "purpose", "expected_signal", "observed_excerpt")
_KQL_QUERY_KEYS = (
    "query",
    "workspace",
    "purpose",
    "observed_excerpt",
    "operator_interpretation",
)


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


def _validate_native_rows(
    *, entries: Any, keys: tuple[str, ...], label: str, minimum: int
) -> list[str]:
    errors: list[str] = []
    if not isinstance(entries, list):
        return [f"`{label}` must be a list."]
    if len(entries) < minimum:
        errors.append(f"`{label}` must contain at least {minimum} entr{'y' if minimum == 1 else 'ies'}.")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"`{label}[{index}]` must be an object.")
            continue
        missing = [key for key in keys if not str(entry.get(key, "")).strip()]
        if missing:
            errors.append(
                f"`{label}[{index}]` is missing required field(s): {', '.join(missing)}."
            )
    return errors


def _matches_any_pattern(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _is_azure_cli_command(command: str) -> bool:
    return command.lstrip().startswith("az ")


def _uses_json_output(command: str) -> bool:
    command_normalized = " ".join(command.split())
    return " -o json" in f" {command_normalized}" or "--output json" in command_normalized


def _validate_signal_families(
    *,
    commands: list[dict[str, Any]],
    contract: dict[str, Any],
) -> tuple[set[int], list[str]]:
    errors: list[str] = []
    qualifying_indexes: set[int] = set()
    families = contract.get("required_signal_families") or []
    top_level_json_required = bool(contract.get("must_use_json_output"))

    for index, entry in enumerate(commands):
        command = str(entry.get("command", "")).strip()
        if top_level_json_required and _is_azure_cli_command(command) and not _uses_json_output(command):
            errors.append(
                f"`commands[{index}].command` must append `-o json` or `--output json` for machine-readable grading."
            )

    for family in families:
        family_matches: set[int] = set()
        family_json_required = bool(family.get("must_use_json_output"))
        command_patterns = family.get("command_patterns") or []
        output_patterns = family.get("output_patterns") or []
        for index, entry in enumerate(commands):
            command = str(entry.get("command", "")).strip()
            observed_excerpt = str(entry.get("observed_excerpt", "")).strip()
            if not command or not observed_excerpt:
                continue
            if (top_level_json_required or family_json_required) and _is_azure_cli_command(command) and not _uses_json_output(command):
                continue
            if _matches_any_pattern(command, command_patterns) and _matches_any_pattern(observed_excerpt, output_patterns):
                family_matches.add(index)
        qualifying_indexes.update(family_matches)
        minimum_matches = int(family.get("minimum_matches", 1))
        if len(family_matches) < minimum_matches:
            errors.append(
                f"Signal family `{family.get('name', 'unnamed')}` matched {len(family_matches)} command(s); expected at least {minimum_matches}."
            )
    return qualifying_indexes, errors


def _validate_native_operator_evidence(
    *,
    day_id: str,
    contract: dict[str, Any],
    repo_root: Path,
) -> GateResult:
    rel_path = contract["artifact_path"]
    path = repo_root / rel_path
    gate_id = f"day{day_id}_native_operator_evidence"
    if not path.exists():
        return GateResult(
            gate_id=gate_id,
            mode=contract["mode"],
            status=FAIL,
            command=f"validate {rel_path}",
            detail=f"Missing native operator evidence artifact `{rel_path}`.",
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GateResult(
            gate_id=gate_id,
            mode=contract["mode"],
            status=FAIL,
            command=f"validate {rel_path}",
            detail=f"Could not parse `{rel_path}` as JSON: {exc}",
        )

    errors: list[str] = []
    if payload.get("day") != day_id:
        errors.append(f"`day` must equal `{day_id}`.")
    if not str(payload.get("operator_interpretation", "")).strip():
        errors.append("`operator_interpretation` must be non-empty.")

    limitations = payload.get("limitations")
    if isinstance(limitations, str):
        if not limitations.strip():
            errors.append("`limitations` must be non-empty.")
    elif isinstance(limitations, list):
        if not limitations or not all(str(item).strip() for item in limitations):
            errors.append("`limitations` must contain at least one non-empty item.")
    else:
        errors.append("`limitations` must be a string or a list of strings.")

    errors.extend(
        _validate_native_rows(
            entries=payload.get("commands"),
            keys=_NATIVE_COMMAND_KEYS,
            label="commands",
            minimum=0,
        )
    )
    errors.extend(
        _validate_native_rows(
            entries=payload.get("queries"),
            keys=_NATIVE_QUERY_KEYS,
            label="queries",
            minimum=int(contract.get("minimum_queries", 0)),
        )
    )

    commands = payload.get("commands")
    if isinstance(commands, list):
        qualifying_indexes, family_errors = _validate_signal_families(
            commands=[entry for entry in commands if isinstance(entry, dict)],
            contract=contract,
        )
        errors.extend(family_errors)
        minimum_commands = int(contract.get("minimum_commands", 0))
        if contract.get("required_signal_families"):
            if len(qualifying_indexes) < minimum_commands:
                errors.append(
                    "Only commands matching the required signal families count toward the minimum command threshold."
                )
        elif len(commands) < minimum_commands:
            errors.append(
                f"`commands` must contain at least {minimum_commands} entr{'y' if minimum_commands == 1 else 'ies'}."
            )

    live_demo = payload.get("live_demo")
    if not isinstance(live_demo, dict):
        errors.append("`live_demo` must be an object.")
    else:
        if live_demo.get("required") != bool(contract.get("live_demo_required")):
            errors.append("`live_demo.required` does not match the manifest contract.")
        if live_demo.get("review_stage") != contract.get("review_stage"):
            errors.append("`live_demo.review_stage` does not match the manifest contract.")
        if contract.get("live_demo_required"):
            if live_demo.get("passed") is not True:
                errors.append("`live_demo.passed` must be `true` for blocking native evidence.")
            if not str(live_demo.get("witnessed_by", "")).strip():
                errors.append("`live_demo.witnessed_by` must be recorded for blocking native evidence.")
            if not str(live_demo.get("recorded_at", "")).strip():
                errors.append("`live_demo.recorded_at` must be recorded for blocking native evidence.")

    if errors:
        return GateResult(
            gate_id=gate_id,
            mode=contract["mode"],
            status=FAIL,
            command=f"validate {rel_path}",
            detail="; ".join(errors),
        )

    return GateResult(
        gate_id=gate_id,
        mode=contract["mode"],
        status=PASS,
        command=f"validate {rel_path}",
        detail=f"Native operator evidence validated from `{rel_path}`.",
    )


def validate_native_operator_evidence_artifact(
    *,
    day_id: str,
    contract: dict[str, Any],
    repo_root: Path,
) -> GateResult:
    return _validate_native_operator_evidence(day_id=day_id, contract=contract, repo_root=repo_root)


def _validate_rollback_rehearsal(
    *,
    day_id: str,
    contract: dict[str, Any],
    repo_root: Path,
) -> GateResult:
    rel_path = contract["artifact_path"]
    path = repo_root / rel_path
    gate_id = f"day{day_id}_rollback_rehearsal"
    if not path.exists():
        return GateResult(
            gate_id=gate_id,
            mode="blocking",
            status=FAIL,
            command=f"validate {rel_path}",
            detail=f"Missing rollback rehearsal artifact `{rel_path}`.",
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GateResult(
            gate_id=gate_id,
            mode="blocking",
            status=FAIL,
            command=f"validate {rel_path}",
            detail=f"Could not parse `{rel_path}` as JSON: {exc}",
        )

    errors: list[str] = []
    if payload.get("day") != day_id:
        errors.append(f"`day` must equal `{day_id}`.")
    if contract.get("traffic_shift_required") and payload.get("traffic_restored_before_git") is not True:
        errors.append("`traffic_restored_before_git` must be `true` before rollback proof passes.")
    if not str(payload.get("stable_revision", "")).strip():
        errors.append("`stable_revision` must be recorded.")
    if not str(payload.get("failing_revision", "")).strip():
        errors.append("`failing_revision` must be recorded.")

    traffic_shift = payload.get("traffic_shift")
    if not isinstance(traffic_shift, dict):
        errors.append("`traffic_shift` must be an object.")
    else:
        command = str(traffic_shift.get("command", "")).strip()
        verification_command = str(traffic_shift.get("verification_command", "")).strip()
        combined_excerpt = " ".join(
            [
                str(traffic_shift.get("observed_excerpt", "")).strip(),
                str(traffic_shift.get("verification_excerpt", "")).strip(),
            ]
        ).strip()
        if not command:
            errors.append("`traffic_shift.command` must be non-empty.")
        if not verification_command:
            errors.append("`traffic_shift.verification_command` must be non-empty.")
        if _is_azure_cli_command(command) and not _uses_json_output(command):
            errors.append("`traffic_shift.command` must use `-o json` or `--output json`.")
        if _is_azure_cli_command(verification_command) and not _uses_json_output(verification_command):
            errors.append("`traffic_shift.verification_command` must use `-o json` or `--output json`.")
        if command and not _matches_any_pattern(command, contract.get("command_patterns", [])):
            errors.append("`traffic_shift.command` does not match the required rollback traffic-shift command family.")
        for pattern in contract.get("verification_patterns", []):
            if not re.search(pattern, combined_excerpt, flags=re.IGNORECASE):
                errors.append(f"Rollback verification output is missing required pattern `{pattern}`.")

    readiness_retry_policy = payload.get("readiness_retry_policy")
    expected_retry_policy = contract.get("readiness_retry_policy", {})
    if not isinstance(readiness_retry_policy, dict):
        errors.append("`readiness_retry_policy` must be an object.")
    else:
        for key, expected_value in expected_retry_policy.items():
            if readiness_retry_policy.get(key) != expected_value:
                errors.append(f"`readiness_retry_policy.{key}` must equal `{expected_value}`.")

    health_checks = payload.get("health_checks")
    if not isinstance(health_checks, list):
        errors.append("`health_checks` must be a list.")
    else:
        names = {str(item.get("name", "")).strip() for item in health_checks if isinstance(item, dict)}
        for required_name in contract.get("health_checks", []):
            if required_name not in names:
                errors.append(f"Missing required rollback health check `{required_name}`.")
        for index, check in enumerate(health_checks):
            if not isinstance(check, dict):
                errors.append(f"`health_checks[{index}]` must be an object.")
                continue
            if not str(check.get("command", "")).strip():
                errors.append(f"`health_checks[{index}].command` must be non-empty.")
            if check.get("passed") is not True:
                errors.append(f"`health_checks[{index}].passed` must be `true`.")
            if int(check.get("attempts", 0)) < 1:
                errors.append(f"`health_checks[{index}].attempts` must be at least 1.")
            if not str(check.get("observed_excerpt", "")).strip():
                errors.append(f"`health_checks[{index}].observed_excerpt` must be non-empty.")

    if errors:
        return GateResult(
            gate_id=gate_id,
            mode="blocking",
            status=FAIL,
            command=f"validate {rel_path}",
            detail="; ".join(errors),
        )

    return GateResult(
        gate_id=gate_id,
        mode="blocking",
        status=PASS,
        command=f"validate {rel_path}",
        detail=f"Rollback rehearsal evidence validated from `{rel_path}`.",
    )


def validate_rollback_rehearsal_artifact(
    *,
    day_id: str,
    contract: dict[str, Any],
    repo_root: Path,
) -> GateResult:
    return _validate_rollback_rehearsal(day_id=day_id, contract=contract, repo_root=repo_root)


def _validate_kql_evidence(
    *,
    day_id: str,
    contract: dict[str, Any],
    repo_root: Path,
) -> GateResult:
    rel_path = contract["artifact_path"]
    path = repo_root / rel_path
    gate_id = f"day{day_id}_kql_evidence"
    mode = PHASE1_GATE_MODES.get(day_id, "blocking")
    if not path.exists():
        return GateResult(
            gate_id=gate_id,
            mode=mode,
            status=FAIL,
            command=f"validate {rel_path}",
            detail=f"Missing KQL evidence artifact `{rel_path}`.",
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GateResult(
            gate_id=gate_id,
            mode=mode,
            status=FAIL,
            command=f"validate {rel_path}",
            detail=f"Could not parse `{rel_path}` as JSON: {exc}",
        )

    errors: list[str] = []
    if payload.get("day") != day_id:
        errors.append(f"`day` must equal `{day_id}`.")
    queries = payload.get("queries")
    if not isinstance(queries, list):
        errors.append("`queries` must be a list.")
    else:
        minimum = int(contract.get("minimum_queries", 1))
        if len(queries) < minimum:
            errors.append(f"`queries` must contain at least {minimum} entr{'y' if minimum == 1 else 'ies'}.")
        for index, query in enumerate(queries):
            if not isinstance(query, dict):
                errors.append(f"`queries[{index}]` must be an object.")
                continue
            missing = [key for key in _KQL_QUERY_KEYS if not str(query.get(key, "")).strip()]
            if missing:
                errors.append(
                    f"`queries[{index}]` is missing required field(s): {', '.join(missing)}."
                )
            signal_found = query.get("signal_found")
            if not isinstance(signal_found, bool):
                errors.append(f"`queries[{index}].signal_found` must be a boolean.")

    if errors:
        return GateResult(
            gate_id=gate_id,
            mode=mode,
            status=FAIL,
            command=f"validate {rel_path}",
            detail="; ".join(errors),
        )

    return GateResult(
        gate_id=gate_id,
        mode=mode,
        status=PASS,
        command=f"validate {rel_path}",
        detail=f"KQL evidence validated from `{rel_path}`.",
    )


def validate_kql_evidence_artifact(
    *,
    day_id: str,
    contract: dict[str, Any],
    repo_root: Path,
) -> GateResult:
    return _validate_kql_evidence(day_id=day_id, contract=contract, repo_root=repo_root)


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
    kql_contract: dict[str, Any] | None = None
    rollback_contract: dict[str, Any] | None = None
    if day_id == "00":
        gates = _day0_gates(track)
        title = f"Bootstrap {track.title()} Environment"
        lineage = {"day": day_id, "title": title, "active_constraints": []}
        native_contract: dict[str, Any] | None = None
    else:
        manifest = load_manifest(root)
        day_entry = get_day(manifest, day_id)
        gates = day_entry.get("mastery_gates", [])
        title = day_entry.get("title", f"Day {day_id}")
        native_contract = day_entry.get("native_operator_evidence")
        kql_contract = day_entry.get("kql_evidence")
        rollback_contract = day_entry.get("rollback_rehearsal")
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
    if native_contract is not None:
        results.append(
            _validate_native_operator_evidence(
                day_id=day_id,
                contract=native_contract,
                repo_root=root,
            )
        )
    if day_id != "00" and kql_contract is not None:
        results.append(
            _validate_kql_evidence(
                day_id=day_id,
                contract=kql_contract,
                repo_root=root,
            )
        )
    if day_id != "00" and rollback_contract is not None:
        results.append(
            _validate_rollback_rehearsal(
                day_id=day_id,
                contract=rollback_contract,
                repo_root=root,
            )
        )

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
