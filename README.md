# ROS 2 Multi-Robot Fleet Management

A portfolio project exploring multi-robot task allocation, robot registration, telemetry, and fleet-level coordination using ROS 2.

> **Development status:** Initial software architecture and fleet-allocation foundation. ROS 2 runtime, Gazebo integration, multi-robot navigation, and end-to-end behaviour have not yet been validated.

## Project goals

- Maintain a registry of robots and their latest reported state.
- Accept task requests and assign eligible robots.
- Exclude unavailable or low-battery robots from new assignments.
- Publish assignments through ROS 2 topics.
- Grow toward multi-robot navigation, task lifecycle management, and fleet observability.

## Planned architecture

```text
                 Fleet Manager
       +-------------------------------+
       | Robot Registry                |
       | Task Queue / Allocator        |
       | Assignment & Status Interface |
       +---------------+---------------+
                       |
          ROS 2 topics (JSON MVP)
                       |
        +--------------+--------------+
        |              |              |
     /robot_1       /robot_2       /robot_3
     Robot Agent    Robot Agent    Robot Agent
        |              |              |
     Navigation     Navigation     Navigation
     (planned)      (planned)      (planned)
```

The first milestone uses a deliberately small ROS 2 interface based on `std_msgs/msg/String` with JSON payloads. This keeps the prototype inspectable while the message contracts evolve. A future milestone can replace these payloads with dedicated ROS 2 interface messages and actions.

## Repository layout

```
fleet_manager/
  fleet_manager/
    allocator.py
    models.py
    registry.py
    fleet_manager_node.py
  test/
    test_allocator.py
  package.xml
  setup.py
  setup.cfg
  resource/
docs/
  ARCHITECTURE.md
  ROADMAP.md
```

## Development environment

Target platform: Ubuntu 22.04, ROS 2 Humble, Python 3.10.

ROS 2 runtime instructions will be added as the node and robot-side interfaces mature. Pure Python allocation tests can be run independently:

```bash
cd fleet_manager
python3 -m pip install pytest
PYTHONPATH=. pytest -q test
```

## Current implementation

- [x] Initial repository architecture and roadmap
- [x] Robot state model and in-memory registry
- [x] Deterministic battery-aware task allocator
- [x] ROS 2 fleet-manager node scaffold using JSON topic payloads
- [x] Unit tests for allocation logic
- [x] Robot-side telemetry and assignment agent scaffold
- [x] Robot agent JSON protocol unit tests
- [ ] ROS 2 build and runtime verification
- [ ] Robot-side namespaced simulation and runtime integration
- [ ] Navigation action dispatch and task lifecycle
- [ ] Multi-robot conflict handling and observability

## Design boundaries

This is a research and learning prototype, not a certified industrial fleet controller. Allocation decisions are not safety-rated and must not replace robot-local protective systems, emergency stops, or safety-rated traffic management.

## Attribution

This repository is an independently developed portfolio project. Third-party dependencies and ROS 2 components remain subject to their respective licences.
