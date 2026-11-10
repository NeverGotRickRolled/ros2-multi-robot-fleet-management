# Robot Agent and Nav2 Integration

## Responsibility boundary

The fleet manager allocates tasks and tracks protocol state. Each robot agent owns its local Nav2 action client and reports action outcomes. Nav2 itself must already be running for that robot.

## Message flow

```text
Client -> /fleet/task_request -> Fleet Manager
Fleet Manager -> /fleet/task_assignment -> Robot Agent
Robot Agent -> /fleet/task_ack -> Fleet Manager
Robot Agent -> /fleet/task_status (accepted/executing/succeeded/failed)
Robot Agent -> /fleet/robot_status (heartbeat and availability)
```

## Namespace model

Use one robot namespace per agent, such as `/robot_1` and `/robot_2`. Fleet topics remain absolute and shared. The Nav2 action name is relative (`navigate_to_pose`), so the agent in namespace `/robot_1` connects to `/robot_1/navigate_to_pose`.

Example:

```bash
ros2 run robot_agent robot_agent --ros-args -r __ns:=/robot_1 -p robot_id:=robot_1 -p use_nav2:=true
```

## Destination contract

In Nav2 mode, `destination` is a JSON-encoded string:

```json
{"x":2.0,"y":1.0,"yaw":0.0,"frame_id":"map"}
```

The agent converts planar x/y/yaw into a `geometry_msgs/msg/PoseStamped` and sends a `nav2_msgs/action/NavigateToPose` goal. Yaw is radians. The Nav2 map/localization frame must match `frame_id`.

## State semantics

- `accepted`: the agent accepted the assignment.
- `executing`: the Nav2 action goal was submitted; it is not a guarantee of physical motion.
- `succeeded`: Nav2 returned `STATUS_SUCCEEDED`.
- `failed`: the server was unavailable, rejected the goal, or returned a non-success terminal result.

## Limitations

No launch orchestration for Nav2, map server, AMCL, robot_state_publisher, controllers, or simulation is included. No named-location database or traffic conflict manager is included. Validate action names, namespaces, TF, map frame, localization and velocity controller on the target ROS 2 Humble system before testing motion.
