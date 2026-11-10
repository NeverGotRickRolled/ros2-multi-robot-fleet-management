# Development Roadmap

## Milestone 1 — Fleet core
- [x] Robot state model and in-memory registry
- [x] Battery-aware deterministic allocator
- [x] ROS 2 topic adapter scaffold
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
- [ ] Agent-driven executing/succeeded/failed events from a real task executor

## Milestone 3 — Navigation
- [ ] Nav2 action client integration
- [ ] Per-robot namespace and frame configuration
- [ ] Goal result and cancellation handling

## Milestone 4 — Coordination
- [ ] Distance-aware allocation
- [ ] Persistent task queue and recovery after restart
- [ ] Charging and robot capability constraints
- [ ] Shared-zone / traffic conflict strategy

## Milestone 5 — Demonstration and verification
- [ ] ROS 2 Humble colcon build
- [ ] ROS 2 topic-level integration tests
- [ ] Multi-robot simulation
- [ ] Recorded demo and test report
