from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from aegisap.day5.state.durable_models import DurableWorkflowState, HistoryMessage


@dataclass
class HistoryCompactionResult:
    compacted: bool
    summary_block: dict | None
    dropped_count: int


class HistoryManager:
    """
    Keeps structured state authoritative.
    Uses raw recent window plus structured summary blocks for older history.
    """

    def __init__(self, max_raw_messages: int = 24, retain_recent: int = 12) -> None:
        self.max_raw_messages = max_raw_messages
        self.retain_recent = retain_recent

    def append_message(
        self,
        state: DurableWorkflowState,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> None:
        state.history_state.raw_messages.append(
            HistoryMessage(
                role=role,  # type: ignore[arg-type]
                content=content,
                metadata=metadata or {},
                created_at=datetime.now(timezone.utc),
            )
        )

    def compact_if_needed(
        self,
        state: DurableWorkflowState,
        summariser: Callable[[list[HistoryMessage]], str],
    ) -> HistoryCompactionResult:
        raw = state.history_state.raw_messages
        if len(raw) <= self.max_raw_messages:
            return HistoryCompactionResult(False, None, 0)

        to_summarise = raw[:-self.retain_recent]
        retained = raw[-self.retain_recent:]

        summary_text = summariser(to_summarise)
        summary_block = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "message_count": len(to_summarise),
            "summary": summary_text,
            "source_roles": [m.role for m in to_summarise],
        }

        state.history_state.summary_blocks.append(summary_block)
        state.history_state.raw_messages = retained

        return HistoryCompactionResult(
            compacted=True,
            summary_block=summary_block,
            dropped_count=len(to_summarise),
        )

    def build_node_context(
        self,
        state: DurableWorkflowState,
        include_summary: bool = True,
        raw_limit: int = 8,
    ) -> dict:
        recent = state.history_state.raw_messages[-raw_limit:]
        context = {
            "recent_history": [m.model_dump(mode="json") for m in recent],
            "approval_state": state.approval_state.model_dump(mode="json"),
            "plan_version": state.plan_version,
            "current_node": state.current_node,
        }
        if include_summary:
            context["history_summaries"] = state.history_state.summary_blocks[-3:]
        return context
