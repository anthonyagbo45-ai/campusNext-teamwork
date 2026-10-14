import json
import os
import re

from campusflow.constants import PRIORITIES, STATUSES
from campusflow.errors import StorageError
from campusflow.ids import id_number

# "notes" is not required here: tickets from older files load with notes = [].
REQUIRED_KEYS = ("id", "title", "category", "urgency", "affected_users",
                 "priority", "status", "assigned_to")
NOTE_KEYS = ("note_id", "author", "message")
_NOTE_ID_PATTERN = re.compile(r"^N(\d+)$")


def _check_notes(ticket, path, position):
    notes = ticket.get("notes", [])
    if not isinstance(notes, list):
        raise StorageError(f"{path}: item {position} has notes that are not a list.")
    seen = set()
    for note in notes:
        if not isinstance(note, dict) or any(key not in note for key in NOTE_KEYS):
            raise StorageError(
                f"{path}: item {position} has a note missing note_id, author or message."
            )
        if not all(isinstance(note[key], str) for key in NOTE_KEYS):
            raise StorageError(f"{path}: item {position} has a note with a non-text field.")
        match = _NOTE_ID_PATTERN.match(note["note_id"])
        if not match:
            raise StorageError(
                f"{path}: item {position} has an unreadable note ID {note['note_id']!r}."
            )
        number = int(match.group(1))
        if number in seen:
            raise StorageError(
                f"{path}: item {position} repeats note ID {note['note_id']!r}."
            )
        seen.add(number)


def _check_ticket(ticket, path, position):
    if not isinstance(ticket, dict):
        raise StorageError(f"{path}: item {position} is not a ticket.")
    missing = [key for key in REQUIRED_KEYS if key not in ticket]
    if missing:
        raise StorageError(f"{path}: item {position} is missing {', '.join(missing)}.")
    if ticket["status"] not in STATUSES or ticket["priority"] not in PRIORITIES:
        raise StorageError(f"{path}: item {position} has an unknown status or priority.")
    _check_notes(ticket, path, position)


def load_tickets(path):
    """Missing file = fresh start. Any problem = StorageError (file untouched).

    The whole file is checked before anything is returned, so a bad file
    can never replace what is already in memory.
    """
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
    seen_numbers = {}
    for position, ticket in enumerate(data, start=1):
        _check_ticket(ticket, path, position)
        number = id_number(ticket["id"])
        if number == float("inf"):
            raise StorageError(
                f"{path}: item {position} has an unreadable ID {ticket['id']!r}."
            )
        if number in seen_numbers:
            raise StorageError(
                f"{path}: item {position} repeats ID {ticket['id']!r} "
                f"(already used by item {seen_numbers[number]})."
            )
        seen_numbers[number] = position
    for ticket in data:
        ticket.setdefault("notes", [])
    return data


def save_tickets(tickets, path):
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle, indent=2)
        os.replace(temp_path, path)
    except OSError as error:
        raise StorageError(f"Could not write {path}: {error}") from error
