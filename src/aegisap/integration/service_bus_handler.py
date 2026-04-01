"""Azure Service Bus handler for AegisAP (Day 13).

AegisAP uses Service Bus as the reliable transport for:
- Inbound invoice events from ERP/document-intake systems
- Outbound approval notifications to downstream LOB systems
- DLQ-resident messages requiring manual or automated remediation

Authentication uses Managed Identity (no connection strings in code).

Usage::

    handler = ServiceBusHandler.from_env()
    # Receive and process one message
    with handler.receive() as msg:
        process(msg)
        handler.complete(msg)
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage as AzureServiceBusMessage
from azure.servicebus import ServiceBusReceiveMode


@dataclass
class ServiceBusMessage:
    """Application-level wrapper around an Azure Service Bus message."""

    body: dict[str, Any]
    message_id: str
    correlation_id: str | None
    subject: str | None
    _raw: Any = field(repr=False, default=None)


class ServiceBusHandler:
    """Send and receive structured messages on Azure Service Bus.

    Both the sender and the receiver authenticate via Managed Identity.
    """

    def __init__(
        self,
        namespace_fqdn: str,
        queue_name: str,
        max_wait_time: float = 5.0,
    ) -> None:
        """
        Args:
            namespace_fqdn: Fully-qualified domain name, e.g.
                            ``aegisap-sb.servicebus.windows.net``
            queue_name: Name of the Service Bus queue to read/write.
            max_wait_time: How long to block waiting for a message (seconds).
        """
        self._namespace_fqdn = namespace_fqdn
        self._queue_name = queue_name
        self._max_wait_time = max_wait_time
        self._credential = DefaultAzureCredential()

    @classmethod
    def from_env(cls) -> "ServiceBusHandler":
        namespace_fqdn = os.environ["AZURE_SERVICEBUS_NAMESPACE_FQDN"]
        queue_name = os.environ["AZURE_SERVICEBUS_QUEUE_NAME"]
        return cls(namespace_fqdn=namespace_fqdn, queue_name=queue_name)

    def send(
        self,
        body: dict[str, Any],
        correlation_id: str | None = None,
        subject: str | None = None,
    ) -> None:
        """Send a JSON-serialisable message to the configured queue."""
        with ServiceBusClient(
            fully_qualified_namespace=self._namespace_fqdn,
            credential=self._credential,
        ) as sb_client:
            with sb_client.get_queue_sender(self._queue_name) as sender:
                msg = AzureServiceBusMessage(
                    body=json.dumps(body).encode(),
                    correlation_id=correlation_id,
                    subject=subject,
                )
                sender.send_messages(msg)

    @contextmanager
    def receive(self) -> Generator[ServiceBusMessage | None, None, None]:
        """Context manager that yields one message or None if queue is empty.

        The caller must call ``complete()`` or ``abandon()`` on the message
        before the context exits; otherwise the message lock expires and the
        message is automatically abandoned.
        """
        with ServiceBusClient(
            fully_qualified_namespace=self._namespace_fqdn,
            credential=self._credential,
        ) as sb_client:
            with sb_client.get_queue_receiver(
                queue_name=self._queue_name,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                max_wait_time=self._max_wait_time,
            ) as receiver:
                messages = receiver.receive_messages(max_message_count=1)
                if not messages:
                    yield None
                    return
                raw = messages[0]
                try:
                    body_bytes = b"".join(raw.body)
                    body = json.loads(body_bytes.decode())
                except Exception:
                    body = {}
                msg = ServiceBusMessage(
                    body=body,
                    message_id=raw.message_id or "",
                    correlation_id=raw.correlation_id,
                    subject=raw.subject,
                    _raw=raw,
                )
                self._current_receiver = receiver
                yield msg

    def complete(self, msg: ServiceBusMessage) -> None:
        """Complete (acknowledge) a received message."""
        if msg._raw is not None and hasattr(self, "_current_receiver"):
            self._current_receiver.complete_message(msg._raw)

    def abandon(self, msg: ServiceBusMessage) -> None:
        """Abandon a received message so it becomes available again."""
        if msg._raw is not None and hasattr(self, "_current_receiver"):
            self._current_receiver.abandon_message(msg._raw)

    def dead_letter(self, msg: ServiceBusMessage, reason: str) -> None:
        """Explicitly dead-letter a message with a reason string."""
        if msg._raw is not None and hasattr(self, "_current_receiver"):
            self._current_receiver.dead_letter_message(
                msg._raw, reason=reason, error_description=reason
            )
