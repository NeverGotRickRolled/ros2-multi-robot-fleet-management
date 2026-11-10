"""ROS 2 adapter for the fleet registry and allocator.

MVP wire format: JSON strings on /fleet/robot_status and /fleet/task_request.
Assignments are published on /fleet/task_assignment.
"""
import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .allocator import TaskAllocator
from .models import RobotState, RobotStatus, Task
from .registry import RobotRegistry


class FleetManagerNode(Node):
    def __init__(self):
        super().__init__("fleet_manager")
        self.declare_parameter("minimum_battery_percent", 20.0)
        minimum_battery = float(self.get_parameter("minimum_battery_percent").value)
        self.registry = RobotRegistry()
        self.allocator = TaskAllocator(self.registry, minimum_battery)

        self.status_sub = self.create_subscription(
            String, "/fleet/robot_status", self.robot_status_callback, 10
        )
        self.task_sub = self.create_subscription(
            String, "/fleet/task_request", self.task_request_callback, 10
        )
        self.assignment_pub = self.create_publisher(
            String, "/fleet/task_assignment", 10
        )
        self.get_logger().info("Fleet manager started; awaiting robot status.")

    def robot_status_callback(self, message):
        try:
            payload = json.loads(message.data)
            state = RobotState(
                robot_id=str(payload["robot_id"]),
                status=RobotStatus(payload["status"]),
                battery_percent=float(payload["battery_percent"]),
                current_task_id=str(payload.get("current_task_id", "")),
            )
            self.registry.update(state)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.get_logger().warning(f"Ignoring invalid robot status: {exc}")

    def task_request_callback(self, message):
        try:
            payload = json.loads(message.data)
            task = Task(
                task_id=str(payload["task_id"]),
                destination=str(payload["destination"]),
                priority=int(payload.get("priority", 0)),
            )
            robot = self.allocator.select_robot(task)
            if robot is None:
                self.get_logger().warning(
                    f"No eligible robot available for task {task.task_id}"
                )
                return
            assignment = String()
            assignment.data = json.dumps({
                "robot_id": robot.robot_id,
                "task_id": task.task_id,
                "destination": task.destination,
            })
            self.assignment_pub.publish(assignment)
            robot.status = RobotStatus.BUSY
            robot.current_task_id = task.task_id
            self.registry.update(robot)
            self.get_logger().info(f"Assigned task {task.task_id} to {robot.robot_id}")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.get_logger().warning(f"Ignoring invalid task request: {exc}")


def main(args=None):
    rclpy.init(args=args)
    node = FleetManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
