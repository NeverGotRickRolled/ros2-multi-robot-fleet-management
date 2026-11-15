# System Architecture

## System boundary

The repository implements the fleet coordination layer and a robot-side ROS 2 agent. Navigation is an optional integration with an independently running Nav2 stack. Simulation, robot description, localization, and low-level control are external dependencies.

## Components

1. **Robot registry** stores the latest telemetry for each robot.
2. **Task store** tracks task IDs, assignment ownership, lifecycle state, and failure reason in memory.
3. **Task allocator** selects an available robot that meets the configured minimum battery threshold.
4. **Fleet manager** queues requests, reserves robots, publishes assignments, handles acknowledgements and status events, and monitors heartbeat freshness.
5. **Robot agent** publishes telemetry, filters assignments by robot ID, acknowledges work, and optionally owns a local Nav2 action client.
6. **Nav2 stack** is external per-robot infrastructure and must be launched and configured separately.

## Fleet topics

All fleet messages currently use JSON encoded in `std_msgs/msg/String`.

| Topic | Direction | Purpose |
|---|---|---|
| `/fleet/robot_status` | Robot → fleet | Telemetry and heartbeat |
| `/fleet/task_request` | Client → fleet | Task request |
| `/fleet/task_assignment` | Fleet → robots | Robot-specific assignment broadcast |
| `/fleet/task_ack` | Robot → fleet | Accepted/rejected acknowledgement |
| `/fleet/task_status` | Robot → fleet | Lifecycle events |

## Task lifecycle

```text
PENDING -> ASSIGNED -> ACCEPTED -> EXECUTING -> SUCCEEDED
                    |             |
                    +-> REJECTED  +-> FAILED
                    |
                    +-> FAILED (heartbeat timeout)
```

The fleet manager validates task ownership before accepting acknowledgements or status updates. It reserves a selected robot as busy before publishing an assignment. A rejected assignment frees the robot and leaves the task in the rejected state.

In acknowledgement-only mode, an agent accepts a task but does not navigate; it remains busy until an external task status event or heartbeat timeout. In Nav2 mode, the agent reports `executing` after the Nav2 action server accepts the goal and reports a terminal result when the action completes.

## Nav2 goal contract

When Nav2 mode is enabled, `destination` is a JSON-encoded string such as:

```json
{"x":2.0,"y":1.0,"yaw":0.0,"frame_id":"map"}
```

The agent converts planar x/y/yaw into a `geometry_msgs/msg/PoseStamped` and sends a `nav2_msgs/action/NavigateToPose` goal. The action name defaults to relative `navigate_to_pose`, which resolves within the robot's ROS namespace (for example `/robot_1/navigate_to_pose`).

## Verification status

GitHub Actions currently passes the Python unit tests, Python syntax checks, and ROS 2 Humble colcon build. The Nav2 action client has not yet been validated against a live action server. No Gazebo simulation or physical robot test has been completed.

## Operational boundaries

Nav2, localization, mapping, TF, robot controllers, simulation, and traffic deconfliction are not launched or configured by this repository. Task state is in memory and is lost on process restart. The prototype is not safety-rated; validate action names, namespaces, TF, map frame, localization, and velocity control in simulation before testing motion on hardware.
