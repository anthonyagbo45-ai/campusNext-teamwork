import re

_ID_PATTERN = re.compile(r"^T(\d+)$")


def id_number(ticket_id):
    """Return the number in an ID like 'T012' (12). Unreadable IDs sort last."""
    match = _ID_PATTERN.match(ticket_id) if isinstance(ticket_id, str) else None
    return int(match.group(1)) if match else float("inf")


def next_id(tickets):
    """Highest existing ID number + 1, so IDs stay unique after reload."""
    numbers = [id_number(t["id"]) for t in tickets if id_number(t["id"]) != float("inf")]
    return f"T{(max(numbers) + 1 if numbers else 1):03d}"
