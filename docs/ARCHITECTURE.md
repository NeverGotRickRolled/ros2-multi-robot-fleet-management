# System Architecture

## Logical components

1. **Robot registry** stores the latest reported state for each robot.
2. **Task allocator** selects an eligible robot using availability and battery level.
3. **Fleet manager ROS 2 node** adapts ROS 2 topic messages to the domain logic.
4. **Robot agents** (planned) will report telemetry and execute assigned work.
5. **Navigation integration** (planned) will dispatch goals through Nav2 actions.

## Initial ROS 2 interface

| Topic | Type | Direction | Purpose |
|---|---|---|---|
| `/fleet/robot_status` | `std_msgs/msg/String` | Robot → fleet | JSON robot telemetry |
| `/fleet/task_request` | `std_msgs/msg/String` | Client → fleet | JSON task request |
| `/fleet/task_assignment` | `std_msgs/msg/String` | Fleet → robot | JSON task assignment |

Example robot status:

```json
{"robot_id":"robot_1","status":"available","battery_percent":78.5,"current_task_id":""}
```

Example task request:

```json
{"task_id":"move_001","destination":"loading_bay","priority":2}
```

Example assignment:

```json
{"robot_id":"robot_1","task_id":"move_001","destination":"loading_bay"}
```

## Allocation policy (MVP)

- Only robots with status `available` are eligible.
- Robots below the configured minimum battery percentage are excluded.
- The eligible robot with the highest battery is selected.
- Equal battery values are resolved by robot ID for deterministic behaviour.
- If no robot is eligible, the task is not assigned.

This baseline does not yet account for travel distance, task priority, robot capabilities, charging, traffic conflicts, or completion acknowledgement.
