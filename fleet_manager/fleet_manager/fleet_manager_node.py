"""ROS 2 adapter for fleet registration, task dispatch and lifecycle tracking.

MVP wire format: JSON strings on fleet topics. Navigation execution is not
implemented; task states reflect protocol events, not physical motion.
"""
import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .allocator import TaskAllocator
from .models import RobotState, RobotStatus, Task
from .registry import RobotRegistry
from .task_store import TaskState, TaskStore


class FleetManagerNode(Node):
    def __init__(self):
        super().__init__("fleet_manager")
        self.declare_parameter("minimum_battery_percent", 20.0)
        self.declare_parameter("heartbeat_timeout_sec", 5.0)
        minimum_battery = float(self.get_parameter("minimum_battery_percent").value)
        self.heartbeat_timeout = float(
            self.get_parameter("heartbeat_timeout_sec").value
        )
        if self.heartbeat_timeout <= 0.0:
            raise ValueError("heartbeat_timeout_sec must be greater than zero")

        self.registry = RobotRegistry()
        self.allocator = TaskAllocator(self.registry, minimum_battery)
        self.tasks = TaskStore()
        self.last_seen = {}

        self.status_sub = self.create_subscription(
            String, "/fleet/robot_status", self.robot_status_callback, 10
        )
        self.task_sub = self.create_subscription(
            String, "/fleet/task_request", self.task_request_callback, 10
        )
        self.ack_sub = self.create_subscription(
            String, "/fleet/task_ack", self.task_ack_callback, 10
        )
        self.task_status_sub = self.create_subscription(
            String, "/fleet/task_status", self.task_status_callback, 10
        )
        self.assignment_pub = self.create_publisher(
            String, "/fleet/task_assignment", 10
        )
        self.create_timer(1.0, self.check_heartbeat_timeouts)
        self.get_logger().info("Fleet manager started; awaiting robot status.")

    def _now_seconds(self):
        return self.get_clock().now().nanoseconds / 1_000_000_000.0

    def _decode(self, message, label):
        try:
            payload = json.loads(message.data)
            if not isinstance(payload, dict):
                raise ValueError("payload must be a JSON object")
            return payload
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self.get_logger().warning(f"Ignoring invalid {label}: {exc}")
            return None

    def robot_status_callback(self, message):
        payload = self._decode(message, "robot status")
        if payload is None:
            return
        try:
            state = RobotState(
                robot_id=str(payload["robot_id"]),
                status=RobotStatus(payload["status"]),
                battery_percent=float(payload["battery_percent"]),
                current_task_id=str(payload.get("current_task_id", "")),
            )
            existing = self.registry.get(state.robot_id)
            # A queued pre-assignment AVAILABLE heartbeat must not undo a
            # reservation made by the fleet manager.
            if (
                existing is not None
                and existing.status == RobotStatus.BUSY
                and existing.current_task_id
                and state.status == RobotStatus.AVAILABLE
                and not state.current_task_id
            ):
                state.status = RobotStatus.BUSY
                state.current_task_id = existing.current_task_id
            self.registry.update(state)
            self.last_seen[state.robot_id] = self._now_seconds()
            self.dispatch_pending_tasks()
        except (KeyError, TypeError, ValueError) as exc:
            self.get_logger().warning(f"Ignoring invalid robot status: {exc}")

    def task_request_callback(self, message):
        payload = self._decode(message, "task request")
        if payload is None:
            return
        try:
            task = Task(
                task_id=str(payload["task_id"]),
                destination=str(payload["destination"]),
                priority=int(payload.get("priority", 0)),
            )
            self.tasks.add(task)
            self.get_logger().info(f"Queued task {task.task_id}")
            self.dispatch_pending_tasks()
        except (KeyError, TypeError, ValueError) as exc:
            self.get_logger().warning(f"Ignoring task request: {exc}")

    def dispatch_pending_tasks(self):
        pending = sorted(
            self.tasks.pending(),
            key=lambda record: (-record.task.priority, record.task.task_id),
        )
        for record in pending:
            robot = self.allocator.select_robot(record.task)
            if robot is None:
                break

            # Reserve in local state before publishing to prevent duplicate dispatch.
            robot.status = RobotStatus.BUSY
            robot.current_task_id = record.task.task_id
            self.registry.update(robot)
            self.tasks.transition(
                record.task.task_id, TaskState.ASSIGNED, robot.robot_id
            )
            assignment = String()
            assignment.data = json.dumps({
                "robot_id": robot.robot_id,
                "task_id": record.task.task_id,
                "destination": record.task.destination,
            })
            self.assignment_pub.publish(assignment)
            self.get_logger().info(
                f"Assigned task {record.task.task_id} to {robot.robot_id}"
            )

    def task_ack_callback(self, message):
        payload = self._decode(message, "task acknowledgement")
        if payload is None:
            return
        try:
            robot_id = str(payload["robot_id"])
            task_id = str(payload["task_id"])
            state = str(payload["state"])
            record = self.tasks.get(task_id)
            if record is None or record.robot_id != robot_id:
                self.get_logger().warning(
                    f"Ignoring acknowledgement for unknown/mismatched task {task_id}"
                )
                return
            if state == "accepted":
                self.tasks.transition(task_id, TaskState.ACCEPTED, robot_id)
            elif state == "rejected":
                self.tasks.transition(
                    task_id, TaskState.REJECTED, robot_id,
                    str(payload.get("reason", "robot_rejected")),
                )
            else:
                raise ValueError(f"unsupported acknowledgement state: {state}")
            self.get_logger().info(f"Task {task_id} acknowledgement: {state}")
        except (KeyError, TypeError, ValueError) as exc:
            self.get_logger().warning(f"Ignoring invalid task acknowledgement: {exc}")

    def task_status_callback(self, message):
        payload = self._decode(message, "task status")
        if payload is None:
            return
        try:
            robot_id = str(payload["robot_id"])
            task_id = str(payload["task_id"])
            state = TaskState(str(payload["state"]))
            record = self.tasks.get(task_id)
            if record is None or record.robot_id != robot_id:
                self.get_logger().warning(
                    f"Ignoring status for unknown/mismatched task {task_id}"
                )
                return
            self.tasks.transition(
                task_id, state, robot_id, str(payload.get("reason", ""))
            )
            if state in {TaskState.SUCCEEDED, TaskState.FAILED}:
                robot = self.registry.get(robot_id)
                if robot is not None and robot.current_task_id == task_id:
                    robot.status = RobotStatus.AVAILABLE
                    robot.current_task_id = ""
                    self.registry.update(robot)
                self.dispatch_pending_tasks()
            self.get_logger().info(f"Task {task_id} status: {state.value}")
        except (KeyError, TypeError, ValueError) as exc:
            self.get_logger().warning(f"Ignoring invalid task status: {exc}")

    def check_heartbeat_timeouts(self):
        now = self._now_seconds()
        for robot_id, last_seen in list(self.last_seen.items()):
            if now - last_seen <= self.heartbeat_timeout:
                continue
            robot = self.registry.get(robot_id)
            if robot is None or robot.status == RobotStatus.OFFLINE:
                continue
            task_id = robot.current_task_id
            robot.status = RobotStatus.OFFLINE
            robot.current_task_id = ""
            self.registry.update(robot)
            if task_id:
                record = self.tasks.get(task_id)
                if record and record.state not in {
                    TaskState.SUCCEEDED, TaskState.FAILED, TaskState.REJECTED
                }:
                    self.tasks.transition(
                        task_id, TaskState.FAILED, robot_id, "heartbeat_timeout"
                    )
            self.get_logger().warning(
                f"Robot {robot_id} heartbeat timed out; marked offline"
            )


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
