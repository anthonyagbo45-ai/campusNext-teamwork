from campusflow.constants import CATEGORIES, URGENCY_LEVELS
from campusflow.errors import TicketNotFoundError, ValidationError
from campusflow.ids import id_number, next_id


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
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Title must not be blank.")
    category = _match_choice(category, CATEGORIES, "category")
    urgency = _match_choice(urgency, URGENCY_LEVELS, "urgency")
    if isinstance(affected_users, bool) or not isinstance(affected_users, int) or affected_users < 1:
        raise ValidationError("affected_users must be a positive whole number.")
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


def list_tickets(tickets):
    """Return a new list ordered by ID number."""
    return sorted(tickets, key=lambda t: id_number(t["id"]))


def view_ticket(tickets, ticket_id):
    wanted_id = ticket_id.strip().upper() if isinstance(ticket_id, str) else ""
    for ticket in tickets:
        if ticket["id"] == wanted_id:
            return ticket
    raise TicketNotFoundError(f"No ticket with ID {ticket_id!r}")
