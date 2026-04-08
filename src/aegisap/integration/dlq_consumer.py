"""Dead-Letter Queue consumer for AegisAP (Day 13)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusReceiveMode


_TRANSIENT_REASONS = frozenset({
    "timeout",
    "connection_error",
    "service_unavailable",
    "throttled",
})


@dataclass
class DlqEntry:
    message_id: str
    body: dict[str, Any]
    failure_reason: str | None
    dead_letter_reason: str | None
    is_transient: bool


@dataclass
class DlqReport:
    total: int = 0
    retried: int = 0
    archived: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def all_handled(self) -> bool:
        return len(self.errors) == 0

    @property
    def drained(self) -> int:
        return self.total

    def summary(self) -> str:
        return (
            f"DLQ drain: total={self.total} retried={self.retried} "
            f"archived={self.archived} errors={len(self.errors)}"
        )

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "retried": self.retried,
            "archived": self.archived,
            "error_count": len(self.errors),
            "errors": self.errors[:10],
            "all_handled": self.all_handled,
            "drained": self.drained,
        }


class DlqConsumer:
    """Drain and process messages from the AegisAP Service Bus Dead-Letter Queue."""

    def __init__(
        self,
        *,
        namespace_fqdn: str | None = None,
        queue_name: str,
        connection_string: str | None = None,
        max_wait_time: float = 3.0,
    ) -> None:
        self._namespace_fqdn = namespace_fqdn
        self._queue_name = queue_name
        self._connection_string = connection_string
        self._max_wait_time = max_wait_time
        self._credential = None if connection_string else DefaultAzureCredential()

    @classmethod
    def from_env(cls) -> "DlqConsumer":
        connection_string = os.environ.get("AZURE_SERVICE_BUS_CONNECTION_STRING", "").strip()
        queue_name = (
            os.environ.get("AEGISAP_DLQ_QUEUE_NAME", "").strip()
            or os.environ.get("AZURE_SERVICEBUS_QUEUE_NAME", "").strip()
        )
        if connection_string and queue_name:
            return cls(connection_string=connection_string, queue_name=queue_name)
        namespace_fqdn = os.environ["AZURE_SERVICEBUS_NAMESPACE_FQDN"]
        queue_name = queue_name or os.environ["AZURE_SERVICEBUS_QUEUE_NAME"]
        return cls(namespace_fqdn=namespace_fqdn, queue_name=queue_name)

    def _build_client(self) -> ServiceBusClient:
        if self._connection_string:
            return ServiceBusClient.from_connection_string(self._connection_string)
        if not self._namespace_fqdn or self._credential is None:
            raise ValueError("namespace_fqdn or connection_string is required.")
        return ServiceBusClient(
            fully_qualified_namespace=self._namespace_fqdn,
            credential=self._credential,
        )

    async def drain(self, max_messages: int = 100) -> DlqReport:
        report = DlqReport()
        with self._build_client() as sb_client:
            dlq_path = f"{self._queue_name}/$DeadLetterQueue"
            with sb_client.get_queue_receiver(
                queue_name=dlq_path,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                max_wait_time=self._max_wait_time,
            ) as receiver:
                while report.total < max_messages:
                    msgs = receiver.receive_messages(max_message_count=10)
                    if not msgs:
                        break
                    for raw in msgs:
                        report.total += 1
                        try:
                            body_bytes = b"".join(raw.body)
                            body = json.loads(body_bytes.decode())
                        except Exception:
                            body = {}

                        dlq_reason = getattr(raw, "dead_letter_reason", None)
                        failure_reason = body.get("failure_reason", "unknown")
                        entry = DlqEntry(
                            message_id=raw.message_id or "",
                            body=body,
                            failure_reason=failure_reason,
                            dead_letter_reason=dlq_reason,
                            is_transient=failure_reason in _TRANSIENT_REASONS,
                        )

                        try:
                            receiver.complete_message(raw)
                            if entry.is_transient:
                                report.retried += 1
                            else:
                                report.archived += 1
                        except Exception as exc:
                            report.errors.append(str(exc))

        return report
