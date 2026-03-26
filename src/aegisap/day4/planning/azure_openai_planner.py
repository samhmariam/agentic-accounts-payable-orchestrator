from __future__ import annotations

import os
from functools import lru_cache

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
        response = client.chat.completions.create(
            model=self.deployment,
            messages=[
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
            temperature=0,
        )
        return _extract_message_text(response)
