# Robot Agent Interface

## Responsibility boundary

The fleet manager makes an assignment decision. The robot agent validates whether the assignment is addressed to its configured robot ID and whether its local state permits acceptance.

The current agent only acknowledges receipt. It does not drive a robot or claim task completion.

## Message flow

```text
Robot Agent
  |-- /fleet/robot_status (JSON heartbeat) --> Fleet Manager
  |<-- /fleet/task_assignment (JSON) -------- Fleet Manager
  |-- /fleet/task_ack (accepted/rejected) ---> Fleet Manager / observer
  |-- /fleet/task_status (accepted) ---------> Fleet Manager / observer
```

## Multi-instance example

Launch two agents with distinct IDs. Both currently use shared fleet-level topics; the agent filters assignment messages by `robot_id`.

```bash
ros2 run robot_agent robot_agent --ros-args -p robot_id:=robot_1 -p battery_percent:=82.0
ros2 run robot_agent robot_agent --ros-args -p robot_id:=robot_2 -p battery_percent:=64.0
```

## Next integration steps

- Add task acknowledgement subscription to the fleet manager.
- Reserve a robot atomically when an assignment is published.
- Add task accepted / rejected / executing / succeeded / failed states.
- Integrate a Nav2 action client per robot namespace.
- Add heartbeat timeout and stale robot handling.
