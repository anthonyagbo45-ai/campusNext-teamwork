import json
import os
import tempfile
import unittest

from campusflow.errors import StorageError
from campusflow.storage import load_tickets, save_tickets
from tests.helpers import make_ticket


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "tickets.json")

    def tearDown(self):
        self.dir.cleanup()

    def _write(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f)

    def test_empty_list_round_trips(self):
        save_tickets([], self.path)
        self.assertEqual(load_tickets(self.path), [])

    def test_save_does_not_leave_a_temp_file(self):
        save_tickets([make_ticket()], self.path)
        self.assertEqual(os.listdir(self.dir.name), ["tickets.json"])

    def test_item_that_is_not_a_ticket_is_rejected(self):
        self._write(["oops"])
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_ticket_missing_a_field_is_rejected(self):
        broken = make_ticket()
        del broken["status"]
        self._write([broken])
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_unknown_status_in_file_is_rejected(self):
        self._write([make_ticket(status="done")])
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_bad_file_is_left_untouched_after_failed_load(self):
        self._write([{"id": "T001"}])
        before = open(self.path).read()
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        self.assertEqual(open(self.path).read(), before)

    def test_ids_stay_unique_after_reload(self):
        from campusflow.tickets import create_ticket
        tickets = []
        create_ticket(tickets, "a", "Other", "low", 1)
        save_tickets(tickets, self.path)
        reloaded = load_tickets(self.path)
        self.assertEqual(create_ticket(reloaded, "b", "Other", "low", 1)["id"], "T002")


if __name__ == "__main__":
    unittest.main()
