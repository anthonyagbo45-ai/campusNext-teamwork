from campusflow.errors import TicketNotFoundError, ValidationError


def assign_ticket(tickets, ticket_id, staff_name):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            if not staff_name.strip():
                raise ValidationError("Staff member name must not be blank.")
            ticket["assigned_to"] = staff_name
            return ticket
    raise TicketNotFoundError(f"No ticket with ID {ticket_id}")