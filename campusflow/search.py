from campusflow.constants import CATEGORIES, PRIORITIES, PRIORITY_RANK, STATUSES
from campusflow.errors import ValidationError
from campusflow.ids import id_number


def _normalise_filter(value, allowed, label):
    """Empty or None means 'do not filter'. Otherwise return the canonical choice."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"Invalid {label} {value!r}. Allowed: {', '.join(allowed)}.")
    wanted = value.strip().casefold()
    if not wanted:
        return None
    for option in allowed:
        if option.casefold() == wanted:
            return option
    raise ValidationError(f"Invalid {label} {value!r}. Allowed: {', '.join(allowed)}.")


def normalise_category(value):
    return _normalise_filter(value, CATEGORIES, "category")


def normalise_status(value):
    return _normalise_filter(value, STATUSES, "status")


def normalise_priority(value):
    return _normalise_filter(value, PRIORITIES, "priority")


def search_tickets(tickets, title="", category=None, status=None, priority=None):
    """Read-only search. Every filter that is supplied must match (AND).

    - title: case-insensitive substring match; empty means any title
    - category / status / priority: exact match after normalising; empty means any
    Returns a NEW list in ticket-ID order. The tickets themselves are never changed.
    """
    if title is None:
        title = ""
    if not isinstance(title, str):
        raise ValidationError("Title search text must be text.")
    wanted_title = title.strip().casefold()
    wanted_category = normalise_category(category)       # validate ALL filters first
    wanted_status = normalise_status(status)
    wanted_priority = normalise_priority(priority)

    matches = []
    for ticket in tickets:
        if wanted_title and wanted_title not in ticket["title"].casefold():
            continue
        if wanted_category and ticket["category"] != wanted_category:
            continue
        if wanted_status and ticket["status"] != wanted_status:
            continue
        if wanted_priority and ticket["priority"] != wanted_priority:
            continue
        matches.append(ticket)
    return sorted(matches, key=lambda t: id_number(t["id"]))


def sort_by_priority(tickets):
    """New list: critical -> low, ties by earlier numeric ticket ID. (T2 before T10.)"""
    return sorted(tickets, key=lambda t: (PRIORITY_RANK[t["priority"]], id_number(t["id"])))
