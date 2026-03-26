from __future__ import annotations

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
