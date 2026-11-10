"""JSON protocol helpers shared by the robot agent and its tests."""
import json


def make_status_payload(robot_id, status, battery_percent, current_task_id=""):
    if not robot_id or not robot_id.strip():
        raise ValueError("robot_id must not be empty")
    battery = float(battery_percent)
    if not 0.0 <= battery <= 100.0:
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
    """Parse and validate an assignment message.

    Returns a dictionary containing robot_id, task_id and destination.
    """
    payload = json.loads(payload_text)
    if not isinstance(payload, dict):
        raise ValueError("assignment must be a JSON object")
    required = ("robot_id", "task_id", "destination")
    if any(not isinstance(payload.get(key), str) or not payload[key].strip()
           for key in required):
        raise ValueError("assignment requires non-empty robot_id, task_id and destination")
    return {key: payload[key] for key in required}


def encode_json(payload):
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)
