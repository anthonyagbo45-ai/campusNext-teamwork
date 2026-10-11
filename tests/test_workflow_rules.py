import unittest

from campusflow.errors import InvalidTransitionError, TicketNotFoundError, ValidationError
from campusflow.workflow import assign_ticket, change_status, reopen_ticket
from tests.helpers import make_ticket


class StatusRuleTests(unittest.TestCase):
    def test_status_text_is_normalised(self):
        tickets = [make_ticket(assigned_to="Amina")]
        change_status(tickets, "T001", "  IN_PROGRESS ")
        self.assertEqual(tickets[0]["status"], "in_progress")

    def test_full_path_open_to_resolved(self):
        tickets = [make_ticket(assigned_to="Amina")]
        change_status(tickets, "T001", "in_progress")
        change_status(tickets, "T001", "resolved")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_resolved_ticket_cannot_change_status(self):
        tickets = [make_ticket(status="resolved", assigned_to="Amina")]
        with self.assertRaises(InvalidTransitionError):
            change_status(tickets, "T001", "open")

    def test_resolved_ticket_cannot_be_assigned(self):
        tickets = [make_ticket(status="resolved", assigned_to="Amina")]
        with self.assertRaises(InvalidTransitionError):
            assign_ticket(tickets, "T001", "Bola")
        self.assertEqual(tickets[0]["assigned_to"], "Amina")

    def test_unknown_id_is_checked_before_bad_status(self):
        with self.assertRaises(TicketNotFoundError):
            change_status([make_ticket()], "T999", "nonsense")

    def test_bad_status_is_checked_before_state(self):
        tickets = [make_ticket(status="resolved")]
        with self.assertRaises(ValidationError):
            change_status(tickets, "T001", "nonsense")

    def test_non_text_status_is_rejected(self):
        with self.assertRaises(ValidationError):
            change_status([make_ticket()], "T001", None)


class ReopenTests(unittest.TestCase):
    def test_reopen_sets_status_to_open(self):
        tickets = [make_ticket(status="resolved", assigned_to="Amina")]
        reopen_ticket(tickets, "t001")
        self.assertEqual(tickets[0]["status"], "open")

    def test_reopen_open_ticket_is_rejected(self):
        with self.assertRaises(InvalidTransitionError):
            reopen_ticket([make_ticket()], "T001")

    def test_reopen_unknown_id(self):
        with self.assertRaises(TicketNotFoundError):
            reopen_ticket([make_ticket()], "T404")


if __name__ == "__main__":
    unittest.main()
