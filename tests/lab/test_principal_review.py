from __future__ import annotations

from aegisap.lab.review import compute_review_verdict, deterministic_findings


def test_deterministic_review_flags_over_privileged_rbac() -> None:
    findings = deterministic_findings(
        changed_files=["infra/modules/role_assignments.bicep"],
        diff_text='+            roleDefinitionName: "Contributor"\n',
    )

    assert any(item.finding_id == "over_privileged_rbac" for item in findings)


def test_deterministic_review_flags_missing_tests_for_src_changes() -> None:
    findings = deterministic_findings(
        changed_files=["src/aegisap/day_01/normalizers.py"],
        diff_text="+    return amount\n",
    )

    assert any(item.finding_id == "missing_tests" for item in findings)
    assert any(item.finding_id == "missing_day01_evidence" for item in findings)


def test_deterministic_review_flags_wave1_scope_drift_and_missing_day02_evidence() -> None:
    findings = deterministic_findings(
        changed_files=[
            "src/aegisap/observability/retry_policy.py",
            "infra/network/private_endpoints.bicep",
            "tests/day2/test_resilience_controls.py",
        ],
        diff_text="+TRANSIENT_STATUS_CODES = ('500',)\n",
    )

    ids = {item.finding_id for item in findings}
    assert "wave1_wrong_file_scope" in ids
    assert "missing_day02_evidence" in ids


def test_deterministic_review_flags_missing_wave2_day03_and_day05_evidence() -> None:
    findings = deterministic_findings(
        changed_files=[
            "src/aegisap/day3/retrieval/ranker.py",
            "src/aegisap/day5/workflow/resume_service.py",
            "tests/day5/integration/test_resume_service.py",
        ],
        diff_text="+    return ranked\n",
    )

    ids = {item.finding_id for item in findings}
    assert "missing_day03_evidence" in ids
    assert "missing_day05_evidence" in ids


def test_deterministic_review_flags_missing_wave2_day04_and_day06_evidence() -> None:
    findings = deterministic_findings(
        changed_files=[
            "src/aegisap/day4/planning/policy_overlay.py",
            "src/aegisap/day6/review/prompt_injection.py",
            "tests/day6/test_review_gate.py",
        ],
        diff_text="+    return outcome\n",
    )

    ids = {item.finding_id for item in findings}
    assert "missing_day04_evidence" in ids
    assert "missing_day06_evidence" in ids


def test_deterministic_review_flags_wave3_missing_day08_evidence_and_rbac() -> None:
    findings = deterministic_findings(
        changed_files=[
            "infra/modules/role_assignments.bicep",
            "tests/day8/test_security_and_context.py",
        ],
        diff_text='+var runtimeRole = searchIndexDataContributorRoleDefinitionId\n',
    )

    ids = {item.finding_id for item in findings}
    assert "over_privileged_rbac" in ids
    assert "missing_day08_evidence" in ids


def test_deterministic_review_flags_wave3_missing_day09_and_day10_evidence() -> None:
    findings = deterministic_findings(
        changed_files=[
            "src/aegisap/routing/routing_policy.py",
            "tests/day9/test_routing_policy.py",
            "src/aegisap/deploy/gates.py",
            "tests/day10/test_release_envelope.py",
        ],
        diff_text="+    return envelope\n",
    )

    ids = {item.finding_id for item in findings}
    assert "cross_day_scope_drift" in ids
    assert "missing_day09_evidence" in ids
    assert "missing_day10_evidence" in ids


def test_deterministic_review_flags_wave4_missing_day11_and_day12_evidence() -> None:
    findings = deterministic_findings(
        changed_files=[
            "src/aegisap/identity/actor_verifier.py",
            "tests/day11/test_actor_verification.py",
            "src/aegisap/network/bicep_policy_checker.py",
            "tests/day12/test_bicep_policy_checker.py",
        ],
        diff_text="+    return result\n",
    )

    ids = {item.finding_id for item in findings}
    assert "cross_day_scope_drift" in ids
    assert "missing_day11_evidence" in ids
    assert "missing_day12_evidence" in ids


def test_deterministic_review_flags_wave4_missing_day13_and_day14_evidence() -> None:
    findings = deterministic_findings(
        changed_files=[
            "src/aegisap/mcp/server.py",
            "tests/day13/test_mcp_server.py",
            "src/aegisap/deploy/gates_v2.py",
            "tests/day14/test_breaking_changes.py",
        ],
        diff_text="+    return payload\n",
    )

    ids = {item.finding_id for item in findings}
    assert "cross_day_scope_drift" in ids
    assert "missing_day13_evidence" in ids
    assert "missing_day14_evidence" in ids


def test_blocking_mode_verdict_blocks_on_deterministic_findings() -> None:
    findings = deterministic_findings(
        changed_files=["src/aegisap/day_01/normalizers.py"],
        diff_text="+    return amount\n",
    )

    verdict = compute_review_verdict(
        mode="blocking",
        deterministic=findings,
        llm_review={"findings": [], "block_on_findings": False},
    )

    assert verdict["blocking"] is True
    assert "missing_tests" in verdict["blocking_reasons"]
