# robot_agent

Robot-side ROS 2 node for fleet telemetry and assignment reception.

## Responsibilities in this milestone

- Publishes periodic robot status to `/fleet/robot_status`.
- Listens for assignments on `/fleet/task_assignment`.
- Ignores assignments addressed to other robot IDs.
- Accepts an assignment only while its local state is `available`.
- Publishes receipt acknowledgement on `/fleet/task_ack`.
- Publishes task lifecycle telemetry on `/fleet/task_status`.

## ROS 2 parameters

| Parameter | Default | Meaning |
|---|---:|---|
| `robot_id` | `robot_1` | Unique robot identifier |
| `battery_percent` | `100.0` | Initial simulated battery percentage |
| `heartbeat_period_sec` | `1.0` | Status publication period |

## Run (ROS 2 Humble)

After building the workspace with this package:

```bash
ros2 run robot_agent robot_agent --ros-args -p robot_id:=robot_1 -p battery_percent:=82.0
```

Run another instance in a separate terminal with a different ID:

```bash
ros2 run robot_agent robot_agent --ros-args -p robot_id:=robot_2 -p battery_percent:=64.0
```

## Topic contract

All messages currently use `std_msgs/msg/String` containing JSON. This is an MVP protocol; a later milestone should introduce dedicated ROS 2 interfaces.

- `/fleet/robot_status`: `robot_id`, `status`, `battery_percent`, `current_task_id`
- `/fleet/task_assignment`: `robot_id`, `task_id`, `destination`
- `/fleet/task_ack`: `robot_id`, `task_id`, `state`, optional `reason`
- `/fleet/task_status`: `robot_id`, `task_id`, `state`

## Important limitation

This node acknowledges task receipt but does **not** execute navigation, report task completion, simulate battery drain, or autonomously recover from faults. Nav2 action integration and task completion are future milestones. Do not interpret an acknowledgement as proof that a robot physically completed a task.
