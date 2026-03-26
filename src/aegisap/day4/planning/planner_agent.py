from __future__ import annotations

import json
import re
from typing import Protocol

from .planner_prompt import build_planner_prompt
from .plan_types import CaseFacts, DerivedPolicyOverlay


class ModelClient(Protocol):
    async def invoke(self, prompt: str) -> str:
        ...


async def request_execution_plan_payload(
    *,
    model: ModelClient,
    case_facts: CaseFacts,
    policy_overlay: DerivedPolicyOverlay,
) -> object:
    prompt = build_planner_prompt(case_facts=case_facts, policy_overlay=policy_overlay)
    raw = await model.invoke(prompt)
    return coerce_json(raw)


def coerce_json(raw: str) -> object:
    trimmed = raw.strip()
    if trimmed.startswith("{"):
        return json.loads(trimmed)

    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", trimmed, flags=re.IGNORECASE)
    if fenced and fenced.group(1):
        return json.loads(fenced.group(1).strip())

    raise ValueError("planner_did_not_return_json")
