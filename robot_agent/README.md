# robot_agent

ROS 2 robot-side fleet agent with optional Nav2 `NavigateToPose` action execution.

## Capabilities

- Publishes periodic telemetry to `/fleet/robot_status`.
- Filters assignments by configured `robot_id`.
- Publishes accepted/rejected acknowledgements.
- Supports optional Nav2 goal execution.
- Publishes `executing`, `succeeded`, or `failed` based on Nav2 action events when Nav2 mode is enabled.
- Returns to available after a successful goal; reports error after a failed goal.

## Parameters

| Parameter | Default | Meaning |
|---|---:|---|
| `robot_id` | `robot_1` | Unique fleet robot ID |
| `battery_percent` | `100.0` | Initial reported battery |
| `heartbeat_period_sec` | `1.0` | Telemetry period |
| `use_nav2` | `false` | Enable actual Nav2 action client |
| `nav2_action_name` | `navigate_to_pose` | Relative action name; resolves within robot namespace |
| `nav2_server_timeout_sec` | `3.0` | Wait for action server before failing the task |

## Build (ROS 2 Humble)

Install Nav2 messages and geometry dependencies, then build from a ROS 2 workspace:

```bash
sudo apt install ros-humble-nav2-msgs ros-humble-geometry-msgs
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## Run

Acknowledgement-only mode (does not move a robot):

```bash
ros2 run robot_agent robot_agent --ros-args -p robot_id:=robot_1
```

Nav2 mode for a robot whose action server is available at `/robot_1/navigate_to_pose`:

```bash
ros2 run robot_agent robot_agent --ros-args \
  -r __ns:=/robot_1 -p robot_id:=robot_1 -p use_nav2:=true
```

Run the second agent in its own namespace and with a distinct robot ID:

```bash
ros2 run robot_agent robot_agent --ros-args \
  -r __ns:=/robot_2 -p robot_id:=robot_2 -p use_nav2:=true
```

The fleet topics are absolute and shared; the Nav2 action name is relative so each agent resolves it inside its namespace.

## Task destination format

With `use_nav2:=true`, send destination as a JSON string containing planar map coordinates:

```json
{
  "task_id": "go_to_loading_bay",
  "destination": "{\"x\": 2.0, \"y\": 1.0, \"yaw\": 0.0, \"frame_id\": \"map\"}",
  "priority": 2
}
```

The `yaw` field is in radians and defaults to zero. Coordinates must be finite numbers. The robot's Nav2 stack must use the same frame and have a valid localization/map setup.

## Important limitations

This is an action-client integration scaffold, not a complete multi-robot deployment. It assumes each robot's Nav2 stack is already launched, localized, and exposes `NavigateToPose`. It does not launch Nav2, create maps, configure localization, resolve named places, or implement fleet-wide traffic deconfliction. Hardware motion and ROS 2 runtime behaviour must be validated on the target robots before operational use.
