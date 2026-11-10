"""In-memory registry of the most recently reported robot states."""
from typing import Dict, List, Optional

from .models import RobotState


class RobotRegistry:
    def __init__(self):
        self._robots: Dict[str, RobotState] = {}

    def update(self, state: RobotState) -> None:
        self._robots[state.robot_id] = state

    def get(self, robot_id: str) -> Optional[RobotState]:
        return self._robots.get(robot_id)

    def all(self) -> List[RobotState]:
        return list(self._robots.values())
