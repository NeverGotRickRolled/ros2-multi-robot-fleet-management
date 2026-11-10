"""In-memory task records and validated lifecycle transitions."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .models import Task


class TaskState(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REJECTED = "rejected"


_ALLOWED = {
    TaskState.PENDING: {TaskState.ASSIGNED},
    TaskState.ASSIGNED: {
        TaskState.ACCEPTED, TaskState.REJECTED, TaskState.FAILED
    },
    TaskState.ACCEPTED: {
        TaskState.EXECUTING, TaskState.SUCCEEDED, TaskState.FAILED
    },
    TaskState.EXECUTING: {TaskState.SUCCEEDED, TaskState.FAILED},
    TaskState.SUCCEEDED: set(),
    TaskState.FAILED: set(),
    TaskState.REJECTED: set(),
}


@dataclass
class TaskRecord:
    task: Task
    state: TaskState = TaskState.PENDING
    robot_id: str = ""
    reason: str = ""


class TaskStore:
    """Stores tasks and rejects duplicate IDs or invalid state transitions."""

    def __init__(self):
        self._records: Dict[str, TaskRecord] = {}

    def add(self, task: Task) -> TaskRecord:
        if task.task_id in self._records:
            raise ValueError(f"duplicate task_id: {task.task_id}")
        record = TaskRecord(task=task)
        self._records[task.task_id] = record
        return record

    def get(self, task_id: str) -> Optional[TaskRecord]:
        return self._records.get(task_id)

    def pending(self) -> List[TaskRecord]:
        return [
            record for record in self._records.values()
            if record.state == TaskState.PENDING
        ]

    def transition(
        self, task_id: str, new_state: TaskState, robot_id: str = "",
        reason: str = ""
    ) -> TaskRecord:
        record = self.get(task_id)
        if record is None:
            raise ValueError(f"unknown task_id: {task_id}")
        if new_state not in _ALLOWED[record.state]:
            raise ValueError(
                f"invalid task transition: {record.state.value} -> {new_state.value}"
            )
        if record.robot_id and robot_id and record.robot_id != robot_id:
            raise ValueError("task is assigned to a different robot")
        if new_state == TaskState.ASSIGNED and not robot_id:
            raise ValueError("assigned task requires robot_id")
        record.state = new_state
        if robot_id:
            record.robot_id = robot_id
        record.reason = reason
        return record
