# System Architecture

## Logical components

1. **Robot registry** stores each robot's latest telemetry and current availability.
2. **Task store** tracks task IDs, assigned robot IDs, lifecycle states and failure reasons.
3. **Task allocator** selects an available robot meeting the minimum battery threshold.
4. **Fleet manager ROS 2 node** accepts requests, reserves robots, publishes assignments, consumes acknowledgements/status, and monitors heartbeat freshness.
5. **Robot agents** publish telemetry and acknowledge assignment receipt. Navigation execution is not implemented yet.
6. **Navigation integration** is planned through per-robot Nav2 action clients.

## ROS 2 topic interface (JSON over std_msgs/msg/String)

| Topic | Direction | Purpose |
|---|---|---|
| `/fleet/robot_status` | Robot → fleet | Robot telemetry and heartbeat |
| `/fleet/task_request` | Client → fleet | New task request |
| `/fleet/task_assignment` | Fleet → robot | Assignment for a specific robot |
| `/fleet/task_ack` | Robot → fleet | Assignment accepted or rejected |
| `/fleet/task_status` | Robot → fleet | Accepted, executing, succeeded or failed status |

Example status:

```json
{"robot_id":"robot_1","status":"available","battery_percent":78.5,"current_task_id":""}
```

Example task request:

```json
{"task_id":"move_001","destination":"loading_bay","priority":2}
```

## Task lifecycle

```text
PENDING -> ASSIGNED -> ACCEPTED -> EXECUTING -> SUCCEEDED
                    |             |
                    +-> REJECTED  +-> FAILED
                    |
                    +-> FAILED (e.g. robot heartbeat timeout)
```

- Duplicate task IDs are rejected by the in-memory task store.
- Pending tasks are considered in descending priority order, then task ID.
- The manager reserves a robot as busy before publishing the assignment.
- Acknowledgements and task status are accepted only from the robot assigned to that task.
- Robots without a fresh heartbeat are marked offline after the configurable timeout (default 5 seconds).
- A heartbeat timeout fails that robot's active task with reason `heartbeat_timeout`.
- Terminal task states are `succeeded`, `failed`, and `rejected`.

## Allocation policy (MVP)

- Only robots with status `available` are eligible.
- Robots below the configured minimum battery percentage are excluded (default 20%).
- The eligible robot with the highest battery is selected.
- Equal battery values are resolved by robot ID for deterministic behaviour.
- If no robot is eligible, tasks remain pending and are reconsidered when a robot reports status.

## Current limitations

The robot agent currently acknowledges assignment receipt only. It does not send `executing`, `succeeded`, or `failed` based on navigation, because no navigation executor exists yet. Those states are supported by the fleet protocol/store for the future Nav2 integration. Heartbeat freshness uses the ROS node clock. The task store and registry are in-memory and are lost when the process restarts. This prototype is not safety-rated.
