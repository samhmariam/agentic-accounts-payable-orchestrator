from __future__ import annotations

import asyncio

from aegisap.day4.planning.azure_openai_planner import AzureOpenAIPlannerClient


class FakeResponse:
    def __init__(self, content):
        class Message:
            def __init__(self, content):
                self.content = content

        class Choice:
            def __init__(self, content):
                self.message = Message(content)

        self.choices = [Choice(content)]


class FakeClient:
    def __init__(self, content):
        self._content = content
        self.chat = self
        self.completions = self

    def create(self, **kwargs):
        return FakeResponse(self._content)


def test_azure_openai_planner_returns_string_content(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "planner")
    monkeypatch.setattr(
        "aegisap.day4.planning.azure_openai_planner._get_client",
        lambda: FakeClient('{"plan_id": "plan-1"}'),
    )

    result = asyncio.run(AzureOpenAIPlannerClient().invoke("Return JSON"))

    assert result == '{"plan_id": "plan-1"}'


def test_azure_openai_planner_flattens_content_parts(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "planner")
    parts = [type("Part", (), {"text": '{"plan_id": "'})(), type("Part", (), {"text": 'plan-2"}'})()]
    monkeypatch.setattr(
        "aegisap.day4.planning.azure_openai_planner._get_client",
        lambda: FakeClient(parts),
    )

    result = asyncio.run(AzureOpenAIPlannerClient().invoke("Return JSON"))

    assert result == '{"plan_id": "plan-2"}'
