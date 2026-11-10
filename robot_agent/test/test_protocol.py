import math
import pytest

from robot_agent.protocol import (
    encode_json,
    make_status_payload,
    parse_assignment,
    parse_navigation_goal,
)


def test_make_status_payload_validates_and_normalizes_battery():
    payload = make_status_payload("robot_1", "available", "76.5")
    assert payload["robot_id"] == "robot_1"
    assert payload["battery_percent"] == 76.5
    assert payload["current_task_id"] == ""


@pytest.mark.parametrize("battery", [-1, 101, float("nan"), float("inf")])
def test_rejects_battery_outside_finite_range(battery):
    with pytest.raises(ValueError):
        make_status_payload("robot_1", "available", battery)


def test_rejects_unknown_status():
    with pytest.raises(ValueError):
        make_status_payload("robot_1", "moving", 50)


def test_parse_assignment():
    assignment = parse_assignment(
        '{"robot_id":"robot_2","task_id":"task_9","destination":"dock"}'
    )
    assert assignment == {
        "robot_id": "robot_2",
        "task_id": "task_9",
        "destination": "dock",
    }


def test_rejects_assignment_missing_destination():
    with pytest.raises(ValueError):
        parse_assignment('{"robot_id":"robot_1","task_id":"task_1"}')


def test_parse_navigation_goal_and_yaw_quaternion():
    goal = parse_navigation_goal(
        '{"x":1.5,"y":-2,"yaw":1.5707963267948966,"frame_id":"map"}'
    )
    assert goal["x"] == 1.5
    assert goal["y"] == -2.0
    assert goal["frame_id"] == "map"
    assert goal["qz"] == pytest.approx(math.sqrt(0.5))
    assert goal["qw"] == pytest.approx(math.sqrt(0.5))


@pytest.mark.parametrize("destination", [
    '{"x":"north","y":2}', '{"x":1}', '{"x":NaN,"y":2}',
    '{"x":1,"y":2,"frame_id":""}', '[]'
])
def test_rejects_invalid_navigation_destination(destination):
    with pytest.raises(ValueError):
        parse_navigation_goal(destination)


def test_encode_json_is_deterministic():
    assert encode_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'
