# ROS 2 Multi-Robot Fleet Management

A portfolio prototype for multi-robot task allocation, telemetry, task lifecycle tracking, heartbeat monitoring, and optional Nav2 goal execution.

> **Verification status:** Pure Python unit tests and syntax checks run in GitHub Actions. ROS 2 Humble build, Nav2 action-server integration, Gazebo simulation, and physical robot behaviour have not yet been verified.

## Architecture

```text
Task Client -> Fleet Manager -> Assignment -> Robot Agent
                  |                            |
            Robot Registry                Nav2 Action Client
            Task Lifecycle                 (optional)
            Battery Allocator                   |
            Heartbeat Monitor               Nav2 Stack
```

## Implemented

- Battery-aware deterministic robot allocation.
- Task queue with priority ordering and duplicate task ID protection.
- Validated lifecycle states and assignment acknowledgement handling.
- Robot heartbeat monitoring and offline detection.
- Robot agent telemetry and assignment filtering.
- Optional `NavigateToPose` action client in each robot namespace.
- Pure Python unit tests and GitHub Actions CI.

## Task destination for Nav2

With `use_nav2:=true`, a task destination is a JSON-encoded string:

```json
{"x":2.0,"y":1.0,"yaw":0.0,"frame_id":"map"}
```

Coordinates are in the robot's configured Nav2 global frame (normally `map`); yaw is radians. Each robot's Nav2 stack must already be running and expose `/robot_N/navigate_to_pose`.

## Build dependencies (Ubuntu 22.04 / ROS 2 Humble)

```bash
sudo apt update
sudo apt install ros-humble-nav2-msgs ros-humble-geometry-msgs
```

Place both packages in a ROS 2 workspace, source Humble, then:

```bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Launch the fleet manager and two example agents together (acknowledgement-only mode):

```bash
ros2 launch fleet_manager fleet_demo.launch.py
```

Enable Nav2 clients only after the Nav2 stacks are already running in both robot namespaces:

```bash
ros2 launch fleet_manager fleet_demo.launch.py use_nav2:=true
```

Run a single agent manually in a robot namespace with Nav2 enabled:

```bash
ros2 run robot_agent robot_agent --ros-args -r __ns:=/robot_1 -p robot_id:=robot_1 -p use_nav2:=true
```

A second agent uses `/robot_2`. Fleet topics are shared absolute topics; Nav2 action names are relative to each robot namespace.

## Pure Python tests (no ROS 2 required)

```bash
cd fleet_manager && PYTHONPATH=. pytest -q test
cd ../robot_agent && PYTHONPATH=. pytest -q test
```

## Limitations and safety

This repository does not launch or configure Nav2, mapping, localization, TF, robot controllers, Gazebo, or multi-robot traffic management. Named destinations, persistent task storage, recovery after process restart and safety-rated coordination are not implemented. This is a development prototype, not an industrial safety controller. Validate on simulation before any hardware motion.
