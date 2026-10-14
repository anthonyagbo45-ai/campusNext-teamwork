import json
import os
import tempfile
import unittest

from campusflow.errors import StorageError
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from tests.helpers import make_ticket


def note(note_id="N001", author="Mentor A", message="A good message"):
    return {"note_id": note_id, "author": author, "message": message}


class LoadChecksTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "tickets.json")

    def write(self, data):
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle)

    def test_duplicate_ticket_ids_are_rejected(self):
        self.write([make_ticket("T001"), make_ticket("T001")])
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_same_number_in_different_spelling_is_a_duplicate(self):
        self.write([make_ticket("T001"), make_ticket("T1")])
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_unreadable_ticket_ids_are_rejected(self):
        for bad in ("ABC", "", 5, None):
            with self.subTest(bad=bad):
                self.write([make_ticket(bad)])
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_notes_must_be_a_list(self):
        for bad in ("text", 5, {"note_id": "N001"}, None):
            with self.subTest(bad=bad):
                ticket = make_ticket("T001")
                ticket["notes"] = bad
                self.write([ticket])
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_note_missing_a_field_is_rejected(self):
        for missing in ("note_id", "author", "message"):
            with self.subTest(missing=missing):
                bad = note()
                del bad[missing]
                self.write([make_ticket("T001", notes=[bad])])
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_note_fields_must_be_text(self):
        for field in ("note_id", "author", "message"):
            with self.subTest(field=field):
                bad = note()
                bad[field] = 7
                self.write([make_ticket("T001", notes=[bad])])
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_bad_note_id_is_rejected(self):
        for bad_id in ("X001", "N", "", "001", "N-1"):
            with self.subTest(note_id=bad_id):
                self.write([make_ticket("T001", notes=[note(bad_id)])])
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_duplicate_note_ids_in_one_ticket_are_rejected(self):
        self.write([make_ticket("T001", notes=[note("N001"), note("N001")])])
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_same_note_id_on_different_tickets_is_fine(self):
        self.write([make_ticket("T001", notes=[note("N001")]),
                    make_ticket("T002", notes=[note("N001")])])
        self.assertEqual(len(load_tickets(self.path)), 2)

    def test_ticket_without_notes_loads_with_empty_list(self):
        old_style = make_ticket("T001")
        del old_style["notes"]
        self.write([old_style])
        self.assertEqual(load_tickets(self.path)[0]["notes"], [])

    def test_notes_round_trip(self):
        tickets = [make_ticket("T001", notes=[note("N001"), note("N002")])]
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_ids_continue_after_reload(self):
        self.write([make_ticket("T001"), make_ticket("T005")])
        loaded = load_tickets(self.path)
        new = create_ticket(loaded, "New one", "Other", "low", 1)
        self.assertEqual(new["id"], "T006")


if __name__ == "__main__":
    unittest.main()
