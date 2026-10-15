from campusflow.errors import CampusFlowError, ValidationError
from campusflow.ids import id_number
from campusflow.notes import add_note
from campusflow.reports import build_report
from campusflow.constants import CATEGORIES, PRIORITIES, STATUSES, URGENCY_LEVELS
from campusflow.search import search_tickets, sort_by_priority
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket, list_tickets, view_ticket
from campusflow.understanding_check import run_check
from campusflow.work_queue import get_work_queue
from campusflow.workflow import assign_ticket, change_status, reopen_ticket

MENU = """
CampusFlow
1) Create ticket   2) List tickets   3) View ticket   4) Assign ticket
5) Change status   6) Reopen ticket  7) Work queue    8) Report
9) Add follow-up note   10) View ticket notes   11) Search tickets
12) Understanding check
0) Exit"""

CHECK_NOTES_FILE = "understanding-check-notes.md"


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


CATEGORY_HINTS = {
    "Network": "Wi-Fi, internet, cables, switches, login to the campus network",
    "Hardware": "laptops, desktops, printers, projectors, screens, keyboards",
    "Software": "apps, installations, updates, licences, accounts",
    "Other": "anything that does not fit the three above",
}
URGENCY_HINTS = {
    "high": "work has stopped, or many people are affected",
    "medium": "work is slowed down, or a workaround exists",
    "low": "minor problem, no one is blocked",
}


def _pick(ask, out, label, options, hints=None, allow_blank=False):
    """Show a numbered list and ask until the answer is a valid number or name.

    Accepts the number (1, 2, ...) or the option's name in any case. If
    allow_blank is True, pressing Enter returns None, meaning "any".
    """
    out(f"{label}:")
    for number, option in enumerate(options, start=1):
        hint = f" - {hints[option]}" if hints and option in hints else ""
        out(f"  {number}) {option}{hint}")
    if allow_blank:
        out("  (press Enter for any)")
    while True:
        answer = ask(f"{label} (1-{len(options)}): ").strip()
        if not answer and allow_blank:
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        for option in options:
            if answer.casefold() == option.casefold():
                return option
        out(f"Error: Invalid {label.lower()} {answer!r}. "
            f"Choose a number from 1 to {len(options)} or type a name.")


def _format_search_row(t):
    return (f"{t['id']} | {t['title']} | {t['category']} | {t['priority']} | "
            f"{t['status']} | {t['assigned_to'] or 'unassigned'}")


def _search(tickets, ask, out):
    title = ask("Title contains (blank = any): ")
    category = _pick(ask, out, "Category", CATEGORIES, CATEGORY_HINTS, allow_blank=True)
    status = _pick(ask, out, "Status", STATUSES, allow_blank=True)
    priority = _pick(ask, out, "Priority", PRIORITIES, allow_blank=True)
    results = search_tickets(tickets, title, category, status, priority)
    if ask("Sort by priority? (y/n): ").strip().lower() == "y":
        results = sort_by_priority(results)
    if not results:
        out("No matching tickets.")
    for ticket in results:
        out(_format_search_row(ticket))


def _show_notes(tickets, ask, out):
    ticket = view_ticket(tickets, ask("Ticket ID: "))
    notes = sorted(ticket["notes"], key=lambda n: id_number("T" + n["note_id"][1:]))
    if not notes:
        out(f"{ticket['id']} has no notes.")
    for note in notes:
        out(f"{note['note_id']} [{note['author']}] {note['message']}")


def handle_choice(choice, tickets, ask, out, check_notes_path=CHECK_NOTES_FILE):
    """Run one menu choice. Returns True if tickets changed (so the caller saves)."""
    if choice == "1":
        title = ask("Title: ")
        category = _pick(ask, out, "Category", CATEGORIES, CATEGORY_HINTS)
        urgency = _pick(ask, out, "Urgency", URGENCY_LEVELS, URGENCY_HINTS)
        t = create_ticket(tickets, title, category, urgency,
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
        out(f"Resolved: {r['resolved']}  Unresolved: {r['unresolved']}  "
            f"Resolution: {r['resolution_percentage']}%")
        for key in ("by_status", "by_priority", "by_category"):
            out(key.replace("_", " ") + ": " + ", ".join(f"{k}={v}" for k, v in r[key].items()))
    elif choice == "9":
        note = add_note(tickets, ask("Ticket ID: "), ask("Author: "), ask("Message: "))
        out(f"Added note {note['note_id']}.")
        return True
    elif choice == "10":
        _show_notes(tickets, ask, out)
    elif choice == "11":
        _search(tickets, ask, out)
    elif choice == "12":
        run_check(ask, out, notes_path=check_notes_path)
    else:
        out("Please choose a number from the menu.")
    return False


def run(path, ask=input, out=print, check_notes_path=CHECK_NOTES_FILE):
    """The only place that calls input(). Errors are caught and printed."""
    try:
        tickets = load_tickets(path)
    except CampusFlowError as error:
        out(f"Error: {error}")
        return
    while True:
        out(MENU)
        try:
            choice = ask("Choose: ").strip()
        except (KeyboardInterrupt, EOFError):       # Ctrl+C / Ctrl+D: leave politely
            out("\nGoodbye.")
            return
        if choice == "0":
            out("Goodbye.")
            return
        try:
            if handle_choice(choice, tickets, ask, out, check_notes_path):
                save_tickets(tickets, path)
        except CampusFlowError as error:
            out(f"Error: {error}")
