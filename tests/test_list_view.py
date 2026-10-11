import unittest

from campusflow.errors import TicketNotFoundError, ValidationError
from campusflow.tickets import list_tickets, view_ticket
from tests.helpers import make_ticket


class ListFilterTests(unittest.TestCase):
    def setUp(self):
        self.tickets = [make_ticket("T003", status="resolved", assigned_to="A"),
                        make_ticket("T001"),
                        make_ticket("T002", status="in_progress", assigned_to="B")]

    def test_no_filter_returns_all_in_id_order(self):
        self.assertEqual([t["id"] for t in list_tickets(self.tickets)], ["T001", "T002", "T003"])

    def test_status_filter_is_case_and_space_tolerant(self):
        self.assertEqual([t["id"] for t in list_tickets(self.tickets, " IN_PROGRESS ")], ["T002"])

    def test_unknown_status_filter_is_rejected(self):
        with self.assertRaises(ValidationError):
            list_tickets(self.tickets, "done")

    def test_list_does_not_change_the_input(self):
        list_tickets(self.tickets)
        self.assertEqual([t["id"] for t in self.tickets], ["T003", "T001", "T002"])

    def test_empty_list(self):
        self.assertEqual(list_tickets([]), [])


class ViewTests(unittest.TestCase):
    def test_view_returns_the_same_ticket_object(self):
        tickets = [make_ticket("T001"), make_ticket("T002")]
        self.assertIs(view_ticket(tickets, "t002"), tickets[1])

    def test_view_non_text_id(self):
        with self.assertRaises(TicketNotFoundError):
            view_ticket([make_ticket()], None)


if __name__ == "__main__":
    unittest.main()
