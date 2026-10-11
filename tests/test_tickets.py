import unittest

from campusflow.errors import TicketNotFoundError, ValidationError
from campusflow.tickets import compute_priority, create_ticket, list_tickets, view_ticket
from tests.helpers import make_ticket


class CreateTicketTests(unittest.TestCase):
    def test_creates_open_unassigned_ticket(self):
        tickets = []
        t = create_ticket(tickets, "  Wi-Fi down ", " network ", "HIGH", 60)
        self.assertEqual(t["id"], "T001")
        self.assertEqual(t["title"], "Wi-Fi down")
        self.assertEqual(t["category"], "Network")
        self.assertEqual(t["urgency"], "high")
        self.assertEqual(t["priority"], "critical")
        self.assertEqual(t["status"], "open")
        self.assertIsNone(t["assigned_to"])
        self.assertEqual(tickets, [t])

    def test_next_id_is_highest_plus_one(self):
        tickets = [make_ticket("T001"), make_ticket("T007")]
        self.assertEqual(create_ticket(tickets, "x", "Other", "low", 1)["id"], "T008")

    def test_invalid_inputs_raise_validation_error(self):
        bad = [("  ", "Other", "low", 1), ("x", "Plumbing", "low", 1),
               ("x", "Other", "urgent", 1), ("x", "Other", "low", 0),
               ("x", "Other", "low", -3), ("x", "Other", "low", 2.5),
               ("x", "Other", "low", True), ("x", "Other", "low", "5"),
               (None, "Other", "low", 1)]
        for args in bad:
            with self.subTest(args=args):
                tickets = []
                with self.assertRaises(ValidationError):
                    create_ticket(tickets, *args)
                self.assertEqual(tickets, [])


class PriorityTests(unittest.TestCase):
    def test_rules(self):
        cases = [("high", 10, "critical"), ("high", 60, "critical"), ("high", 9, "high"),
        ("low", 10, "high"), ("medium", 10, "high"), ("medium", 9, "medium"),
        ("low", 3, "medium"), ("low", 9, "medium"), ("medium", 1, "medium"),
        ("low", 2, "low"), ("low", 1, "low")]
        for urgency, users, expected in cases:
            with self.subTest(urgency=urgency, users=users):
                self.assertEqual(compute_priority(urgency, users), expected)


class ListViewTests(unittest.TestCase):
    def test_list_is_sorted_copy(self):
        tickets = [make_ticket("T010"), make_ticket("T002")]
        result = list_tickets(tickets)
        self.assertEqual([t["id"] for t in result], ["T002", "T010"])
        self.assertEqual([t["id"] for t in tickets], ["T010", "T002"])

    def test_view_is_case_and_space_tolerant(self):
        tickets = [make_ticket("T001")]
        self.assertIs(view_ticket(tickets, " t001 "), tickets[0])

    def test_view_unknown_id(self):
        with self.assertRaises(TicketNotFoundError):
            view_ticket([make_ticket()], "T999")


if __name__ == "__main__":
    unittest.main()
