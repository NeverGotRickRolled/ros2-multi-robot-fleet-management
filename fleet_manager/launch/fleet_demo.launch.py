"""Launch fleet manager and two robot agents.

Set use_nav2:=true only after each robot's Nav2 stack is already running
in its matching namespace and exposes navigate_to_pose.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    use_nav2 = LaunchConfiguration("use_nav2")
    return LaunchDescription([
        DeclareLaunchArgument(
            "use_nav2",
            default_value="false",
            description="Enable NavigateToPose clients; requires external Nav2 stacks",
        ),
        Node(
            package="fleet_manager",
            executable="fleet_manager",
            name="fleet_manager",
            output="screen",
            parameters=[{"minimum_battery_percent": 20.0,
                         "heartbeat_timeout_sec": 5.0}],
        ),
        Node(
            package="robot_agent",
            executable="robot_agent",
            namespace="robot_1",
            name="robot_agent",
            output="screen",
            parameters=[{
                "robot_id": "robot_1",
                "battery_percent": 82.0,
                "use_nav2": ParameterValue(use_nav2, value_type=bool),
                "nav2_action_name": "navigate_to_pose",
            }],
        ),
        Node(
            package="robot_agent",
            executable="robot_agent",
            namespace="robot_2",
            name="robot_agent",
            output="screen",
            parameters=[{
                "robot_id": "robot_2",
                "battery_percent": 64.0,
                "use_nav2": ParameterValue(use_nav2, value_type=bool),
                "nav2_action_name": "navigate_to_pose",
            }],
        ),
    ])
