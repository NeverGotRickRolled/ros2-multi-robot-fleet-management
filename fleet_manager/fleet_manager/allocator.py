"""Deterministic task-to-robot allocation policy."""
from typing import Optional

from .models import RobotState, RobotStatus, Task
from .registry import RobotRegistry


class TaskAllocator:
    def __init__(self, registry: RobotRegistry, minimum_battery: float = 20.0):
        if not 0.0 <= minimum_battery <= 100.0:
            raise ValueError("minimum_battery must be between 0 and 100")
        self.registry = registry
        self.minimum_battery = minimum_battery

    def select_robot(self, task: Task) -> Optional[RobotState]:
        """Choose the eligible robot with the highest battery.

        Ties are resolved by robot_id for deterministic behaviour.
        The task argument is reserved for future task-aware cost functions.
        """
        del task
        candidates = [
            robot for robot in self.registry.all()
            if robot.status == RobotStatus.AVAILABLE
            and robot.battery_percent >= self.minimum_battery
        ]
        if not candidates:
            return None
        return sorted(
            candidates, key=lambda robot: (-robot.battery_percent, robot.robot_id)
        )[0]
