import unittest

from campusflow.errors import TicketNotFoundError, ValidationError
from campusflow.workflow import assign_ticket, change_status


def make_ticket(ticket_id="T001", status="open", assigned_to=None):
    return {
        "id": ticket_id, "title": "Example", "category": "Other",
        "urgency": "low", "affected_users": 1, "priority": "low",
        "status": status, "assigned_to": assigned_to,
    }


class AssignTicketTests(unittest.TestCase):
    def test_assign_sets_staff_name_on_the_right_ticket(self):
        tickets = [make_ticket("T001"), make_ticket("T002")]
        assign_ticket(tickets, "T002", "Amina")
        self.assertEqual(tickets[1]["assigned_to"], "Amina")
        self.assertIsNone(tickets[0]["assigned_to"])

    def test_unknown_ticket_id_is_rejected(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(TicketNotFoundError):
            assign_ticket(tickets, "T999", "Amina")

    def test_blank_staff_name_is_rejected(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValidationError):
            assign_ticket(tickets, "T001", "   ")
        self.assertIsNone(tickets[0]["assigned_to"])

    def test_non_text_staff_name_is_rejected(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValidationError):
            assign_ticket(tickets, "T001", None)
        self.assertIsNone(tickets[0]["assigned_to"])

    def test_staff_name_is_stored_without_extra_spaces(self):
        tickets = [make_ticket("T001")]
        assign_ticket(tickets, "T001", "  Amina  ")
        self.assertEqual(tickets[0]["assigned_to"], "Amina")

    def test_ticket_id_is_case_and_space_tolerant(self):
        tickets = [make_ticket("T001")]
        assign_ticket(tickets, "  t001 ", "Amina")
        self.assertEqual(tickets[0]["assigned_to"], "Amina")

    def test_unknown_id_is_checked_before_blank_name(self):
        with self.assertRaises(TicketNotFoundError):
            assign_ticket([], "T999", "   ")

class ChangeStatusTests(unittest.TestCase):
    def test_assigned_ticket_moves_to_in_progress(self):
        tickets = [make_ticket("T001", assigned_to="Amina")]
        change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "in_progress")


if __name__ == "__main__":
    unittest.main()
