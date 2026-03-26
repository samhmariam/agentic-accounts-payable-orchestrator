from __future__ import annotations

import os
from functools import lru_cache

from aegisap.observability.metrics import record_estimated_cost, record_tokens
from aegisap.observability.retry_policy import RetryPolicy, execute_with_retry
from aegisap.observability.tracing import node_span_attributes, start_observability_span
from aegisap.security.credentials import get_openai_client


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value

@lru_cache(maxsize=1)
def _get_client():
    return get_openai_client()


def _extract_message_text(response) -> str:
    content = response.choices[0].message.content
    if isinstance(content, str):
        return content

    parts: list[str] = []
    for item in content or []:
        text = getattr(item, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)


class AzureOpenAIPlannerClient:
    """
    Live Day 4 planner client backed by Azure OpenAI chat completions.
    """

    def __init__(self, *, deployment: str | None = None) -> None:
        self.deployment = deployment or _required_env("AZURE_OPENAI_CHAT_DEPLOYMENT")

    async def invoke(self, prompt: str) -> str:
        client = _get_client()
        with start_observability_span(
            "dep.llm.call",
            attributes=node_span_attributes(
                node_name="llm_call",
                idempotent=True,
                prompt_revision="day4",
                model_name=self.deployment,
            ),
        ):
            response = execute_with_retry(
                client.chat.completions.create,
                policy=RetryPolicy(max_attempts=3, initial_backoff_ms=250, max_backoff_ms=1_000, deadline_ms=6_000),
                node_name="azure_openai_planner",
                dependency_name="azure_openai",
                idempotent=True,
                decision_reason_code="PLANNER_MODEL_CALL",
                kwargs={
                    "model": self.deployment,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are the AegisAP planning controller.\n"
                                "Return JSON only.\n"
                                "Do not wrap the payload in markdown.\n"
                                "Do not omit mandatory controls from the policy overlay.\n"
                                "Do not produce explanatory prose outside the JSON payload."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0,
                },
            )
            usage = getattr(response, "usage", None)
            if usage is not None:
                prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
                completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
                record_tokens(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    node_name="azure_openai_planner",
                    model_name=self.deployment,
                )
                record_estimated_cost(
                    cost_usd=round((prompt_tokens * 0.0000025) + (completion_tokens * 0.00001), 6),
                    node_name="azure_openai_planner",
                    model_name=self.deployment,
                )
        return _extract_message_text(response)
