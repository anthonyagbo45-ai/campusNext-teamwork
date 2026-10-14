# Design decisions

## Ownership

| Issue | Feature | Owner |
|---|---|---|
| #1 | F1 Create | Nese |
| #2 | F2 List / View | Nese |
| #3 | F3 Assign | Anthony |
| #4 | F4 Workflow | Anthony |
| #5 | F5 Work queue | Anthony |
| #6 | F6 Reports | Anthony |
| #7 | F7 Persistence | Nese |
| #8 | CLI menu | Anthony |

Each engineer writes the unit tests for their own features.

## Data structure
- Tickets are stored in one Python list of dictionaries.
- Each ticket has: id, title, category, urgency, affected_users, priority, status, assigned_to, notes (a list of notes).
- The list is passed into every function as an argument. There are no global variables.

## Function contracts
- create_ticket(tickets, title, category, urgency, affected_users): adds and returns the new ticket.
- assign_ticket(tickets, ticket_id, staff_name): returns the updated ticket.
- change_status(tickets, ticket_id, new_status): returns the updated ticket.
- reopen_ticket(tickets, ticket_id): returns the updated ticket.
- add_note(tickets, ticket_id, author, message): adds a note to the ticket and returns the new note.
- get_work_queue(tickets): returns a new sorted list.
- build_report(tickets): returns a dictionary of counts.
- load_tickets(path) and save_tickets(tickets, path): only storage.py touches files.
- Invalid input raises an exception with a clear message. The CLI catches it and prints it.
- Only the CLI calls input(), so the other functions can be tested without typing.

## Rules we agreed on
- Category, urgency and status are case-insensitive and whitespace is trimmed.
- affected_users must be a positive whole number.
- Priority rules are checked in order and the first match wins.
- Workflow: open -> in_progress -> resolved. A ticket must be assigned before in_progress.
- A resolved ticket cannot be changed until it is reopened (reopen sets it to open).
- Work queue: open tickets only, ordered critical -> low, ties by earlier ID number.
- Next ticket ID = highest existing ID number + 1, so IDs stay unique after reload.
- Missing JSON file = fresh start. Malformed JSON = clear error, and the file is not overwritten.
- Bad input values (blank staff name, unknown status, affected_users of 0, invalid category or urgency) raise ValidationError.
- Valid input that the ticket's current state does not allow (assigning or changing a resolved ticket, moving an unassigned ticket to in_progress, moving to a status out of order, reopening a ticket that is not resolved) raise InvalidTransitionError.
- Unknown ticket IDs raise TicketNotFoundError.
- Check order inside a function: find the ticket first (TicketNotFoundError), then validate the input (ValidationError), then check the ticket's state (InvalidTransitionError).
- Ticket IDs are trimmed and uppercased before lookup.
- All input checks live in campusflow/validation.py and are used by creation, assignment, status change and notes.
- Every ticket has a notes list, empty at creation. Each note has note_id, author and message.
- Note IDs count per ticket (N001, N002, ...): highest existing number + 1. A rejected note uses no ID.
- A note message is trimmed and must be 5 to 300 characters. The author must not be blank.
- A resolved ticket does not accept notes until it is reopened. Existing notes are kept.
- Loading checks the whole file before anything is used. Duplicate ticket IDs (T001 and T1 count as the same), unreadable IDs and malformed notes raise StorageError. Tickets from older files without notes load with an empty list.
- A rejected action leaves the ticket list exactly as it was.

## Branch plan
- Branch names: feat/1-ticket-creation, feat/3-assign-ticket, and so on.
- Branches start from the same main and use different files.
- The first approved PR merges first. The second engineer then updates their branch from main, reruns the tests, and gets re-approval before merging.