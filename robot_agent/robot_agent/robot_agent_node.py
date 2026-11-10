"""Robot-side ROS 2 agent: telemetry, assignment reception and acknowledgements.

This first version does not execute navigation. It acknowledges receipt of
assignments and exposes task status so a Nav2 action client can be added later.
"""
import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .protocol import encode_json, make_status_payload, parse_assignment


class RobotAgentNode(Node):
    def __init__(self):
        super().__init__("robot_agent")
        self.declare_parameter("robot_id", "robot_1")
        self.declare_parameter("battery_percent", 100.0)
        self.declare_parameter("heartbeat_period_sec", 1.0)

        self.robot_id = str(self.get_parameter("robot_id").value)
        self.battery_percent = float(self.get_parameter("battery_percent").value)
        self.heartbeat_period = float(
            self.get_parameter("heartbeat_period_sec").value
        )
        if not self.robot_id.strip():
            raise ValueError("robot_id parameter must not be empty")
        if not 0.0 <= self.battery_percent <= 100.0:
            raise ValueError("battery_percent parameter must be between 0 and 100")
        if self.heartbeat_period <= 0.0:
            raise ValueError("heartbeat_period_sec must be greater than zero")

        self.status = "available"
        self.current_task_id = ""

        self.status_pub = self.create_publisher(
            String, "/fleet/robot_status", 10
        )
        self.ack_pub = self.create_publisher(
            String, "/fleet/task_ack", 10
        )
        self.task_status_pub = self.create_publisher(
            String, "/fleet/task_status", 10
        )
        self.assignment_sub = self.create_subscription(
            String, "/fleet/task_assignment", self.assignment_callback, 10
        )
        self.heartbeat_timer = self.create_timer(
            self.heartbeat_period, self.publish_status
        )
        self.publish_status()
        self.get_logger().info(
            f"Robot agent online: {self.robot_id} "
            f"(heartbeat {self.heartbeat_period:.1f}s)"
        )

    def publish_status(self):
        payload = make_status_payload(
            self.robot_id, self.status, self.battery_percent,
            self.current_task_id
        )
        message = String()
        message.data = encode_json(payload)
        self.status_pub.publish(message)

    def publish_task_event(self, publisher, payload):
        message = String()
        message.data = encode_json(payload)
        publisher.publish(message)

    def assignment_callback(self, message):
        try:
            assignment = parse_assignment(message.data)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.get_logger().warning(f"Ignoring invalid assignment: {exc}")
            return

        if assignment["robot_id"] != self.robot_id:
            return

        if self.status != "available":
            self.get_logger().warning(
                f"Cannot accept {assignment['task_id']}: robot status is {self.status}"
            )
            self.publish_task_event(self.ack_pub, {
                "robot_id": self.robot_id,
                "task_id": assignment["task_id"],
                "state": "rejected",
                "reason": f"robot_{self.status}",
            })
            return

        self.status = "busy"
        self.current_task_id = assignment["task_id"]
        self.publish_task_event(self.ack_pub, {
            "robot_id": self.robot_id,
            "task_id": self.current_task_id,
            "state": "accepted",
        })
        self.publish_task_event(self.task_status_pub, {
            "robot_id": self.robot_id,
            "task_id": self.current_task_id,
            "state": "accepted",
        })
        self.publish_status()
        self.get_logger().info(
            f"Accepted task {self.current_task_id}: {assignment['destination']}. "
            "Navigation execution is not implemented yet."
        )


def main(args=None):
    rclpy.init(args=args)
    node = RobotAgentNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
