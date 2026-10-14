from campusflow.constants import CATEGORIES, STATUSES, URGENCY_LEVELS
from campusflow.errors import TicketNotFoundError, ValidationError
from campusflow.ids import id_number, next_id
from campusflow.validation import (
    validate_affected_users,
    validate_category,
    validate_title,
    validate_urgency,
)


def compute_priority(urgency, affected_users):
    """Rules are checked in order; the first match wins."""
    if urgency == "high" and affected_users >= 10:      # RULE 1
        return "critical"
    if urgency == "high" or affected_users >= 10:       # RULE 2
        return "high"
    if urgency == "medium" or affected_users >= 3:      # RULE 3
        return "medium"
    return "low"                                        # RULE 4


def _match_choice(value, allowed, label):
    if isinstance(value, str):
        for option in allowed:
            if value.strip().lower() == option.lower():
                return option
    raise ValidationError(f"Invalid {label} {value!r}. Allowed: {', '.join(allowed)}.")


def create_ticket(tickets, title, category, urgency, affected_users):
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)
    ticket = {
        "id": next_id(tickets),
        "title": title.strip(),
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": compute_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket


def list_tickets(tickets, status=None):
    """Return a NEW list ordered by ID number. Optional status filter (case-insensitive)."""
    if status is not None:
        wanted = status.strip().lower() if isinstance(status, str) else status
        if wanted not in STATUSES:
            raise ValidationError(f"Invalid status {status!r}. Allowed: {', '.join(STATUSES)}.")
        tickets = [t for t in tickets if t["status"] == wanted]
    return sorted(tickets, key=lambda t: id_number(t["id"]))


def view_ticket(tickets, ticket_id):
    wanted_id = ticket_id.strip().upper() if isinstance(ticket_id, str) else ""
    for ticket in tickets:
        if ticket["id"] == wanted_id:
            return ticket
    raise TicketNotFoundError(f"No ticket with ID {ticket_id!r}")
