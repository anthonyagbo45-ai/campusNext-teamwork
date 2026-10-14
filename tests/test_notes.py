import copy
import unittest

from campusflow.errors import InvalidTransitionError, TicketNotFoundError, ValidationError
from campusflow.notes import add_note
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status, reopen_ticket
from tests.helpers import make_ticket


class AddNoteTests(unittest.TestCase):
    def test_first_note_gets_n001_and_is_stored(self):
        tickets = [make_ticket("T001")]
        note = add_note(tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        self.assertEqual(note, {"note_id": "N001", "author": "Mentor A",
                                "message": "Wi-Fi router reboot attempted"})
        self.assertEqual(tickets[0]["notes"], [note])

    def test_second_note_gets_n002(self):
        tickets = [make_ticket("T001")]
        add_note(tickets, "T001", "Mentor A", "Router reboot attempted")
        note = add_note(tickets, "T001", "Mentor B", "Investigating switch ports")
        self.assertEqual(note["note_id"], "N002")

    def test_note_ids_count_per_ticket(self):
        tickets = [make_ticket("T001"), make_ticket("T002")]
        add_note(tickets, "T001", "Mentor A", "First note here")
        note = add_note(tickets, "T002", "Mentor A", "First note here")
        self.assertEqual(note["note_id"], "N001")

    def test_author_and_message_are_trimmed(self):
        tickets = [make_ticket("T001")]
        note = add_note(tickets, "t001 ", "  Mentor A ", "   Rebooted the router   ")
        self.assertEqual((note["author"], note["message"]), ("Mentor A", "Rebooted the router"))

    def test_in_progress_ticket_accepts_notes(self):
        tickets = [make_ticket("T001", status="in_progress", assigned_to="Amina")]
        self.assertEqual(add_note(tickets, "T001", "Mentor A", "Checking cables")["note_id"], "N001")

    def test_message_length_boundaries(self):
        tickets = [make_ticket("T001")]
        for good in ("12345", "x" * 300):
            with self.subTest(length=len(good)):
                add_note(tickets, "T001", "Mentor A", good)
        for bad in ("", "    ", "1234", " 1234 ", "x" * 301):
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    add_note(tickets, "T001", "Mentor A", bad)

    def test_blank_or_non_text_author_is_rejected(self):
        tickets = [make_ticket("T001")]
        for bad in ("", "   ", None, 42):
            with self.subTest(author=bad):
                with self.assertRaises(ValidationError):
                    add_note(tickets, "T001", bad, "A perfectly good message")

    def test_rejected_note_changes_nothing_and_does_not_use_an_id(self):
        tickets = [make_ticket("T001")]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValidationError):
            add_note(tickets, "T001", "Mentor A", "hi")
        self.assertEqual(tickets, before)
        self.assertEqual(add_note(tickets, "T001", "Mentor A", "Now a good note")["note_id"], "N001")

    def test_resolved_ticket_rejects_note_and_stays_unchanged(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Amina")]
        before = copy.deepcopy(tickets)
        with self.assertRaises(InvalidTransitionError):
            add_note(tickets, "T001", "Mentor A", "Trying to add after resolve")
        self.assertEqual(tickets, before)

    def test_note_after_reopen_is_accepted_and_old_notes_are_kept(self):
        tickets = [make_ticket("T001", assigned_to="Amina")]
        add_note(tickets, "T001", "Mentor A", "Router reboot attempted")
        add_note(tickets, "T001", "Mentor B", "Investigating switch ports")
        change_status(tickets, "T001", "in_progress")
        change_status(tickets, "T001", "resolved")
        with self.assertRaises(InvalidTransitionError):
            add_note(tickets, "T001", "Mentor A", "Rejected while resolved")
        self.assertEqual(len(tickets[0]["notes"]), 2)          # kept through resolve
        reopen_ticket(tickets, "T001")
        note = add_note(tickets, "T001", "Mentor A", "Accepted after reopen")
        self.assertEqual(note["note_id"], "N003")              # rejected one used no ID
        self.assertEqual([n["note_id"] for n in tickets[0]["notes"]], ["N001", "N002", "N003"])

    def test_unknown_ticket_id(self):
        with self.assertRaises(TicketNotFoundError):
            add_note([make_ticket("T001")], "T999", "Mentor A", "A perfectly good message")

    def test_check_order_find_then_validate_then_state(self):
        resolved = [make_ticket("T001", status="resolved")]
        with self.assertRaises(TicketNotFoundError):            # unknown id beats bad message
            add_note(resolved, "T404", "Mentor A", "hi")
        with self.assertRaises(ValidationError):                # bad message beats resolved state
            add_note(resolved, "T001", "Mentor A", "hi")

    def test_new_note_id_follows_highest_existing_id(self):
        tickets = [make_ticket("T001", notes=[
            {"note_id": "N001", "author": "A", "message": "first one"},
            {"note_id": "N004", "author": "A", "message": "fourth one"}])]
        self.assertEqual(add_note(tickets, "T001", "Mentor A", "Next note here")["note_id"], "N005")


class NewTicketNotesTests(unittest.TestCase):
    def test_new_ticket_starts_with_empty_notes(self):
        self.assertEqual(create_ticket([], "Wi-Fi down", "network", "low", 1)["notes"], [])

    def test_each_ticket_has_its_own_notes_list(self):
        tickets = []
        a = create_ticket(tickets, "A", "Other", "low", 1)
        b = create_ticket(tickets, "B", "Other", "low", 1)
        add_note(tickets, a["id"], "Mentor A", "Only for ticket A")
        self.assertEqual(b["notes"], [])


if __name__ == "__main__":
    unittest.main()