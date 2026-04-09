from __future__ import annotations

from aegisap.lab.artifacts import rebuild_day_artifact


def test_rebuild_day7_artifact_writes_eval_and_transfer_outputs() -> None:
    result = rebuild_day_artifact("07")
    assert result["day"] == "07"
    assert result["payload"]["day"] == 7
    assert "claims_transfer_report_path" in result["supporting_artifacts"]
    transfer = result["supporting_artifacts"]["claims_transfer_report"]
    assert transfer["total_cases"] == 5


def test_rebuild_day10_artifact_writes_release_and_rollback_outputs() -> None:
    result = rebuild_day_artifact("10")
    assert result["day"] == "10"
    assert "all_passed" in result["payload"]
    assert "rollback_rehearsal_path" in result["supporting_artifacts"]
    rollback = result["supporting_artifacts"]["rollback_rehearsal"]
    assert rollback["traffic_restored_before_git"] is True
    assert rollback["rollback_unit"] == "aca_revision"


def test_rebuild_day11_artifact_writes_obo_contract() -> None:
    result = rebuild_day_artifact("11")
    assert result["day"] == "11"
    assert result["payload"]["gate_passed"] is True
    assert result["payload"]["actor_binding_ok"] is True


def test_rebuild_day12_artifact_writes_network_bundle() -> None:
    result = rebuild_day_artifact("12")
    assert result["day"] == "12"
    assert result["payload"]["all_passed"] is True
    assert "static_bicep_analysis_path" in result["supporting_artifacts"]


def test_rebuild_day13_artifact_writes_contract_and_dlq_reports() -> None:
    result = rebuild_day_artifact("13")
    assert result["day"] == "13"
    assert result["payload"]["all_passed"] is True
    assert "webhook_reliability_report_path" in result["supporting_artifacts"]


def test_rebuild_day14_artifact_writes_cto_and_chaos_outputs() -> None:
    result = rebuild_day_artifact("14")
    assert result["day"] == "14"
    assert result["payload"]["cto_trace_report_path"].endswith("build/day14/cto_trace_report.json")
    chaos = result["supporting_artifacts"]["chaos_capstone"]["payload"]
    assert chaos["passed"] == chaos["total"] == 10
