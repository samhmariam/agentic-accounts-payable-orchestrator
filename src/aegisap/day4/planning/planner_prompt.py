from __future__ import annotations

import json

from .plan_types import CaseFacts, DerivedPolicyOverlay


def build_planner_prompt(*, case_facts: CaseFacts, policy_overlay: DerivedPolicyOverlay) -> str:
    return "\n".join(
        [
            "You are the Payment Recommendation Planner for AegisAP.",
            "Return ONLY valid JSON that matches the required execution plan schema.",
            "",
            "Objective:",
            "Create a safe execution plan that determines whether a payment recommendation is eligible.",
            "",
            "Non-negotiable constraints:",
            "- Do not create or release a payment recommendation unless the recommendation gate can later be satisfied.",
            "- Do not waive missing PO requirements.",
            "- Do not waive bank change verification.",
            "- Existing supplier status does not remove fresh risk indicators.",
            "- Use the provided policy overlay as binding constraints, not suggestions.",
            "- Every critical control must either be satisfied or route to escalation.",
            "- Include escalation_route and escalation_reason_template.",
            "- Keep all actions reversible and set irreversible_actions_allowed to false.",
            "",
            "Required task fields:",
            "- task_id",
            "- task_type",
            "- owner_agent",
            "- depends_on",
            "- inputs",
            "- required_evidence",
            "- expected_outputs",
            "- preconditions",
            "- stop_if_missing",
            "- min_confidence",
            "- on_failure",
            "- action_class",
            "",
            "Case facts:",
            json.dumps(case_facts.model_dump(), indent=2),
            "",
            "Deterministic policy overlay:",
            json.dumps(policy_overlay.model_dump(), indent=2),
            "",
            "Planning rules:",
            "- Include all mandatory task types from the overlay.",
            "- Add a manual escalation package task if combined risk exists.",
            "- Recommendation tasks must remain reversible.",
            "- Global preconditions and stop conditions must include the overlay items.",
            "- Escalation triggers, route, and approvals must include the overlay items.",
            "- recommendation_gate must explicitly track task completion, evidence sufficiency, blockers, confidence, approvals, escalation status, PO status, bank change verification, and approval path.",
            "",
            "Output format:",
            "Return a single JSON object. No markdown fences. No commentary.",
        ]
    )
