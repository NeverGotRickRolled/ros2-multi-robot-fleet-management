# Interview Walkthrough — ROS 2 Multi-Robot Fleet Management

## 60-second project explanation

"I built a ROS 2 fleet-management prototype that coordinates multiple robot agents. The fleet manager maintains robot telemetry, chooses an available robot using battery-aware allocation, dispatches tasks, and tracks acknowledgements and task lifecycle events. Each robot agent publishes heartbeats and filters assignments by its robot ID. I also implemented an optional Nav2 NavigateToPose action client so an agent can forward a structured destination to its own Nav2 stack. The Python tests and ROS 2 Humble package build pass in GitHub Actions; live Nav2 and Gazebo validation are the next steps."

## Problem being addressed

In a multi-robot deployment, sending tasks directly to individual robots makes it difficult to track availability, battery state, task ownership, and failures centrally. A fleet manager provides a coordination point for task assignment and status monitoring.

## Design decisions

### Why a fleet manager?

It centralizes task intake, robot selection, assignment ownership, and lifecycle tracking. Robot-side agents remain responsible for their own telemetry and navigation integration.

### How is a robot selected?

The allocator considers robots that are available and meet the configured minimum battery threshold. Selection is deterministic, including a stable tie-break, which makes behaviour easier to test and reproduce.

### Why reserve before publishing?

The manager marks the selected robot busy and records the task assignment before publishing the assignment message. This reduces the chance that another pending task is dispatched to the same robot during the same dispatch cycle.

### Why use ROS 2 topics for fleet messages?

Telemetry, task requests, assignments, acknowledgements, and task status are asynchronous events. The current prototype transports them as JSON strings in `std_msgs/msg/String`. A production evolution would use custom ROS interfaces with explicit fields and stronger schema/version control.

### Why use a Nav2 action?

Navigation is a long-running operation with feedback and a terminal result. The `NavigateToPose` action is a better fit than a one-shot topic message for sending a goal and observing whether it completes.

### How are multiple agents separated?

Each agent can run in a distinct ROS namespace, such as `/robot_1` and `/robot_2`. Fleet topics are absolute and shared; the Nav2 action name is relative so it resolves inside each robot namespace.

## Current engineering limitations

Be open about these limitations:

- Task and robot registry state is in memory, not persistent.
- No automatic retry, reassignment, or task cancellation workflow.
- No traffic deconfliction or shared-zone reservation.
- No robot model, Gazebo world, map, localization, or controller launch is included.
- The Nav2 action client is implemented but still needs live action-server validation.
- CI build success does not prove runtime navigation or physical robot behaviour.

## Verification statement

The current verified evidence is the passing GitHub Actions workflow for Python tests, syntax checks, and a ROS 2 Humble colcon build. Do not claim live Nav2, Gazebo, or hardware testing until those tests have been run and evidence captured.

## Suggested next improvements

1. Run ROS 2 runtime integration tests on Ubuntu 22.04 / Humble.
2. Validate the Nav2 action client against a real action server.
3. Add cancellation and failure recovery.
4. Add persistent task state.
5. Add robot URDF/Xacro, world, and multi-robot Gazebo launch.
6. Implement and test traffic coordination.
