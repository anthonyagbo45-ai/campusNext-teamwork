from campusflow.errors import TicketNotFoundError, ValidationError


def assign_ticket(tickets, ticket_id, staff_name):
    wanted_id = ticket_id.strip().upper() if isinstance(ticket_id, str) else ""
    for ticket in tickets:
        if ticket["id"] == wanted_id:
            if not isinstance(staff_name, str) or not staff_name.strip():
                raise ValidationError("Staff member name must not be blank.")
            ticket["assigned_to"] = staff_name.strip()
            return ticket
    raise TicketNotFoundError(f"No ticket with ID {ticket_id!r}")