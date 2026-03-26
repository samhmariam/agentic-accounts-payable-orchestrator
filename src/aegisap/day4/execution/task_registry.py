from __future__ import annotations

from aegisap.day4.execution.default_workers import default_workers
from aegisap.day4.execution.task_contracts import WorkerExecutor
from aegisap.day4.planning.plan_types import PlanTaskType


class TaskRegistry:
    def __init__(self) -> None:
        self._executors: dict[PlanTaskType, WorkerExecutor] = {}

    def register(self, executor: WorkerExecutor) -> None:
        self._executors[executor.task_type] = executor

    def get(self, task_type: PlanTaskType) -> WorkerExecutor:
        executor = self._executors.get(task_type)
        if executor is None:
            raise ValueError(f"no_executor_registered_for_task_type:{task_type}")
        return executor


def create_default_task_registry() -> TaskRegistry:
    registry = TaskRegistry()
    for executor in default_workers():
        registry.register(executor)
    return registry
