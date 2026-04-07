from __future__ import annotations

from aegisap.common.openai_compat import build_chat_completion_kwargs


def test_gpt5_chat_kwargs_use_gpt5_compatible_parameters() -> None:
    kwargs = build_chat_completion_kwargs(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": "Reply with OK"}],
        temperature=0.0,
        max_tokens=1,
    )

    assert kwargs["model"] == "gpt-5-nano"
    assert kwargs["max_completion_tokens"] == 1
    assert "max_tokens" not in kwargs
    assert "temperature" not in kwargs


def test_legacy_chat_kwargs_keep_legacy_parameters() -> None:
    kwargs = build_chat_completion_kwargs(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": "Reply with OK"}],
        temperature=0.0,
        max_tokens=1,
    )

    assert kwargs["model"] == "gpt-4.1-mini"
    assert kwargs["max_tokens"] == 1
    assert kwargs["temperature"] == 0.0
    assert "max_completion_tokens" not in kwargs
