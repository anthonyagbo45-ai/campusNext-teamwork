import json
import os

from campusflow.constants import PRIORITIES, STATUSES
from campusflow.errors import StorageError

REQUIRED_KEYS = ("id", "title", "category", "urgency", "affected_users",
                 "priority", "status", "assigned_to")


def _check_ticket(ticket, path, position):
    if not isinstance(ticket, dict):
        raise StorageError(f"{path}: item {position} is not a ticket.")
    missing = [key for key in REQUIRED_KEYS if key not in ticket]
    if missing:
        raise StorageError(f"{path}: item {position} is missing {', '.join(missing)}.")
    if ticket["status"] not in STATUSES or ticket["priority"] not in PRIORITIES:
        raise StorageError(f"{path}: item {position} has an unknown status or priority.")


def load_tickets(path):
    """Missing file = fresh start. Malformed JSON = StorageError (file untouched)."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as error:
        raise StorageError(f"{path} is not valid JSON ({error}). Fix or remove it.") from error
    except OSError as error:
        raise StorageError(f"Could not read {path}: {error}") from error
    if not isinstance(data, list):
        raise StorageError(f"{path} must contain a list of tickets.")
    for position, ticket in enumerate(data, start=1):
        _check_ticket(ticket, path, position)
    return data


def save_tickets(tickets, path):
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle, indent=2)
        os.replace(temp_path, path)
    except OSError as error:
        raise StorageError(f"Could not write {path}: {error}") from error
