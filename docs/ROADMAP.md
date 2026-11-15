# Development Roadmap

This roadmap distinguishes implementation from runtime verification. A checked implementation item does not imply that it has been validated against a live robot or simulator.

## Milestone 1 — Fleet core
- [x] Robot state model and in-memory registry
- [x] Battery-aware deterministic allocator
- [x] ROS 2 topic adapter
- [x] Pure Python unit tests

## Milestone 2 — Task lifecycle and robot agents
- [x] Robot status heartbeat publisher
- [x] Assignment subscriber with robot ID filtering
- [x] Assignment receipt acknowledgement publisher
- [x] Fleet manager acknowledgement consumer
- [x] Task lifecycle store and transition validation
- [x] Duplicate task ID protection
- [x] Robot reservation before assignment publication
- [x] Heartbeat timeout and stale-robot detection
- [x] Nav2-mode task execution and action-result reporting (implementation only; live server validation pending)

## Milestone 3 — Navigation integration
- [x] Optional Nav2 `NavigateToPose` action client
- [x] Per-robot namespace and relative action-name support
- [x] Goal acceptance and terminal-result handling
- [ ] Goal cancellation and preemption handling
- [ ] Live Nav2 action-server integration test

## Milestone 4 — Coordination and resilience
- [ ] Distance-aware allocation
- [ ] Persistent task queue and recovery after restart
- [ ] Charging and robot capability constraints
- [ ] Shared-zone / traffic conflict strategy
- [ ] Failed-task retry and reassignment policy

## Milestone 5 — Verification and demonstration
- [x] Pure Python tests in GitHub Actions
- [x] Python syntax checks in GitHub Actions
- [x] ROS 2 Humble colcon build in GitHub Actions
- [ ] ROS 2 topic-level integration test on Ubuntu 22.04 / Humble
- [ ] Live Nav2 execution test
- [ ] Multi-robot Gazebo simulation
- [ ] Recorded demonstration and test report
