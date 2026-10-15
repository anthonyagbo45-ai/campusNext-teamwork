import os
import tempfile
import unittest

from campusflow.cli import run
from campusflow.storage import load_tickets


def drive(path, answers, notes_path=None):
    feed = iter(answers)
    lines = []
    run(path, ask=lambda prompt: next(feed), out=lines.append,
        check_notes_path=notes_path or os.devnull)
    return "\n".join(lines)


class CliNextTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "t.json")

    def tearDown(self):
        self.dir.cleanup()

    def _two_tickets(self):
        drive(self.path, ["1", "Wi-Fi down", "network", "high", "12",
                          "1", "Projector broken", "hardware", "low", "1", "0"])

    def test_add_and_view_notes_survive_a_restart(self):
        self._two_tickets()
        drive(self.path, ["9", "T001", "Mentor A", "Router reboot attempted",
                          "9", "T001", "Mentor B", "Investigating switch ports", "0"])
        output = drive(self.path, ["10", "T001", "0"])
        self.assertLess(output.index("N001 [Mentor A]"), output.index("N002 [Mentor B]"))
        self.assertEqual(len(load_tickets(self.path)[0]["notes"]), 2)

    def test_rejected_note_shows_friendly_error_and_uses_no_id(self):
        self._two_tickets()
        output = drive(self.path, ["9", "T001", "Mentor A", "hi",
                                   "9", "T001", "Mentor A", "A proper note", "0"])
        self.assertIn("Error: Note message must be between 5 and 300 characters.", output)
        self.assertIn("Added note N001.", output)

    def test_note_on_resolved_ticket_is_refused_in_the_menu(self):
        self._two_tickets()
        output = drive(self.path, ["4", "T001", "Amina", "5", "T001", "in_progress",
                                   "5", "T001", "resolved",
                                   "9", "T001", "Mentor A", "Trying after resolve", "0"])
        self.assertIn("is resolved. Reopen it before adding notes.", output)

    def test_search_combines_filters_and_shows_the_required_columns(self):
        self._two_tickets()
        output = drive(self.path, ["11", "wi-fi", "network", "open", "", "n", "0"])
        self.assertIn("T001 | Wi-Fi down | Network | critical | open | unassigned", output)
        self.assertNotIn("Projector", output)

    def test_search_reprompts_on_invalid_filter(self):
        self._two_tickets()
        output = drive(self.path, ["11", "", "plumbing", "hardware", "", "", "n", "0"])
        self.assertIn("Error: Invalid category 'plumbing'", output)
        self.assertIn("Projector broken", output)

    def test_search_does_not_save_or_change_anything(self):
        self._two_tickets()
        with open(self.path) as handle:
            before = handle.read()
        drive(self.path, ["11", "", "", "", "", "y", "0"])
        with open(self.path) as handle:
            self.assertEqual(handle.read(), before)

    def test_report_shows_percentage(self):
        self._two_tickets()
        self.assertIn("Resolution: 0.0%", drive(self.path, ["8", "0"]))
        self.assertIn("Total: 0", drive(os.path.join(self.dir.name, "empty.json"), ["8", "0"]))

    def test_understanding_check_runs_from_the_menu(self):
        notes = os.path.join(self.dir.name, "notes.md")
        script = ["12", "B", "Because it protects data.", "C", "Zero tickets must show 0 percent.",
                  "B", "C", "C", "B", "0"]
        output = drive(self.path, script, notes_path=notes)
        self.assertIn("Final score: 6/6", output)
        self.assertTrue(os.path.exists(notes))

    def test_ctrl_c_leaves_politely_instead_of_a_traceback(self):
        def ask(prompt):
            raise KeyboardInterrupt
        lines = []
        run(self.path, ask=ask, out=lines.append)
        self.assertIn("Goodbye.", "\n".join(lines))

    def test_end_of_input_leaves_politely(self):
        def ask(prompt):
            raise EOFError
        lines = []
        run(self.path, ask=ask, out=lines.append)
        self.assertIn("Goodbye.", "\n".join(lines))

    def test_invalid_menu_choices_are_rejected(self):
        output = drive(self.path, ["13", "abc", "", "0"])
        self.assertEqual(output.count("Please choose a number from the menu."), 3)


if __name__ == "__main__":
    unittest.main()
