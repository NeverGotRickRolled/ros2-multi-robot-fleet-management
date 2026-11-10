# Development Roadmap

## Milestone 1 — Fleet core
- [x] Robot state model
- [x] In-memory robot registry
- [x] Battery-aware deterministic allocator
- [x] ROS 2 topic adapter scaffold
- [x] Pure Python unit tests

## Milestone 2 — Robot agents
- [x] Robot status heartbeat publisher
- [x] Assignment subscriber with robot ID filtering
- [x] Assignment receipt acknowledgement publisher
- [ ] Fleet manager acknowledgement consumer and completion state
- [ ] Heartbeat timeout and stale-robot detection

## Milestone 3 — Navigation
- [ ] Nav2 action client integration
- [ ] Per-robot namespace and frame configuration
- [ ] Goal result and cancellation handling

## Milestone 4 — Coordination
- [ ] Distance-aware allocation
- [ ] Task priority and queue policy
- [ ] Duplicate assignment prevention
- [ ] Shared-zone / traffic conflict strategy

## Milestone 5 — Demonstration and verification
- [ ] ROS 2 Humble colcon build
- [ ] Unit and integration tests
- [ ] Multi-robot simulation
- [ ] Recorded demo and test report
