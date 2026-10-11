from campusflow.constants import STATUSES
from campusflow.errors import InvalidTransitionError, TicketNotFoundError, ValidationError

# Which status each status may move to. A resolved ticket cannot move anywhere.
ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": set(),
}


def assign_ticket(tickets, ticket_id, staff_name):
    wanted_id = ticket_id.strip().upper() if isinstance(ticket_id, str) else ""
    for ticket in tickets:
        if ticket["id"] == wanted_id:
            if not isinstance(staff_name, str) or not staff_name.strip():
                raise ValidationError("Staff member name must not be blank.")
            ticket["assigned_to"] = staff_name.strip()
            return ticket
    raise TicketNotFoundError(f"No ticket with ID {ticket_id!r}")


def change_status(tickets, ticket_id, new_status):
    wanted_id = ticket_id.strip().upper() if isinstance(ticket_id, str) else ""
    for ticket in tickets:
        if ticket["id"] == wanted_id:
            if new_status not in STATUSES:
                raise ValidationError(
                    f"Invalid status {new_status!r}. Allowed: {', '.join(STATUSES)}."
                )
            current = ticket["status"]
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
    raise TicketNotFoundError(f"No ticket with ID {ticket_id!r}")
