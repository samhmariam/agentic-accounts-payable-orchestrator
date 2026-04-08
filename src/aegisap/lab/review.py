from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import AzureOpenAI


TECH_FILE_PREFIXES = ("src/", "infra/")
SCOPED_FILE_PREFIXES = ("src/", "infra/", "tests/", ".github/workflows/")
DEFAULT_STRATEGY_PATHS = (
    Path("build/review/principal_review_strategy.json"),
    Path("data/review/principal_review_strategy.json"),
)
RBAC_PATTERNS = (
    re.compile(r"^\+.*\b(Contributor|Owner|User Access Administrator)\b", re.MULTILINE),
    re.compile(r"^\+.*\bSearch Index Data Contributor\b", re.MULTILINE),
    re.compile(r"^\+.*\bsearchIndexDataContributorRoleDefinitionId\b", re.MULTILINE),
)
BUILTIN_EXAMPLES = [
    {
        "profile": "wave1-day01-trust-boundary",
        "diff_smell": "Fail-open trust-boundary repair with no artifact update.",
        "review": "Reject it. Deterministic intake repairs must keep the trust boundary explicit and refresh the written blast-radius evidence.",
    },
    {
        "profile": "wave1-day02-resilience",
        "diff_smell": "Touches retry or backpressure logic without proving 429 handling in tests.",
        "review": "You changed resilience semantics without the proof. Add the failing-and-then-passing tests before this can move.",
    },
    {
        "profile": "wave3-day07-guardrail-leak",
        "diff_smell": "Redaction or audit code changed without Day 7 governance artifacts.",
        "review": "The code may close the leak, but the review packet is incomplete. Update the guardrail evidence and refusal rationale.",
    },
    {
        "profile": "wave3-day08-identity-drift",
        "diff_smell": "Runtime identity uses Search Index Data Contributor for a read-only path.",
        "review": "Absolutely not. Over-privileged runtime identity. Revert to the narrow reader role and justify it with the release evidence.",
    },
    {
        "profile": "wave3-day09-routing-drift",
        "diff_smell": "Routing or cache changes land without Day 9 cost-governance evidence.",
        "review": "The routing patch is not enough on its own. Show the economic control story and the slice risk that drove the fix.",
    },
    {
        "profile": "wave3-day10-release-board",
        "diff_smell": "Release envelope or gate code changes without a matching CAB packet or tests.",
        "review": "No. Release logic needs both proof and governance. Update the Day 10 packet and the gate tests together.",
    },
    {
        "profile": "wave4-day11-actor-binding",
        "diff_smell": "Delegated identity repair changes actor verification without the Day 11 authority packet.",
        "review": "The identity change is not self-justifying. Prove the actor-binding boundary and update the threat model before approval.",
    },
    {
        "profile": "wave4-day12-network-isolation",
        "diff_smell": "Network or posture logic changed without the Day 12 isolation evidence.",
        "review": "A private-network fix needs both technical proof and exception hygiene. Refresh the Day 12 packet and show the checker catches the public path again.",
    },
    {
        "profile": "wave4-day13-boundary-contract",
        "diff_smell": "MCP or DLQ code changed without the Day 13 contract packet.",
        "review": "The integration boundary is still under-defined. Update the partner-facing contract and compensating-action evidence before this moves.",
    },
    {
        "profile": "wave4-day14-chaos-command",
        "diff_smell": "Elite-ops gate changes landed without the Day 14 incident packet or chaos evidence.",
        "review": "No. War-room logic needs rollback, trace, and chaos proof together. Rebuild the Day 14 packet before asking for approval.",
    },
]


@dataclass(frozen=True, slots=True)
class DayReviewRule:
    day_id: str
    evaluator_profile: str
    scope_markers: tuple[str, ...]
    signal_markers: tuple[str, ...]
    evidence_prefix: str
    missing_evidence_id: str
    missing_evidence_summary: str
    missing_evidence_detail: str
    missing_evidence_fix: str


DAY_RULES: dict[str, DayReviewRule] = {
    "01": DayReviewRule(
        day_id="01",
        evaluator_profile="wave1-day01-trust-boundary",
        scope_markers=(
            "src/aegisap/day_01/",
            "tests/test_day_01_",
        ),
        signal_markers=(
            "src/aegisap/day_01/",
            "tests/test_day_01_",
            "docs/curriculum/artifacts/day01/",
            "scenarios/day01/",
            "notebooks/day_1_agentic_fundamentals.py",
            "docs/DAY_01.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day01/",
        missing_evidence_id="missing_day01_evidence",
        missing_evidence_summary="Trust-boundary code changed without Day 1 evidence updates.",
        missing_evidence_detail="Day 1 fixes must still explain blast radius, deterministic rejection, and ownership of the trust boundary.",
        missing_evidence_fix="Update the Day 1 evidence artifacts before asking for approval.",
    ),
    "02": DayReviewRule(
        day_id="02",
        evaluator_profile="wave1-day02-resilience",
        scope_markers=(
            "src/aegisap/observability/retry_policy.py",
            "src/aegisap/resilience/",
            "tests/day2/",
            "tests/day8/test_retry_policy.py",
        ),
        signal_markers=(
            "src/aegisap/observability/retry_policy.py",
            "src/aegisap/resilience/",
            "tests/day2/",
            "tests/day8/test_retry_policy.py",
            "docs/curriculum/artifacts/day02/",
            "scenarios/day02/",
            "notebooks/day_2_requirements_architecture.py",
            "docs/DAY_02.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day02/",
        missing_evidence_id="missing_day02_evidence",
        missing_evidence_summary="Resilience code changed without Day 2 evidence updates.",
        missing_evidence_detail="Day 2 repairs must update the NFR or ADR artifacts that justify the fix under quota pressure.",
        missing_evidence_fix="Update the Day 2 evidence artifacts alongside the resilience repair.",
    ),
    "03": DayReviewRule(
        day_id="03",
        evaluator_profile="wave2-day03-retrieval-authority",
        scope_markers=("src/aegisap/day3/", "tests/day3/"),
        signal_markers=(
            "src/aegisap/day3/",
            "tests/day3/",
            "docs/curriculum/artifacts/day03/",
            "scenarios/day03/",
            "notebooks/day_3_azure_ai_services.py",
            "docs/DAY_03.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day03/",
        missing_evidence_id="missing_day03_evidence",
        missing_evidence_summary="Retrieval-authority code changed without Day 3 evidence updates.",
        missing_evidence_detail="Day 3 fixes must explain why authoritative evidence wins and how stale evidence is still exposed safely.",
        missing_evidence_fix="Update the Day 3 boundary and framework evidence artifacts with the repaired authority logic.",
    ),
    "04": DayReviewRule(
        day_id="04",
        evaluator_profile="wave2-day04-fail-open-planner",
        scope_markers=("src/aegisap/day4/", "tests/day4/"),
        signal_markers=(
            "src/aegisap/day4/",
            "tests/day4/",
            "docs/curriculum/artifacts/day04/",
            "scenarios/day04/",
            "notebooks/day_4_single_agent_loops.py",
            "docs/DAY_04.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day04/",
        missing_evidence_id="missing_day04_evidence",
        missing_evidence_summary="Planner or gate code changed without Day 4 control evidence updates.",
        missing_evidence_detail="Day 4 fixes must prove the planner still fails closed on risky slices.",
        missing_evidence_fix="Update the Day 4 risk register or policy-precedence evidence alongside the code change.",
    ),
    "05": DayReviewRule(
        day_id="05",
        evaluator_profile="wave2-day05-durable-state",
        scope_markers=("src/aegisap/day5/", "tests/day5/"),
        signal_markers=(
            "src/aegisap/day5/",
            "tests/day5/",
            "docs/curriculum/artifacts/day05/",
            "scenarios/day05/",
            "notebooks/day_5_multi_agent_orchestration.py",
            "docs/DAY_05.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day05/",
        missing_evidence_id="missing_day05_evidence",
        missing_evidence_summary="Durable-state code changed without Day 5 governance evidence updates.",
        missing_evidence_detail="Day 5 fixes must explain the pause and resume boundary and checkpoint binding contract in writing.",
        missing_evidence_fix="Update the Day 5 approval or pause-resume governance artifacts before approval.",
    ),
    "06": DayReviewRule(
        day_id="06",
        evaluator_profile="wave2-day06-review-boundary",
        scope_markers=("src/aegisap/day6/", "tests/day6/"),
        signal_markers=(
            "src/aegisap/day6/",
            "tests/day6/",
            "docs/curriculum/artifacts/day06/",
            "scenarios/day06/",
            "notebooks/day_6_data_ml_integration.py",
            "docs/DAY_06.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day06/",
        missing_evidence_id="missing_day06_evidence",
        missing_evidence_summary="Review-boundary code changed without Day 6 authority evidence updates.",
        missing_evidence_detail="Day 6 fixes must explain how injection, authority, and conflict handling combine into a safe refusal.",
        missing_evidence_fix="Update the Day 6 conflict runbook or authority chart with the repaired boundary.",
    ),
    "07": DayReviewRule(
        day_id="07",
        evaluator_profile="wave3-day07-guardrail-leak",
        scope_markers=(
            "src/aegisap/security/redaction.py",
            "src/aegisap/audit/",
            "tests/day7/",
        ),
        signal_markers=(
            "src/aegisap/security/redaction.py",
            "src/aegisap/audit/",
            "tests/day7/",
            "docs/curriculum/artifacts/day07/",
            "scenarios/day07/",
            "notebooks/day_7_testing_eval_guardrails.py",
            "docs/DAY_07.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day07/",
        missing_evidence_id="missing_day07_evidence",
        missing_evidence_summary="Guardrail or audit code changed without Day 7 evidence updates.",
        missing_evidence_detail="Day 7 fixes must refresh the eval-governance packet and explain how the refusal or redaction boundary now behaves.",
        missing_evidence_fix="Update the Day 7 governance artifacts before asking for release approval.",
    ),
    "08": DayReviewRule(
        day_id="08",
        evaluator_profile="wave3-day08-identity-drift",
        scope_markers=(
            "infra/modules/role_assignments.bicep",
            "infra/foundations/search_service.bicep",
            "src/aegisap/security/policy.py",
            "tests/day8/",
            "tests/day7/security/test_search_token_auth_only.py",
        ),
        signal_markers=(
            "infra/modules/role_assignments.bicep",
            "infra/foundations/search_service.bicep",
            "src/aegisap/security/policy.py",
            "tests/day8/",
            "tests/day7/security/test_search_token_auth_only.py",
            "docs/curriculum/artifacts/day08/",
            "scenarios/day08/",
            "notebooks/day_8_cicd_iac_deployment.py",
            "docs/DAY_08.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day08/",
        missing_evidence_id="missing_day08_evidence",
        missing_evidence_summary="Identity or IaC changes landed without Day 8 evidence updates.",
        missing_evidence_detail="Day 8 fixes must update the security review packet and the named ownership path for the repair.",
        missing_evidence_fix="Refresh the Day 8 review packet and release ownership artifacts before approval.",
    ),
    "09": DayReviewRule(
        day_id="09",
        evaluator_profile="wave3-day09-routing-drift",
        scope_markers=(
            "src/aegisap/routing/",
            "src/aegisap/cache/",
            "src/aegisap/cost/",
            "tests/day9/",
        ),
        signal_markers=(
            "src/aegisap/routing/",
            "src/aegisap/cache/",
            "src/aegisap/cost/",
            "tests/day9/",
            "docs/curriculum/artifacts/day09/",
            "scenarios/day09/",
            "notebooks/day_9_scaling_monitoring_cost.py",
            "docs/DAY_09.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day09/",
        missing_evidence_id="missing_day09_evidence",
        missing_evidence_summary="Routing or cost-control code changed without Day 9 evidence updates.",
        missing_evidence_detail="Day 9 fixes must explain the economic control story and the risky slice that forced the routing repair.",
        missing_evidence_fix="Update the Day 9 routing and cost-governance artifacts before approval.",
    ),
    "10": DayReviewRule(
        day_id="10",
        evaluator_profile="wave3-day10-release-board",
        scope_markers=(
            "src/aegisap/deploy/",
            "src/aegisap/api/release.py",
            "src/aegisap/training/checkpoints.py",
            "tests/day10/",
            "tests/training/test_checkpoints.py",
            "tests/api/test_app.py",
        ),
        signal_markers=(
            "src/aegisap/deploy/",
            "src/aegisap/api/release.py",
            "src/aegisap/training/checkpoints.py",
            "tests/day10/",
            "tests/training/test_checkpoints.py",
            "tests/api/test_app.py",
            "docs/curriculum/artifacts/day10/",
            "scenarios/day10/",
            "notebooks/day_10_production_operations.py",
            "docs/DAY_10.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day10/",
        missing_evidence_id="missing_day10_evidence",
        missing_evidence_summary="Release-gate code changed without Day 10 evidence updates.",
        missing_evidence_detail="Day 10 fixes must update the CAB packet or executive release brief together with the gate logic and tests.",
        missing_evidence_fix="Refresh the Day 10 evidence packet before approval.",
    ),
    "11": DayReviewRule(
        day_id="11",
        evaluator_profile="wave4-day11-actor-binding",
        scope_markers=(
            "src/aegisap/identity/",
            "scripts/verify_delegated_identity_contract.py",
            "tests/day11/",
        ),
        signal_markers=(
            "src/aegisap/identity/",
            "scripts/verify_delegated_identity_contract.py",
            "tests/day11/",
            "docs/curriculum/artifacts/day11/",
            "scenarios/day11/",
            "notebooks/day_11_delegated_identity_obo.py",
            "docs/DAY_11.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day11/",
        missing_evidence_id="missing_day11_evidence",
        missing_evidence_summary="Delegated-identity code changed without Day 11 evidence updates.",
        missing_evidence_detail="Day 11 repairs must update the approval-authority model and threat packet alongside the actor-binding fix.",
        missing_evidence_fix="Refresh the Day 11 authority and exception artifacts before approval.",
    ),
    "12": DayReviewRule(
        day_id="12",
        evaluator_profile="wave4-day12-network-isolation",
        scope_markers=(
            "src/aegisap/network/",
            "scripts/check_private_network_static.py",
            "scripts/verify_private_network_posture.py",
            "tests/day12/",
        ),
        signal_markers=(
            "src/aegisap/network/",
            "scripts/check_private_network_static.py",
            "scripts/verify_private_network_posture.py",
            "tests/day12/",
            "docs/curriculum/artifacts/day12/",
            "scenarios/day12/",
            "notebooks/day_12_private_networking_constraints.py",
            "docs/DAY_12.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day12/",
        missing_evidence_id="missing_day12_evidence",
        missing_evidence_summary="Network-isolation code changed without Day 12 evidence updates.",
        missing_evidence_detail="Day 12 fixes must update the network dependency and exception packet together with the repair.",
        missing_evidence_fix="Refresh the Day 12 network evidence before approval.",
    ),
    "13": DayReviewRule(
        day_id="13",
        evaluator_profile="wave4-day13-boundary-contract",
        scope_markers=(
            "src/aegisap/integration/",
            "src/aegisap/mcp/",
            "scripts/verify_mcp_contract_integrity.py",
            "scripts/verify_webhook_reliability.py",
            "tests/day13/",
        ),
        signal_markers=(
            "src/aegisap/integration/",
            "src/aegisap/mcp/",
            "scripts/verify_mcp_contract_integrity.py",
            "scripts/verify_webhook_reliability.py",
            "tests/day13/",
            "docs/curriculum/artifacts/day13/",
            "scenarios/day13/",
            "notebooks/day_13_integration_boundary_and_mcp.py",
            "docs/DAY_13.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day13/",
        missing_evidence_id="missing_day13_evidence",
        missing_evidence_summary="Integration-boundary code changed without Day 13 evidence updates.",
        missing_evidence_detail="Day 13 fixes must update the contract, compensating-action, and partner-communication packet with the repair.",
        missing_evidence_fix="Refresh the Day 13 boundary evidence before approval.",
    ),
    "14": DayReviewRule(
        day_id="14",
        evaluator_profile="wave4-day14-chaos-command",
        scope_markers=(
            "src/aegisap/deploy/gates_v2.py",
            "src/aegisap/traceability/",
            "src/aegisap/training/chaos.py",
            "scripts/verify_canary_regression.py",
            "scripts/verify_trace_correlation.py",
            "scripts/run_chaos_capstone.py",
            "scripts/generate_cto_trace_report.py",
            "tests/day14/",
        ),
        signal_markers=(
            "src/aegisap/deploy/gates_v2.py",
            "src/aegisap/traceability/",
            "src/aegisap/training/chaos.py",
            "scripts/verify_canary_regression.py",
            "scripts/verify_trace_correlation.py",
            "scripts/run_chaos_capstone.py",
            "scripts/generate_cto_trace_report.py",
            "tests/day14/",
            "docs/curriculum/artifacts/day14/",
            "scenarios/day14/",
            "notebooks/day_14_breaking_changes_elite_ops.py",
            "docs/DAY_14.md",
        ),
        evidence_prefix="docs/curriculum/artifacts/day14/",
        missing_evidence_id="missing_day14_evidence",
        missing_evidence_summary="Elite-ops code changed without Day 14 evidence updates.",
        missing_evidence_detail="Day 14 fixes must update the incident-command packet and chaos outputs together with the gate change.",
        missing_evidence_fix="Refresh the Day 14 incident and chaos evidence before approval.",
    ),
}


@dataclass(slots=True)
class ReviewFinding:
    finding_id: str
    severity: str
    summary: str
    detail: str
    suggested_fix: str


def current_time() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_diff(*, repo_root: Path, base_ref: str, head_ref: str) -> tuple[str, list[str]]:
    diff = subprocess.run(
        ["git", "diff", "--no-color", "--unified=0", f"{base_ref}...{head_ref}"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    changed_files = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    return diff, changed_files


def _matches_marker(path: str, marker: str) -> bool:
    return path == marker or path.startswith(marker)


def _matches_any(path: str, markers: tuple[str, ...]) -> bool:
    return any(_matches_marker(path, marker) for marker in markers)


def detect_scope_days(*, changed_files: list[str]) -> list[str]:
    matched = [
        day_id
        for day_id, rule in DAY_RULES.items()
        if any(_matches_any(path, rule.scope_markers) for path in changed_files)
    ]
    return matched


def detect_profiles(*, changed_files: list[str]) -> list[str]:
    matched = [
        rule.evaluator_profile
        for rule in DAY_RULES.values()
        if any(_matches_any(path, rule.signal_markers) for path in changed_files)
    ]
    return matched or [DAY_RULES[day_id].evaluator_profile for day_id in detect_scope_days(changed_files=changed_files)]


def load_review_strategy(*, repo_root: Path, strategy_path: str | Path | None = None) -> dict[str, Any]:
    candidate_paths: list[Path] = []
    if strategy_path:
        path = Path(strategy_path)
        candidate_paths.append(path if path.is_absolute() else repo_root / path)
    candidate_paths.extend(repo_root / path for path in DEFAULT_STRATEGY_PATHS)

    for path in candidate_paths:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payload.setdefault("strategy_path", str(path))
            return payload

    return {
        "compiler": "builtin",
        "llm_blocking_enabled": False,
        "profiles": {},
        "examples": BUILTIN_EXAMPLES,
        "strategy_path": "",
    }


def _strategy_examples(*, strategy: dict[str, Any], profiles: list[str]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    selected: list[dict[str, str]] = []

    profile_map = strategy.get("profiles", {})
    if isinstance(profile_map, dict):
        for profile in profiles:
            payload = profile_map.get(profile, {})
            examples = payload.get("examples", []) if isinstance(payload, dict) else []
            for example in examples:
                key = (str(example.get("profile", profile)), str(example.get("diff_smell", "")))
                if key in seen:
                    continue
                seen.add(key)
                selected.append(example)

    for example in strategy.get("examples", []) or BUILTIN_EXAMPLES:
        key = (str(example.get("profile", "")), str(example.get("diff_smell", "")))
        if key in seen:
            continue
        seen.add(key)
        selected.append(example)
    return selected[:8]


def deterministic_findings(*, changed_files: list[str], diff_text: str) -> list[ReviewFinding]:
    findings: list[ReviewFinding] = []
    changed_set = set(changed_files)

    if any(pattern.search(diff_text) for pattern in RBAC_PATTERNS):
        findings.append(
            ReviewFinding(
                finding_id="over_privileged_rbac",
                severity="blocking",
                summary="Over-privileged RBAC role detected in the diff.",
                detail="Training PRs must use the narrowest day-specific role. Broad or contributor-level runtime access is not accepted.",
                suggested_fix="Replace the broad role with the least-privilege role required for the scenario and defend it in the evidence packet.",
            )
        )

    changed_tests = [path for path in changed_files if path.startswith("tests/")]
    if any(path.startswith(prefix) for prefix in TECH_FILE_PREFIXES for path in changed_files) and not changed_tests:
        findings.append(
            ReviewFinding(
                finding_id="missing_tests",
                severity="blocking",
                summary="Technical changes landed without accompanying test edits.",
                detail="Incident repairs must include the automated proof that the failure reproduced and is now fixed.",
                suggested_fix="Add or update the relevant tests before asking for review.",
            )
        )

    scope_days = detect_scope_days(changed_files=changed_files)
    if {"04", "05"} & set(scope_days):
        required_pushback_artifacts = {
            "adr/ADR-002_irreversible_actions_and_hitl.md",
            "docs/curriculum/artifacts/day04/SPONSOR_PUSHBACK_EMAIL.md",
        }
        missing_pushback = sorted(required_pushback_artifacts - changed_set)
        if missing_pushback:
            findings.append(
                ReviewFinding(
                    finding_id="missing_day04_pushback_artifacts",
                    severity="blocking",
                    summary="Irreversible-action or HITL changes landed without the required Day 4 pushback artifacts.",
                    detail=(
                        "Day 4 and Day 5 repairs must preserve the executive refusal trail and the internal ADR for "
                        "irreversible actions. Missing artifacts: " + ", ".join(missing_pushback)
                    ),
                    suggested_fix=(
                        "Update both `adr/ADR-002_irreversible_actions_and_hitl.md` and "
                        "`docs/curriculum/artifacts/day04/SPONSOR_PUSHBACK_EMAIL.md` before asking for approval."
                    ),
                )
            )
    if "10" in scope_days and "docs/curriculum/artifacts/day10/REVERT_PROOF.md" not in changed_set:
        findings.append(
            ReviewFinding(
                finding_id="missing_day10_revert_proof",
                severity="blocking",
                summary="Day 10 release changes landed without Revert Proof.",
                detail="Release-board changes must update the explicit Revert Proof artifact with the rollback mechanism, last-known-good target, and recovery time box.",
                suggested_fix="Update `docs/curriculum/artifacts/day10/REVERT_PROOF.md` before asking for CAB approval.",
            )
        )
    if "14" in scope_days and "docs/curriculum/artifacts/day14/REVERT_PROOF.md" not in changed_set:
        findings.append(
            ReviewFinding(
                finding_id="missing_day14_revert_proof",
                severity="blocking",
                summary="Day 14 incident-command changes landed without Revert Proof.",
                detail="Elite-ops changes must update the explicit Revert Proof artifact with the rollback mechanism, last-known-good target, and recovery time box.",
                suggested_fix="Update `docs/curriculum/artifacts/day14/REVERT_PROOF.md` before asking for capstone CAB approval.",
            )
        )
    if len(scope_days) > 1:
        findings.append(
            ReviewFinding(
                finding_id="cross_day_scope_drift",
                severity="blocking",
                summary="The PR spans multiple day ownership zones.",
                detail="Learner incident PRs should stay inside a single day's repair surface plus its tests and evidence.",
                suggested_fix="Split the work so one PR repairs one day's incident and evidence packet.",
            )
        )

    if any(path.startswith(".github/workflows/") for path in changed_files) or (
        any(path.startswith("infra/") for path in changed_files) and not ({"08", "12"} & set(scope_days))
    ):
        findings.append(
            ReviewFinding(
                finding_id="wave1_wrong_file_scope",
                severity="blocking",
                summary="The PR touches infrastructure or workflow files outside the expected repair surface.",
                detail="Learner incident PRs should stay inside the scoped production code, tests, and evidence for the active day unless the incident explicitly requires infrastructure ownership.",
                suggested_fix="Remove the unrelated infra or workflow changes, or move them into the day that actually owns them.",
            )
        )

    for day_id in scope_days:
        rule = DAY_RULES[day_id]
        if not any(path.startswith(rule.evidence_prefix) for path in changed_files):
            findings.append(
                ReviewFinding(
                    finding_id=rule.missing_evidence_id,
                    severity="blocking",
                    summary=rule.missing_evidence_summary,
                    detail=rule.missing_evidence_detail,
                    suggested_fix=rule.missing_evidence_fix,
                )
            )

    return findings


def maybe_run_llm_review(
    *,
    diff_text: str,
    changed_files: list[str],
    mode: str,
    strategy: dict[str, Any],
    profiles: list[str],
) -> dict[str, Any]:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "").strip()
    deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "").strip()
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip()
    examples = _strategy_examples(strategy=strategy, profiles=profiles)
    block_on_findings = bool(strategy.get("llm_blocking_enabled"))

    if not all((endpoint, api_version, deployment, api_key)):
        return {
            "status": "skipped",
            "findings": [],
            "detail": "Azure OpenAI review not configured for this run.",
            "profiles": profiles,
            "strategy_source": strategy.get("compiler", "builtin"),
            "block_on_findings": block_on_findings,
        }

    prompt = {
        "role": "system",
        "content": (
            "You are a strict Staff Engineer reviewing an AegisAP incident-repair PR. "
            f"The review mode is `{mode}`. "
            "Return compact JSON with a `findings` array. Each finding must contain "
            "`severity`, `summary`, `detail`, and `suggested_fix`. Use `blocking` only for clear rubric violations. "
            "If there are no material findings, return an empty array."
        ),
    }
    user_message = {
        "role": "user",
        "content": json.dumps(
            {
                "profiles": profiles,
                "strategy_source": strategy.get("compiler", "builtin"),
                "examples": examples,
                "changed_files": changed_files,
                "diff_excerpt": diff_text[:12000],
            },
            indent=2,
        ),
    }

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_version=api_version,
        api_key=api_key,
    )
    response = client.chat.completions.create(
        model=deployment,
        messages=[prompt, user_message],
        temperature=0.0,
        max_tokens=900,
    )
    raw = response.choices[0].message.content or ""
    try:
        payload = json.loads(raw)
        findings = payload.get("findings", [])
    except json.JSONDecodeError:
        return {
            "status": "error",
            "findings": [],
            "detail": raw,
            "profiles": profiles,
            "strategy_source": strategy.get("compiler", "builtin"),
            "block_on_findings": block_on_findings,
        }
    return {
        "status": "completed",
        "findings": findings,
        "detail": raw,
        "profiles": profiles,
        "strategy_source": strategy.get("compiler", "builtin"),
        "block_on_findings": block_on_findings,
    }


def _finding_blocks(severity: str) -> bool:
    return severity.lower() in {"blocking", "blocking_candidate"}


def compute_review_verdict(
    *,
    mode: str,
    deterministic: list[ReviewFinding],
    llm_review: dict[str, Any],
) -> dict[str, Any]:
    blocking_reasons = [
        finding.finding_id
        for finding in deterministic
        if _finding_blocks(finding.severity)
    ]

    if mode == "blocking" and llm_review.get("block_on_findings"):
        blocking_reasons.extend(
            finding.get("summary", "llm_review_finding")
            for finding in llm_review.get("findings", [])
            if _finding_blocks(str(finding.get("severity", "")))
        )

    unique_reasons = list(dict.fromkeys(blocking_reasons))
    return {
        "blocking": bool(unique_reasons),
        "blocking_reasons": unique_reasons,
    }


def render_review_markdown(
    *,
    base_ref: str,
    head_ref: str,
    mode: str,
    changed_files: list[str],
    profiles: list[str],
    deterministic: list[ReviewFinding],
    llm_review: dict[str, Any],
    verdict: dict[str, Any],
) -> str:
    lines = [
        "# Principal Review Draft",
        "",
        f"- Generated at: `{current_time()}`",
        f"- Base ref: `{base_ref}`",
        f"- Head ref: `{head_ref}`",
        f"- Review mode: `{mode}`",
        f"- Blocking verdict: `{verdict['blocking']}`",
        f"- Target profiles: `{', '.join(profiles) if profiles else 'unclassified'}`",
        "",
        "## Changed Files",
        "",
    ]
    lines.extend(f"- `{path}`" for path in changed_files[:50] or ["(no files changed)"])

    lines.extend(["", "## Deterministic Findings", ""])
    if deterministic:
        for finding in deterministic:
            lines.append(f"- `{finding.finding_id}` [{finding.severity}] {finding.summary}")
            lines.append(f"  {finding.detail} Fix: {finding.suggested_fix}")
    else:
        lines.append("- No deterministic findings.")

    lines.extend(["", "## LLM Review", ""])
    lines.append(f"- Status: `{llm_review['status']}`")
    lines.append(f"- Strategy source: `{llm_review.get('strategy_source', 'builtin')}`")
    lines.append(f"- Model findings can block: `{llm_review.get('block_on_findings', False)}`")
    if llm_review.get("findings"):
        for finding in llm_review["findings"]:
            lines.append(
                f"- [{finding.get('severity', 'unknown')}] {finding.get('summary', 'Unspecified finding')} "
                f"| {finding.get('detail', '')} Fix: {finding.get('suggested_fix', '')}"
            )
    elif llm_review.get("detail"):
        lines.append(f"- Detail: {llm_review['detail'][:1000]}")

    lines.extend(["", "## Verdict", ""])
    if verdict["blocking_reasons"]:
        for reason in verdict["blocking_reasons"]:
            lines.append(f"- Blocking: `{reason}`")
    else:
        lines.append("- No blocking findings.")
    return "\n".join(lines) + "\n"


def build_review_payload(
    *,
    repo_root: Path,
    base_ref: str,
    head_ref: str,
    mode: str = "shadow",
    strategy_path: str | Path | None = None,
) -> dict[str, Any]:
    diff_text, changed_files = get_diff(repo_root=repo_root, base_ref=base_ref, head_ref=head_ref)
    profiles = detect_profiles(changed_files=changed_files)
    strategy = load_review_strategy(repo_root=repo_root, strategy_path=strategy_path)
    deterministic = deterministic_findings(changed_files=changed_files, diff_text=diff_text)
    llm_review = maybe_run_llm_review(
        diff_text=diff_text,
        changed_files=changed_files,
        mode=mode,
        strategy=strategy,
        profiles=profiles,
    )
    verdict = compute_review_verdict(mode=mode, deterministic=deterministic, llm_review=llm_review)

    payload = {
        "generated_at": current_time(),
        "mode": mode,
        "shadow_mode": mode != "blocking",
        "blocking": verdict["blocking"],
        "blocking_reasons": verdict["blocking_reasons"],
        "base_ref": base_ref,
        "head_ref": head_ref,
        "changed_files": changed_files,
        "profiles": profiles,
        "strategy": {
            "compiler": strategy.get("compiler", "builtin"),
            "path": strategy.get("strategy_path", ""),
            "llm_blocking_enabled": bool(strategy.get("llm_blocking_enabled")),
        },
        "deterministic_findings": [asdict(item) for item in deterministic],
        "llm_review": llm_review,
        "telemetry": {
            "generated_at": current_time(),
            "mode": mode,
            "profiles": profiles,
            "changed_files": changed_files,
            "blocking": verdict["blocking"],
            "blocking_reasons": verdict["blocking_reasons"],
            "deterministic_finding_ids": [item.finding_id for item in deterministic],
            "human_decision": None,
            "learner_revision": None,
            "false_positive_label": None,
        },
    }
    payload["markdown"] = render_review_markdown(
        base_ref=base_ref,
        head_ref=head_ref,
        mode=mode,
        changed_files=changed_files,
        profiles=profiles,
        deterministic=deterministic,
        llm_review=llm_review,
        verdict=verdict,
    )
    return payload
