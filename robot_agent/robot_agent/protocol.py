"""JSON protocol helpers shared by the robot agent and its tests."""
import json
import math


def make_status_payload(robot_id, status, battery_percent, current_task_id=""):
    if not robot_id or not robot_id.strip():
        raise ValueError("robot_id must not be empty")
    battery = float(battery_percent)
    if not math.isfinite(battery) or not 0.0 <= battery <= 100.0:
        raise ValueError("battery_percent must be between 0 and 100")
    if status not in {"available", "busy", "offline", "error"}:
        raise ValueError(f"unsupported robot status: {status}")
    return {
        "robot_id": robot_id,
        "status": status,
        "battery_percent": battery,
        "current_task_id": current_task_id,
    }


def parse_assignment(payload_text):
    """Parse and validate an assignment JSON object."""
    payload = json.loads(payload_text)
    if not isinstance(payload, dict):
        raise ValueError("assignment must be a JSON object")
    required = ("robot_id", "task_id", "destination")
    if any(not isinstance(payload.get(key), str) or not payload[key].strip()
           for key in required):
        raise ValueError("assignment requires non-empty robot_id, task_id and destination")
    return {key: payload[key] for key in required}


def parse_navigation_goal(destination_text):
    """Decode destination JSON into a planar NavigateToPose target.

    Expected form: {"x": 1.0, "y": 2.0, "yaw": 1.57, "frame_id": "map"}.
    """
    payload = json.loads(destination_text)
    if not isinstance(payload, dict):
        raise ValueError("navigation destination must be a JSON object")
    try:
        x = float(payload["x"])
        y = float(payload["y"])
        yaw = float(payload.get("yaw", 0.0))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("destination requires numeric x and y, with optional yaw") from exc
    frame_id = payload.get("frame_id", "map")
    if not isinstance(frame_id, str) or not frame_id.strip():
        raise ValueError("frame_id must be a non-empty string")
    if not all(math.isfinite(value) for value in (x, y, yaw)):
        raise ValueError("navigation coordinates and yaw must be finite")
    return {
        "x": x,
        "y": y,
        "yaw": yaw,
        "frame_id": frame_id,
        "qz": math.sin(yaw / 2.0),
        "qw": math.cos(yaw / 2.0),
    }


def encode_json(payload):
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)
