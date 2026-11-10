"""Robot-side fleet agent with optional Nav2 NavigateToPose execution."""
import json

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String

from .protocol import (
    encode_json, make_status_payload, parse_assignment, parse_navigation_goal
)


class RobotAgentNode(Node):
    def __init__(self):
        super().__init__("robot_agent")
        self.declare_parameter("robot_id", "robot_1")
        self.declare_parameter("battery_percent", 100.0)
        self.declare_parameter("heartbeat_period_sec", 1.0)
        self.declare_parameter("use_nav2", False)
        self.declare_parameter("nav2_action_name", "navigate_to_pose")
        self.declare_parameter("nav2_server_timeout_sec", 3.0)

        self.robot_id = str(self.get_parameter("robot_id").value)
        self.battery_percent = float(self.get_parameter("battery_percent").value)
        self.heartbeat_period = float(self.get_parameter("heartbeat_period_sec").value)
        self.use_nav2 = bool(self.get_parameter("use_nav2").value)
        self.nav2_action_name = str(self.get_parameter("nav2_action_name").value)
        self.nav2_timeout = float(
            self.get_parameter("nav2_server_timeout_sec").value
        )
        if not self.robot_id.strip():
            raise ValueError("robot_id parameter must not be empty")
        if not 0.0 <= self.battery_percent <= 100.0:
            raise ValueError("battery_percent parameter must be between 0 and 100")
        if self.heartbeat_period <= 0.0 or self.nav2_timeout <= 0.0:
            raise ValueError("heartbeat and Nav2 timeout parameters must be positive")
        if not self.nav2_action_name.strip():
            raise ValueError("nav2_action_name must not be empty")

        self.status = "available"
        self.current_task_id = ""
        self.active_goal_handle = None

        self.status_pub = self.create_publisher(String, "/fleet/robot_status", 10)
        self.ack_pub = self.create_publisher(String, "/fleet/task_ack", 10)
        self.task_status_pub = self.create_publisher(String, "/fleet/task_status", 10)
        self.assignment_sub = self.create_subscription(
            String, "/fleet/task_assignment", self.assignment_callback, 10
        )
        self.heartbeat_timer = self.create_timer(
            self.heartbeat_period, self.publish_status
        )
        self.nav_client = (
            ActionClient(self, NavigateToPose, self.nav2_action_name)
            if self.use_nav2 else None
        )
        self.publish_status()
        mode = "Nav2 enabled" if self.use_nav2 else "acknowledgement-only mode"
        self.get_logger().info(f"Robot agent {self.robot_id} online ({mode})")

    def publish_status(self):
        payload = make_status_payload(
            self.robot_id, self.status, self.battery_percent, self.current_task_id
        )
        message = String()
        message.data = encode_json(payload)
        self.status_pub.publish(message)

    def publish_task_event(self, publisher, payload):
        message = String()
        message.data = encode_json(payload)
        publisher.publish(message)

    def publish_task_status(self, state, reason=""):
        payload = {
            "robot_id": self.robot_id,
            "task_id": self.current_task_id,
            "state": state,
        }
        if reason:
            payload["reason"] = reason
        self.publish_task_event(self.task_status_pub, payload)

    def _finish_task(self, state, reason=""):
        self.publish_task_status(state, reason)
        self.current_task_id = ""
        self.status = "available" if state == "succeeded" else "error"
        self.active_goal_handle = None
        self.publish_status()

    def assignment_callback(self, message):
        try:
            assignment = parse_assignment(message.data)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.get_logger().warning(f"Ignoring invalid assignment: {exc}")
            return
        if assignment["robot_id"] != self.robot_id:
            return
        if self.status != "available":
            self.publish_task_event(self.ack_pub, {
                "robot_id": self.robot_id,
                "task_id": assignment["task_id"],
                "state": "rejected",
                "reason": f"robot_{self.status}",
            })
            return

        goal = None
        if self.use_nav2:
            try:
                goal = parse_navigation_goal(assignment["destination"])
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.publish_task_event(self.ack_pub, {
                    "robot_id": self.robot_id,
                    "task_id": assignment["task_id"],
                    "state": "rejected",
                    "reason": f"invalid_navigation_goal: {exc}",
                })
                return

        self.status = "busy"
        self.current_task_id = assignment["task_id"]
        self.publish_task_event(self.ack_pub, {
            "robot_id": self.robot_id,
            "task_id": self.current_task_id,
            "state": "accepted",
        })
        self.publish_task_status("accepted")
        self.publish_status()

        if self.use_nav2:
            self._send_navigation_goal(goal)
        else:
            self.get_logger().info(
                f"Accepted {self.current_task_id}; Nav2 is disabled, "
                "so no physical navigation will be attempted."
            )

    def _send_navigation_goal(self, goal_data):
        if not self.nav_client.wait_for_server(timeout_sec=self.nav2_timeout):
            self._finish_task("failed", "nav2_action_server_unavailable")
            self.get_logger().error(
                f"Nav2 action server unavailable: {self.nav2_action_name}"
            )
            return

        goal = NavigateToPose.Goal()
        pose = PoseStamped()
        pose.header.frame_id = goal_data["frame_id"]
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = goal_data["x"]
        pose.pose.position.y = goal_data["y"]
        pose.pose.position.z = 0.0
        pose.pose.orientation.z = goal_data["qz"]
        pose.pose.orientation.w = goal_data["qw"]
        goal.pose = pose

        send_future = self.nav_client.send_goal_async(
            goal, feedback_callback=self._navigation_feedback
        )
        send_future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future):
        try:
            goal_handle = future.result()
        except Exception as exc:  # ROS action transport/runtime failure
            self._finish_task("failed", f"goal_submission_error: {exc}")
            return
        if not goal_handle.accepted:
            self._finish_task("failed", "nav2_goal_rejected")
            return
        self.active_goal_handle = goal_handle
        self.publish_task_status("executing")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._navigation_result_callback)

    def _navigation_feedback(self, feedback_message):
        feedback = feedback_message.feedback
        distance = getattr(feedback, "distance_remaining", None)
        if distance is not None:
            self.get_logger().debug(
                f"{self.current_task_id}: {distance:.2f} m remaining"
            )

    def _navigation_result_callback(self, future):
        try:
            result = future.result()
        except Exception as exc:  # ROS action transport/runtime failure
            self._finish_task("failed", f"navigation_result_error: {exc}")
            return
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self._finish_task("succeeded")
        else:
            self._finish_task("failed", f"nav2_terminal_status_{result.status}")


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
