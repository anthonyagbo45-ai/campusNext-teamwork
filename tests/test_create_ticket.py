import unittest

from campusflow.errors import ValidationError
from campusflow.tickets import create_ticket


class CreateTicketRuleTests(unittest.TestCase):
    def test_new_ticket_has_all_eight_fields(self):
        t = create_ticket([], "Printer jammed", "Hardware", "medium", 4)
        self.assertEqual(set(t), {"id", "title", "category", "urgency", "affected_users",
                                  "priority", "status", "assigned_to"})

    def test_category_and_urgency_are_case_and_space_tolerant(self):
        t = create_ticket([], "x", "  sOfTwArE ", "  MEDIUM ", 1)
        self.assertEqual((t["category"], t["urgency"]), ("Software", "medium"))

    def test_ids_increase_one_by_one(self):
        tickets = []
        ids = [create_ticket(tickets, "x", "Other", "low", 1)["id"] for _ in range(3)]
        self.assertEqual(ids, ["T001", "T002", "T003"])

    def test_rejected_ticket_does_not_use_up_an_id(self):
        tickets = []
        with self.assertRaises(ValidationError):
            create_ticket(tickets, "x", "Other", "low", 0)
        self.assertEqual(create_ticket(tickets, "x", "Other", "low", 1)["id"], "T001")

    def test_priority_is_set_by_the_agreed_rules(self):
        self.assertEqual(create_ticket([], "x", "Network", "high", 10)["priority"], "critical")
        self.assertEqual(create_ticket([], "x", "Network", "low", 3)["priority"], "medium")
        self.assertEqual(create_ticket([], "x", "Network", "low", 2)["priority"], "low")


if __name__ == "__main__":
    unittest.main()
