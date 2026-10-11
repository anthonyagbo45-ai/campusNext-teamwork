from campusflow.errors import CampusFlowError, ValidationError
from campusflow.reports import build_report
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket, list_tickets, view_ticket
from campusflow.work_queue import get_work_queue
from campusflow.workflow import assign_ticket, change_status, reopen_ticket

MENU = """
CampusFlow
1) Create ticket   2) List tickets   3) View ticket   4) Assign ticket
5) Change status   6) Reopen ticket  7) Work queue    8) Report
0) Exit"""


def format_ticket(t):
    who = t["assigned_to"] or "unassigned"
    return (f"{t['id']} [{t['priority']}] {t['status']} - {t['title']} "
            f"({t['category']}, {t['urgency']}, {t['affected_users']} users, {who})")


def _ask_number(text):
    try:
        return int(text.strip())
    except ValueError:
        raise ValidationError("affected_users must be a positive whole number.") from None


def _print_tickets(tickets, out):
    if not tickets:
        out("No tickets.")
    for t in tickets:
        out(format_ticket(t))


def handle_choice(choice, tickets, ask, out):
    """Run one menu choice. Returns True if tickets changed (so the caller saves)."""
    if choice == "1":
        t = create_ticket(tickets, ask("Title: "), ask("Category: "), ask("Urgency: "),
                          _ask_number(ask("Affected users: ")))
        out(f"Created {format_ticket(t)}")
        return True
    if choice == "2":
        _print_tickets(list_tickets(tickets), out)
    elif choice == "3":
        out(format_ticket(view_ticket(tickets, ask("Ticket ID: "))))
    elif choice == "4":
        out("Assigned: " + format_ticket(assign_ticket(tickets, ask("Ticket ID: "), ask("Staff name: "))))
        return True
    elif choice == "5":
        out("Updated: " + format_ticket(change_status(tickets, ask("Ticket ID: "), ask("New status: "))))
        return True
    elif choice == "6":
        out("Reopened: " + format_ticket(reopen_ticket(tickets, ask("Ticket ID: "))))
        return True
    elif choice == "7":
        _print_tickets(get_work_queue(tickets), out)
    elif choice == "8":
        r = build_report(tickets)
        out(f"Total: {r['total']}  Unassigned: {r['unassigned']}")
        for key in ("by_status", "by_priority", "by_category"):
            out(key.replace("_", " ") + ": " + ", ".join(f"{k}={v}" for k, v in r[key].items()))
    else:
        out("Please choose a number from the menu.")
    return False


def run(path, ask=input, out=print):
    """The only place that calls input(). Errors are caught and printed."""
    try:
        tickets = load_tickets(path)
    except CampusFlowError as error:
        out(f"Error: {error}")
        return
    while True:
        out(MENU)
        choice = ask("Choose: ").strip()
        if choice == "0":
            out("Goodbye.")
            return
        try:
            if handle_choice(choice, tickets, ask, out):
                save_tickets(tickets, path)
        except CampusFlowError as error:
            out(f"Error: {error}")
