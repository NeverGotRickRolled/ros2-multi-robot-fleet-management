import pytest

from fleet_manager.models import Task
from fleet_manager.task_store import TaskState, TaskStore


def test_task_lifecycle_accepts_execution_and_success():
    store = TaskStore()
    store.add(Task("task_1", "dock"))
    store.transition("task_1", TaskState.ASSIGNED, "robot_1")
    store.transition("task_1", TaskState.ACCEPTED, "robot_1")
    store.transition("task_1", TaskState.EXECUTING, "robot_1")
    record = store.transition("task_1", TaskState.SUCCEEDED, "robot_1")
    assert record.state == TaskState.SUCCEEDED


def test_duplicate_task_ids_are_rejected():
    store = TaskStore()
    store.add(Task("task_1", "dock"))
    with pytest.raises(ValueError, match="duplicate"):
        store.add(Task("task_1", "charging_station"))


def test_task_cannot_be_assigned_to_two_robots():
    store = TaskStore()
    store.add(Task("task_1", "dock"))
    store.transition("task_1", TaskState.ASSIGNED, "robot_1")
    with pytest.raises(ValueError, match="different robot"):
        store.transition("task_1", TaskState.ACCEPTED, "robot_2")


def test_invalid_lifecycle_transition_is_rejected():
    store = TaskStore()
    store.add(Task("task_1", "dock"))
    with pytest.raises(ValueError, match="invalid task transition"):
        store.transition("task_1", TaskState.SUCCEEDED, "robot_1")


def test_rejected_task_is_terminal():
    store = TaskStore()
    store.add(Task("task_1", "dock"))
    store.transition("task_1", TaskState.ASSIGNED, "robot_1")
    store.transition("task_1", TaskState.REJECTED, "robot_1", "robot_busy")
    with pytest.raises(ValueError):
        store.transition("task_1", TaskState.ASSIGNED, "robot_2")
