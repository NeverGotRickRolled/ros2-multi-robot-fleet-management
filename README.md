# ROS 2 Multi-Robot Fleet Management

[![CI: Python tests and ROS 2 Humble build](https://github.com/NeverGotRickRolled/ros2-multi-robot-fleet-management/actions/workflows/python-tests.yml/badge.svg)](https://github.com/NeverGotRickRolled/ros2-multi-robot-fleet-management/actions/workflows/python-tests.yml)

A ROS 2 portfolio project demonstrating a multi-robot fleet manager, battery-aware task allocation, robot telemetry, task lifecycle tracking, heartbeat monitoring, and an optional Nav2 `NavigateToPose` action client.

> **Verification:** Python unit tests, Python syntax checks, and a ROS 2 Humble colcon build pass in GitHub Actions. The Nav2 action client has not yet been exercised against a live Nav2 server. Gazebo simulation and physical robot behaviour have not been tested.

## Project goals

A fleet manager should be able to monitor multiple robots, select a suitable robot for a task, dispatch that task, and track the robot's reported progress. This repository implements the fleet coordination layer and a robot-side ROS 2 agent. Navigation is an optional integration boundary provided by Nav2.

## Architecture

```text
                         /fleet/task_request
 Task Client ------------------------------------+
                                                  v
                                          +---------------+
 Robot 1 -- /fleet/robot_status --------> |               |
 Robot 2 -- /fleet/robot_status --------> | Fleet Manager |
                                          |               |
                                          | Registry      |
                                          | Allocator     |
                                          | Task Store    |
                                          | Heartbeat     |
                                          +-------+-------+
                                                  |
                                      /fleet/task_assignment
                                         /               \
                                        v                 v
                                  Robot Agent 1      Robot Agent 2
                                        |                 |
                                  Nav2 Action       Nav2 Action
                                  (optional)         (optional)
```

See [system architecture](docs/ARCHITECTURE.md) and [robot agent / Nav2 integration](docs/ROBOT_AGENT.md) for details.

## Implemented capabilities

- **Robot registry:** tracks robot ID, availability, battery percentage, and current task.
- **Battery-aware allocation:** selects an available robot above a configurable battery threshold, with deterministic tie-breaking.
- **Task queue:** prioritizes higher-priority tasks and protects against duplicate task IDs.
- **Task lifecycle:** validates assignment, acceptance, execution, success, failure, and rejection transitions.
- **Reservation before dispatch:** marks a selected robot busy before publishing its assignment.
- **Heartbeat monitoring:** marks stale robots offline and fails their active task with a timeout reason.
- **Robot agent:** publishes telemetry, filters assignments by robot ID, and acknowledges accepted or rejected work.
- **Optional Nav2 client:** converts a planar destination into a `NavigateToPose` goal and reports action outcomes.
- **Automated checks:** Python tests, syntax checks, and a ROS 2 Humble package build run in GitHub Actions.

## Repository layout

```text
fleet_manager/   Fleet registry, allocator, task store, ROS 2 node and launch file
robot_agent/     Robot-side telemetry, assignment protocol and optional Nav2 client
docs/            Architecture, robot agent integration, roadmap and verification plan
.github/         Python test and ROS 2 Humble build workflow
```

## ROS 2 interfaces

All fleet-level messages currently use JSON strings in `std_msgs/msg/String`.

| Topic | Direction | Purpose |
|---|---|---|
| `/fleet/robot_status` | Robot → fleet | Robot telemetry and heartbeat |
| `/fleet/task_request` | Client → fleet | New task request |
| `/fleet/task_assignment` | Fleet → robots | Assignment broadcast; each agent filters by robot ID |
| `/fleet/task_ack` | Robot → fleet | Assignment accepted or rejected |
| `/fleet/task_status` | Robot → fleet | Task lifecycle updates |

### Task lifecycle

```text
PENDING -> ASSIGNED -> ACCEPTED -> EXECUTING -> SUCCEEDED
                    |             |
                    +-> REJECTED  +-> FAILED

Heartbeat timeout can fail an active task.
```

### Nav2 destination format

When `use_nav2:=true`, the task's `destination` field must contain JSON like:

```json
{"x": 2.0, "y": 1.0, "yaw": 0.0, "frame_id": "map"}
```

Coordinates are metres in the configured Nav2 global frame; yaw is in radians. The action name defaults to relative `navigate_to_pose`, resolving within each robot namespace (for example, `/robot_1/navigate_to_pose`). Each robot's Nav2 stack must already be running.

## Build and run

Target environment: **Ubuntu 22.04 + ROS 2 Humble**.

Install the additional message dependencies:

```bash
sudo apt update
sudo apt install ros-humble-nav2-msgs ros-humble-geometry-msgs
```

Place `fleet_manager` and `robot_agent` in the `src` directory of a ROS 2 workspace, then build:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Launch the fleet manager and two namespaced example agents in acknowledgement-only mode:

```bash
ros2 launch fleet_manager fleet_demo.launch.py
```

Enable the Nav2 clients only after separate Nav2 stacks are running in both robot namespaces:

```bash
ros2 launch fleet_manager fleet_demo.launch.py use_nav2:=true
```

The launch file starts the fleet manager and two agents. It does **not** spawn robot models, launch Nav2, start Gazebo, or configure maps and localization.

## Run the Python tests without ROS 2

```bash
cd fleet_manager
PYTHONPATH=. pytest -q test

cd ../robot_agent
PYTHONPATH=. pytest -q test
```

For the staged integration and simulation checklist, see [TESTING.md](docs/TESTING.md).

## Current limitations

- Fleet messages are JSON strings rather than custom typed ROS interfaces.
- Robot and task state is in memory; persistence and restart recovery are not implemented.
- No task cancellation or automatic reassignment/retry workflow is implemented.
- Nav2, mapping, localization, TF, robot controllers, and Gazebo are external and must be configured separately.
- Multi-robot traffic deconfliction and shared-zone coordination are not implemented.
- No live Nav2, Gazebo, or physical robot test has been completed.

This is a development and learning prototype, not a safety-rated industrial fleet controller. Validate in simulation before commanding hardware motion.
