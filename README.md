# ROS 2 Multi-Robot Fleet Management

A portfolio project exploring multi-robot task allocation, robot registration, telemetry, task lifecycle tracking, and fleet-level coordination using ROS 2.

> **Development status:** Fleet allocation, task lifecycle logic, robot-agent protocol, and pure Python tests are implemented. ROS 2 runtime, Gazebo integration, multi-robot navigation, and end-to-end behaviour have not yet been validated.

## Project goals

- Maintain a registry of robots and their latest reported state.
- Accept and queue task requests.
- Assign eligible robots using availability and battery level.
- Track assignment acknowledgements and task lifecycle states.
- Detect stale robot heartbeats and mark robots offline.
- Grow toward multi-robot navigation and fleet observability.

## Architecture

```text
                 Fleet Manager
       +--------------------------------+
       | Robot Registry                |
       | Task Store / Lifecycle        |
       | Battery-aware Task Allocator  |
       | Heartbeat Monitor             |
       +---------------+----------------+
                       |
              ROS 2 JSON topics
                       |
        +--------------+--------------+
        |              |              |
     /robot_1       /robot_2       /robot_3
     Robot Agent    Robot Agent    Robot Agent
        |              |              |
      Nav2 planned; not implemented yet
```

The MVP uses `std_msgs/msg/String` with JSON payloads. Dedicated ROS 2 interface messages/actions may replace these once the protocol stabilizes.

## Task lifecycle

```text
PENDING -> ASSIGNED -> ACCEPTED -> EXECUTING -> SUCCEEDED
                    |             |
                    +-> REJECTED  +-> FAILED
                    |
                    +-> FAILED (heartbeat timeout)
```

The agent currently acknowledges receipt only. It does not claim to navigate or complete tasks. The fleet manager supports later execution status events, but those events must come from a real task executor before they represent physical progress.

## ROS 2 topics

- `/fleet/robot_status`: robot telemetry and heartbeat
- `/fleet/task_request`: incoming task requests
- `/fleet/task_assignment`: assignments from fleet manager
- `/fleet/task_ack`: robot acceptance/rejection
- `/fleet/task_status`: task lifecycle updates

## Run pure Python tests

These tests do not require ROS 2:

```bash
python3 -m pip install pytest
cd fleet_manager && PYTHONPATH=. pytest -q test
cd ../robot_agent && PYTHONPATH=. pytest -q test
```

Target runtime: Ubuntu 22.04, ROS 2 Humble, Python 3.10. ROS 2 build and runtime verification are still pending.

## Repository layout

- `fleet_manager/`: registry, allocator, lifecycle store, ROS 2 fleet node and tests
- `robot_agent/`: telemetry and assignment acknowledgement node
- `docs/`: architecture and roadmap

## Design boundaries

This is a research and learning prototype, not a certified industrial fleet controller. Allocation decisions are not safety-rated and must not replace robot-local protective systems, emergency stops, or safety-rated traffic management.
