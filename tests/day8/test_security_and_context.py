from __future__ import annotations

from aegisap.observability.context import WorkflowObservabilityContext
from aegisap.observability.langsmith_bridge import build_langsmith_metadata, ensure_langsmith_ids
from aegisap.security.config import load_security_config
from aegisap.security.policy import validate_security_posture


def test_cloud_runtime_rejects_langsmith_api_key_env_secret() -> None:
    config = load_security_config(
        {
            "AEGISAP_ENVIRONMENT": "cloud",
            "AZURE_KEY_VAULT_URI": "https://example.vault.azure.net/",
            "LANGSMITH_API_KEY": "raw-secret",
        }
    )

    try:
        validate_security_posture(config)
    except RuntimeError as exc:
        assert "LANGSMITH_API_KEY" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("LANGSMITH_API_KEY should be forbidden outside local/test")


def test_langsmith_metadata_reuses_workflow_correlation_ids() -> None:
    context = WorkflowObservabilityContext(
        request_id="req-1",
        workflow_run_id="wf-123",
        case_id="case-123",
        thread_id="thread-123",
        checkpoint_id="cp-9",
        trace_id="trace-123",
        environment="test",
        deployment_revision="rev-test",
    )
    ensure_langsmith_ids(context)
    metadata = build_langsmith_metadata(context)

    assert metadata["workflow_run_id"] == "wf-123"
    assert metadata["checkpoint_id"] == "cp-9"
    assert metadata["trace_id"] == "trace-123"
    assert metadata["case_id_hash"] != "case-123"
