import os
import tempfile
import unittest

from campusflow.cli import run
from campusflow.storage import load_tickets


def drive(path, answers):
    feed = iter(answers)
    lines = []
    run(path, ask=lambda prompt: next(feed), out=lines.append, check_notes_path=os.devnull)
    return "\n".join(lines)


class OptionMenuTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "t.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_create_shows_numbered_category_and_urgency_choices_with_hints(self):
        output = drive(self.path, ["1", "Projector broken", "2", "3", "5", "0"])
        for expected in ("1) Network", "2) Hardware", "3) Software", "4) Other",
                         "laptops, desktops, printers", "1) low", "3) high"):
            self.assertIn(expected, output)

    def test_numbers_pick_the_right_values(self):
        drive(self.path, ["1", "Projector broken", "2", "3", "12", "0"])
        ticket = load_tickets(self.path)[0]
        self.assertEqual((ticket["category"], ticket["urgency"]), ("Hardware", "high"))
        self.assertEqual(ticket["priority"], "critical")

    def test_names_still_work_in_any_case(self):
        drive(self.path, ["1", "App will not install", " SOFTWARE ", "Medium", "1", "0"])
        ticket = load_tickets(self.path)[0]
        self.assertEqual((ticket["category"], ticket["urgency"]), ("Software", "medium"))

    def test_invalid_choice_is_asked_again_not_a_crash(self):
        output = drive(self.path, ["1", "Wi-Fi down", "9", "plumbing", "1", "0", "3", "4", "0"])
        self.assertEqual(output.count("Error: Invalid category"), 2)
        self.assertEqual(output.count("Error: Invalid urgency"), 1)
        ticket = load_tickets(self.path)[0]
        self.assertEqual((ticket["category"], ticket["urgency"]), ("Network", "high"))

    def test_search_choices_allow_blank_for_any(self):
        drive(self.path, ["1", "Wi-Fi down", "1", "3", "5", "0"])
        output = drive(self.path, ["11", "", "", "", "", "n", "0"])
        self.assertIn("(press Enter for any)", output)
        self.assertIn("T001 | Wi-Fi down | Network | high | open | unassigned", output)

    def test_search_by_priority_number(self):
        drive(self.path, ["1", "Wi-Fi down", "1", "3", "12", "0"])
        drive(self.path, ["1", "Printer jam", "2", "1", "1", "0"])
        output = drive(self.path, ["11", "", "", "", "1", "n", "0"])   # priority 1 = critical
        self.assertIn("Wi-Fi down", output)
        self.assertNotIn("Printer jam", output)


if __name__ == "__main__":
    unittest.main()
