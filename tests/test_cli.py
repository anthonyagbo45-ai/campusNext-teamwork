import os
import tempfile
import unittest

from campusflow.cli import run
from campusflow.storage import load_tickets


def drive(path, answers):
    feed = iter(answers)
    lines = []
    run(path, ask=lambda prompt: next(feed), out=lines.append)
    return "\n".join(lines)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "t.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_create_assign_progress_and_persist(self):
        output = drive(self.path, ["1", "Wi-Fi down", "network", "high", "60",
                                   "4", "t001", "Amina", "5", "T001", "in_progress",
                                   "7", "8", "0"])
        self.assertIn("Created T001 [critical]", output)
        self.assertIn("Total: 1", output)
        self.assertEqual(load_tickets(self.path)[0]["status"], "in_progress")

    def test_errors_are_printed_not_raised(self):
        output = drive(self.path, ["1", "x", "Other", "low", "abc", "5", "T404", "open",
                                   "99", "0"])
        self.assertIn("Error: affected_users must be a positive whole number.", output)
        self.assertIn("Error: No ticket with ID 'T404'", output)
        self.assertIn("Please choose a number", output)

    def test_malformed_file_stops_with_clear_error(self):
        with open(self.path, "w") as f:
            f.write("oops")
        self.assertIn("Error:", drive(self.path, []))

    def test_reload_keeps_ids_unique(self):
        drive(self.path, ["1", "a", "Other", "low", "1", "0"])
        drive(self.path, ["1", "b", "Other", "low", "1", "0"])
        self.assertEqual([t["id"] for t in load_tickets(self.path)], ["T001", "T002"])


if __name__ == "__main__":
    unittest.main()
