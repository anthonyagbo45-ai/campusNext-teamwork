import json
import os

from campusflow.errors import StorageError


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
    return data


def save_tickets(tickets, path):
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle, indent=2)
        os.replace(temp_path, path)
    except OSError as error:
        raise StorageError(f"Could not write {path}: {error}") from error
