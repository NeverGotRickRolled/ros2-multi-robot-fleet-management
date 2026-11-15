# Verification and Simulation Test Plan

This document is the planned validation sequence. A test is not considered complete until its result has been observed and recorded.

## 1. Automated checks (completed in GitHub Actions)

- [x] Fleet manager Python unit tests
- [x] Robot agent protocol unit tests
- [x] Python syntax compilation
- [x] ROS 2 Humble colcon build

See the [GitHub Actions workflow](../.github/workflows/python-tests.yml) for the reproducible CI steps.

## 2. ROS 2 runtime integration (pending)

Environment: Ubuntu 22.04, ROS 2 Humble.

1. Build both packages in a clean workspace.
2. Launch the example fleet:
   ```bash
   ros2 launch fleet_manager fleet_demo.launch.py
   ```
3. Inspect the fleet topics:
   ```bash
   ros2 topic list
   ros2 topic echo /fleet/robot_status
   ros2 topic echo /fleet/task_assignment
   ```
4. Publish a task request from a separate terminal:
   ```bash
   ros2 topic pub --once /fleet/task_request std_msgs/msg/String \
     "{data: '{\"task_id\":\"task_001\",\"destination\":\"demo_station\",\"priority\":1}'}"
   ```
5. Confirm that one available robot is reserved and receives the assignment.
6. Confirm the task acknowledgement and verify that the other robot remains available.
7. Stop one agent and confirm that its heartbeat timeout is detected.

Record the exact commands, terminal output, ROS distribution, package versions, and any failures.

## 3. Nav2 integration (pending)

Prerequisites for each robot namespace:

- A running Nav2 stack exposing `navigate_to_pose`.
- A valid map and localization source.
- Correct TF tree and global frame.
- A configured controller and velocity command path.
- Robot footprint and navigation parameters appropriate to the platform.

Then launch the fleet with:

```bash
ros2 launch fleet_manager fleet_demo.launch.py use_nav2:=true
```

Submit a destination encoded as JSON with numeric `x`, `y`, optional `yaw` in radians, and optional `frame_id`. Verify action acceptance, execution status, terminal result, and robot status reset. Test unavailable server, rejected goal, invalid destination, and navigation failure cases.

## 4. Gazebo multi-robot simulation (pending)

Required assets and configuration:

- Robot URDF or Xacro with a valid footprint and sensor/control interfaces.
- Gazebo-compatible robot model and spawn configuration.
- World file with obstacles and navigation space.
- Per-robot namespaces, TF frames, and Nav2 parameter files.
- Map/localization and controller configuration for each robot.

Validation scenarios:

1. Spawn two robots with unique namespaces.
2. Confirm both agents publish distinct robot IDs and telemetry.
3. Submit two tasks and verify deterministic allocation.
4. Observe each robot navigating to its assigned goal.
5. Submit simultaneous goals in the same area and observe whether the current system exposes traffic conflicts (traffic deconfliction is not implemented).
6. Record success/failure outcomes and known limitations.

## 5. Evidence to capture

- GitHub Actions green workflow run.
- Terminal output showing both robot IDs and task assignment.
- Topic echo showing telemetry and task lifecycle messages.
- RViz view showing map, robot poses, and navigation goals when Nav2 is validated.
- Gazebo screenshot or short recording only after the simulation is actually run.
- A short test report with environment, steps, expected result, actual result, and pass/fail status.

Do not describe a planned test as completed. Do not claim physical robot validation based only on CI or simulation.
