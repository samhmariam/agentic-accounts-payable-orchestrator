from __future__ import annotations

from aegisap.cost.cost_ledger import append_cost_ledger_entry
from aegisap.observability.context import get_observability_context, update_observability_context
from aegisap.routing.model_router import ModelGateway, ModelInvocationRequest


class AzureOpenAIPlannerClient:
    """
    Live Day 4 planner client backed by Azure OpenAI chat completions.
    """

    def __init__(self, *, deployment: str | None = None) -> None:
        self.deployment = deployment

    async def invoke(self, prompt: str) -> str:
        context = get_observability_context()
        risk_flags = []
        if context is not None:
            risk_flags = list(context.metadata.get("risk_flags") or [])
        response_text, decision, ledger_entry = ModelGateway().invoke_text(
            ModelInvocationRequest(
                task_class="plan",
                node_name="payment_recommendation_planner",
                system_instruction=(
                    "You are the AegisAP planning controller.\n"
                    "Return JSON only.\n"
                    "Do not wrap the payload in markdown.\n"
                    "Do not omit mandatory controls from the policy overlay.\n"
                    "Do not produce explanatory prose outside the JSON payload."
                ),
                user_prompt=prompt,
                prompt_revision="day4",
                policy_version=context.policy_version if context is not None else None,
                risk_flags=risk_flags,
                evidence_conflict_count=int(context.metadata.get("evidence_conflict_count", 0))
                if context is not None
                else 0,
                metadata={"tenant": "aegisap-training"},
            )
        )
        if context is not None:
            ledger, total_cost = append_cost_ledger_entry(
                list(context.metadata.get("cost_ledger") or []),
                entry=ledger_entry,
            )
            update_observability_context(
                task_class="plan",
                model_deployment=decision.deployment_name,
                routing_decision=decision.reason,
                cost_ledger=ledger,
                workflow_cost_estimate=total_cost,
            )
        return response_text
