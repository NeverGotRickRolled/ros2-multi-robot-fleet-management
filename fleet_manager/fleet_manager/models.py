"""Small domain models used by the fleet registry and allocator."""
from dataclasses import dataclass
from enum import Enum


class RobotStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class RobotState:
    robot_id: str
    status: RobotStatus = RobotStatus.OFFLINE
    battery_percent: float = 0.0
    current_task_id: str = ""

    def __post_init__(self):
        if not self.robot_id.strip():
            raise ValueError("robot_id must not be empty")
        if not 0.0 <= self.battery_percent <= 100.0:
            raise ValueError("battery_percent must be between 0 and 100")


@dataclass(frozen=True)
class Task:
    task_id: str
    destination: str
    priority: int = 0

    def __post_init__(self):
        if not self.task_id.strip():
            raise ValueError("task_id must not be empty")
        if not self.destination.strip():
            raise ValueError("destination must not be empty")
