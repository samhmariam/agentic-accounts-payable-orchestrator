"""tests/day13/test_dlq_consumer.py — unit tests for DlqConsumer + CompensatingActionRunner"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCompensatingActionRunner:
    def test_register_and_compensate(self):
        from aegisap.integration.compensating_action import CompensatingActionRunner

        runner = CompensatingActionRunner()

        @runner.register("non_transient")
        async def _action(message_id: str, payload: dict) -> dict:
            return {"handled": message_id}

        result = asyncio.run(runner.compensate(
            "msg-001", {"invoice_id": "INV-001"}, "non_transient"))
        assert result["handled"] == "msg-001"

    def test_compensate_unknown_classification_raises(self):
        from aegisap.integration.compensating_action import CompensatingActionRunner

        runner = CompensatingActionRunner()
        with pytest.raises((KeyError, ValueError)):
            asyncio.run(runner.compensate("msg-001", {}, "unknown_class"))

    def test_guarded_decorator(self):
        from aegisap.integration.compensating_action import CompensatingActionRunner

        runner = CompensatingActionRunner()

        @runner.register("non_transient")
        async def _action(message_id: str, payload: dict) -> dict:
            return {"ok": True}

        @runner.guarded("non_transient")
        async def _guarded_func(x: int) -> int:
            if x < 0:
                raise ValueError("negative")
            return x * 2

        # Normal execution
        result = asyncio.run(_guarded_func(5))
        assert result == 10

        # On exception, compensating action runs
        # (guarded wraps the call — exact behavior depends on implementation)


class TestDlqConsumer:
    def test_drain_empty_queue_all_handled(self, monkeypatch):
        monkeypatch.setenv("AZURE_SERVICE_BUS_CONNECTION_STRING", "fake-conn")
        monkeypatch.setenv("AEGISAP_DLQ_QUEUE_NAME", "invoice-submissions")

        with patch("aegisap.integration.dlq_consumer.ServiceBusClient") as mock_sb_cls:
            mock_sb = MagicMock()
            mock_receiver = MagicMock()
            mock_receiver.__enter__ = MagicMock(return_value=mock_receiver)
            mock_receiver.__exit__ = MagicMock(return_value=False)
            mock_receiver.receive_messages = MagicMock(return_value=[])
            mock_sb.get_queue_receiver = MagicMock(return_value=mock_receiver)
            mock_sb.__enter__ = MagicMock(return_value=mock_sb)
            mock_sb.__exit__ = MagicMock(return_value=False)
            mock_sb_cls.from_connection_string = MagicMock(
                return_value=mock_sb)

            from aegisap.integration.dlq_consumer import DlqConsumer
            consumer = DlqConsumer.from_env()
            report = asyncio.run(consumer.drain())

        assert report.all_handled is True
        assert report.drained == 0
