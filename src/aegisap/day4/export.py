"""
Export helpers for the Day 4 explicit planning layer.
Converts ExecutionPlan objects to notebook-friendly table rows and Mermaid diagrams.
"""
from __future__ import annotations

from typing import Any


def plan_to_table(plan: Any) -> list[dict[str, Any]]:
    """
    Convert an ExecutionPlan's tasks to plain dicts for marimo table rendering.
    Works with both Pydantic ExecutionPlan models and dicts.
    """
    if hasattr(plan, "tasks"):
        tasks = plan.tasks
    elif isinstance(plan, dict):
        tasks = plan.get("tasks", [])
    else:
        return []

    rows = []
    for task in tasks:
        if hasattr(task, "model_dump"):
            t = task.model_dump(mode="json")
        elif hasattr(task, "__dict__"):
            t = vars(task)
        else:
            t = task
        rows.append(
            {
                "task_id": t.get("task_id", ""),
                "task_type": t.get("task_type", ""),
                "status": t.get("status", "pending"),
                "depends_on": ", ".join(t.get("depends_on", [])),
                "action_class": t.get("action_class", ""),
                "failure_behavior": t.get("failure_behavior", ""),
                "risk_flags": ", ".join(t.get("risk_flags", [])),
            }
        )
    return rows


def plan_to_mermaid(plan: Any) -> str:
    """
    Convert an ExecutionPlan to a Mermaid flowchart showing task dependencies.
    """
    rows = plan_to_table(plan)
    if not rows:
        return "flowchart LR\n    EMPTY[No tasks]"

    lines = ["flowchart LR"]
    for row in rows:
        tid = row["task_id"].replace("-", "_")
        label = f'{tid}["{row["task_type"]}\\n({row["status"]})"]'
        lines.append(f"    {label}")

    lines.append("")
    for row in rows:
        if row["depends_on"]:
            for dep in row["depends_on"].split(", "):
                dep = dep.strip().replace("-", "_")
                tid = row["task_id"].replace("-", "_")
                lines.append(f"    {dep} --> {tid}")

    return "\n".join(lines)
