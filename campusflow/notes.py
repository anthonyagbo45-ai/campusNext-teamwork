from campusflow.errors import InvalidTransitionError
from campusflow.validation import validate_note_author, validate_note_message
from campusflow.workflow import _find_ticket


def next_note_id(ticket):
    highest = 0
    for note in ticket["notes"]:
        highest = max(highest, int(note["note_id"][1:]))
    return f"N{highest + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    ticket = _find_ticket(tickets, ticket_id)           # 1. find
    author = validate_note_author(author)               # 2. validate
    message = validate_note_message(message)
    if ticket["status"] == "resolved":                  # 3. state
        raise InvalidTransitionError(
            f"{ticket['id']} is resolved. Reopen it before adding notes."
        )
    note = {                                            # 4. only now change
        "note_id": next_note_id(ticket),
        "author": author,
        "message": message,
    }
    ticket["notes"].append(note)
    return note
