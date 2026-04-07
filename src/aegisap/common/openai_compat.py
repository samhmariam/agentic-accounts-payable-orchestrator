from __future__ import annotations

from typing import Any


def is_gpt5_chat_deployment(model: str) -> bool:
    return "gpt-5" in model.strip().lower()


def build_chat_completion_kwargs(
    *,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }

    if is_gpt5_chat_deployment(model):
        # GPT-5 chat deployments reject legacy max_tokens and temperature=0.
        if max_tokens is not None:
            kwargs["max_completion_tokens"] = max_tokens
        return kwargs

    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if temperature is not None:
        kwargs["temperature"] = temperature
    return kwargs
