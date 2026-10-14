from campusflow.constants import STATUSES
from campusflow.errors import InvalidTransitionError, TicketNotFoundError, ValidationError
from campusflow.validation import validate_staff_label

# Which status each status may move to. A resolved ticket cannot move anywhere.
ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": set(),
}


def _find_ticket(tickets, ticket_id):
    wanted_id = ticket_id.strip().upper() if isinstance(ticket_id, str) else ""
    for ticket in tickets:
        if ticket["id"] == wanted_id:
            return ticket
    raise TicketNotFoundError(f"No ticket with ID {ticket_id!r}")


def assign_ticket(tickets, ticket_id, staff_name):
    ticket = _find_ticket(tickets, ticket_id)                       # 1. find
    staff_name = validate_staff_label(staff_name)                   # 2. validate
    if ticket["status"] == "resolved":                              # 3. state
        raise InvalidTransitionError(
            f"{ticket['id']} is resolved. Reopen it before assigning."
        )
    ticket["assigned_to"] = staff_name.strip()
    return ticket


def change_status(tickets, ticket_id, new_status):
    ticket = _find_ticket(tickets, ticket_id)                       # 1. find
    if isinstance(new_status, str):
        new_status = new_status.strip().lower()
    if new_status not in STATUSES:                                  # 2. validate
        raise ValidationError(
            f"Invalid status {new_status!r}. Allowed: {', '.join(STATUSES)}."
        )
    current = ticket["status"]                                      # 3. state
    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransitionError(
            f"Cannot move {ticket['id']} from {current} to {new_status}."
        )
    if new_status == "in_progress" and not ticket["assigned_to"]:
        raise InvalidTransitionError(
            f"Assign {ticket['id']} to someone before moving it to in_progress."
        )
    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    ticket = _find_ticket(tickets, ticket_id)
    if ticket["status"] != "resolved":
        raise InvalidTransitionError(f"{ticket['id']} is not resolved, so it cannot be reopened.")
    ticket["status"] = "open"
    return ticket
