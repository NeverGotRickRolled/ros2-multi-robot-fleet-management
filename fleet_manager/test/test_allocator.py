import pytest

from fleet_manager.allocator import TaskAllocator
from fleet_manager.models import RobotState, RobotStatus, Task
from fleet_manager.registry import RobotRegistry


def robot(robot_id, status, battery):
    return RobotState(robot_id, RobotStatus(status), battery)


def test_selects_highest_battery_available_robot():
    registry = RobotRegistry()
    registry.update(robot("robot_1", "available", 55))
    registry.update(robot("robot_2", "available", 82))
    registry.update(robot("robot_3", "busy", 99))
    selected = TaskAllocator(registry).select_robot(Task("task_1", "dock"))
    assert selected.robot_id == "robot_2"


def test_excludes_low_battery_robot():
    registry = RobotRegistry()
    registry.update(robot("robot_1", "available", 15))
    assert TaskAllocator(registry, 20).select_robot(Task("task_1", "dock")) is None


def test_excludes_busy_and_offline_robots():
    registry = RobotRegistry()
    registry.update(robot("robot_1", "busy", 95))
    registry.update(robot("robot_2", "offline", 90))
    assert TaskAllocator(registry).select_robot(Task("task_1", "dock")) is None


def test_tie_break_is_deterministic():
    registry = RobotRegistry()
    registry.update(robot("robot_2", "available", 70))
    registry.update(robot("robot_1", "available", 70))
    selected = TaskAllocator(registry).select_robot(Task("task_1", "dock"))
    assert selected.robot_id == "robot_1"


def test_robot_battery_must_be_in_range():
    import pytest
    with pytest.raises(ValueError):
        robot("robot_1", "available", 120)
