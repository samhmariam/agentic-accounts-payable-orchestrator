from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReplayClass(str, Enum):
    PURE = "pure"
    SNAPSHOTTED_READ = "snapshotted_read"
    SIDE_EFFECTING = "side_effecting"


class ResumeMode(str, Enum):
    ORDINARY_RESUME = "ordinary_resume"
    EXPLICIT_REVALIDATION = "explicit_revalidation"


@dataclass(frozen=True)
class ReplayDecision:
    replay_allowed: bool
    reason: str



def decide_replay(node_class: ReplayClass, mode: ResumeMode) -> ReplayDecision:
    if node_class == ReplayClass.PURE:
        return ReplayDecision(True, "Pure node can replay when no later checkpoint supersedes it.")

    if node_class == ReplayClass.SNAPSHOTTED_READ:
        if mode == ResumeMode.EXPLICIT_REVALIDATION:
            return ReplayDecision(True, "Revalidation step explicitly requested.")
        return ReplayDecision(
            False,
            "Time-varying evidence must be loaded from checkpoint snapshot during ordinary resume.",
        )

    if node_class == ReplayClass.SIDE_EFFECTING:
        return ReplayDecision(
            False,
            "Side-effecting node must not replay implicitly; use idempotency ledger lookup instead.",
        )

    return ReplayDecision(False, "Unknown replay class.")
