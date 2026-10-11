import os
import tempfile
import unittest

from campusflow.errors import StorageError
from campusflow.storage import load_tickets, save_tickets
from tests.helpers import make_ticket


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "tickets.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_missing_file_is_fresh_start(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_round_trip(self):
        tickets = [make_ticket("T001"), make_ticket("T002", assigned_to="Amina")]
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_malformed_json_raises_and_file_is_not_overwritten(self):
        with open(self.path, "w") as f:
            f.write("{not json")
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path) as f:
            self.assertEqual(f.read(), "{not json")

    def test_json_that_is_not_a_list_is_rejected(self):
        with open(self.path, "w") as f:
            f.write('{"a": 1}')
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_unwritable_path_raises_storage_error(self):
        with self.assertRaises(StorageError):
            save_tickets([], os.path.join(self.dir.name, "missing_folder", "t.json"))


if __name__ == "__main__":
    unittest.main()
