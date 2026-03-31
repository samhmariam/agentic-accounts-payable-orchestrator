from __future__ import annotations

import json

from aegisap.routing import routing_policy
from aegisap.routing.routing_policy import route_task


def test_low_risk_extract_routes_to_light_model() -> None:
    decision = route_task(task_class="extract", risk_flags=["clean_path"])

    assert decision.deployment_tier == "light"
    assert decision.task_class == "extract"
    assert decision.escalated is False


def test_risk_escalators_promote_extract_to_strong_model() -> None:
    decision = route_task(task_class="extract", risk_flags=["high_value", "bank_details_changed"])

    assert decision.deployment_tier == "strong"
    assert decision.escalated is True
    assert decision.reason == "risk_escalator_selected_strong_model"


def test_final_render_sensitive_path_uses_strong_model() -> None:
    decision = route_task(task_class="final_render", final_render_sensitive=True)

    assert decision.deployment_tier == "strong"
    assert decision.reason == "sensitive_final_render_requires_strong"


def test_router_prefers_azure_chat_deployment_from_env(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "chat")
    monkeypatch.delenv("AEGISAP_LIGHT_MODEL_DEPLOYMENT", raising=False)
    monkeypatch.delenv("AEGISAP_STRONG_MODEL_DEPLOYMENT", raising=False)

    light = route_task(task_class="extract")
    strong = route_task(task_class="plan")

    assert light.deployment_name == "chat"
    assert strong.deployment_name == "chat"


def test_router_reads_chat_deployment_from_local_day0_state(monkeypatch, tmp_path) -> None:
    state_dir = tmp_path / ".day0"
    state_dir.mkdir()
    state_path = state_dir / "core.json"
    state_path.write_text(
        json.dumps(
            {
                "environment": {
                    "AZURE_OPENAI_CHAT_DEPLOYMENT": "chat",
                }
            }
        )
    )

    monkeypatch.setenv("AEGISAP_ENVIRONMENT", "local")
    monkeypatch.delenv("AZURE_OPENAI_CHAT_DEPLOYMENT", raising=False)
    monkeypatch.delenv("AEGISAP_LIGHT_MODEL_DEPLOYMENT", raising=False)
    monkeypatch.delenv("AEGISAP_STRONG_MODEL_DEPLOYMENT", raising=False)
    monkeypatch.setattr(routing_policy, "__file__", str(tmp_path / "a" / "b" / "c" / "routing_policy.py"))

    light = route_task(task_class="extract")
    strong = route_task(task_class="plan")

    assert light.deployment_name == "chat"
    assert strong.deployment_name == "chat"
