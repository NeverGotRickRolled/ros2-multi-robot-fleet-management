# System Architecture

## Components

1. **Robot registry** stores latest robot telemetry.
2. **Task store** tracks IDs, assignment and lifecycle states.
3. **Task allocator** selects an available robot above the battery threshold.
4. **Fleet manager** queues requests, reserves robots, handles acknowledgements/status and monitors heartbeat freshness.
5. **Robot agent** filters assignments and optionally executes Nav2 `NavigateToPose` goals.
6. **Nav2 stack** is external per-robot infrastructure; it must be launched and configured separately.

## Fleet topics

All fleet messages use JSON in `std_msgs/msg/String` for this MVP.

| Topic | Direction | Purpose |
|---|---|---|
| `/fleet/robot_status` | Robot → fleet | Telemetry and heartbeat |
| `/fleet/task_request` | Client → fleet | Task request |
| `/fleet/task_assignment` | Fleet → robot | Robot-specific assignment |
| `/fleet/task_ack` | Robot → fleet | Accepted/rejected acknowledgement |
| `/fleet/task_status` | Robot → fleet | Lifecycle events |

## Lifecycle

```text
PENDING -> ASSIGNED -> ACCEPTED -> EXECUTING -> SUCCEEDED
                    |             |
                    +-> REJECTED  +-> FAILED
                    |
                    +-> FAILED (heartbeat timeout)
```

The robot agent emits `executing`, `succeeded` and navigation-related `failed` events only when `use_nav2:=true` and a Nav2 action event is received. In acknowledgement-only mode it reports acceptance and remains busy until an external task status event or heartbeat timeout.

## Nav2 goal contract

When Nav2 mode is enabled, `destination` is a JSON-encoded string such as:

```json
{"x":2.0,"y":1.0,"yaw":0.0,"frame_id":"map"}
```

The agent sends a `nav2_msgs/action/NavigateToPose` goal using a `geometry_msgs/msg/PoseStamped`. The action name defaults to relative `navigate_to_pose`, which resolves within the robot's ROS namespace (for example `/robot_1/navigate_to_pose`).

## Operational boundaries

Nav2, localization, mapping, TF, robot controllers, simulation and traffic deconfliction are not launched/configured by this repository. The prototype is not safety-rated. ROS 2 Humble build, action integration, Gazebo simulation and physical robot tests remain required.
