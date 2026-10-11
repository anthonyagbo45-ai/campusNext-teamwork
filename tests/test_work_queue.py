import unittest

from campusflow.work_queue import get_work_queue
from tests.helpers import make_ticket


class WorkQueueTests(unittest.TestCase):
    def test_orders_by_priority_then_id_number(self):
        tickets = [make_ticket("T010", priority="low"), make_ticket("T003", priority="critical"),
                   make_ticket("T002", priority="low"), make_ticket("T004", priority="high"),
                   make_ticket("T009", priority="critical")]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T003", "T009", "T004", "T002", "T010"])

    def test_id_numbers_sort_numerically_not_alphabetically(self):
        tickets = [make_ticket("T100"), make_ticket("T020")]
        self.assertEqual([t["id"] for t in get_work_queue(tickets)], ["T020", "T100"])

    def test_resolved_and_in_progress_are_left_out(self):
        tickets = [make_ticket("T001"), make_ticket("T002", status="resolved"),
                   make_ticket("T003", status="in_progress", assigned_to="A")]
        self.assertEqual([t["id"] for t in get_work_queue(tickets)], ["T001"])

    def test_returns_new_list_and_leaves_input_alone(self):
        tickets = [make_ticket("T002"), make_ticket("T001")]
        result = get_work_queue(tickets)
        self.assertIsNot(result, tickets)
        self.assertEqual([t["id"] for t in tickets], ["T002", "T001"])

    def test_empty(self):
        self.assertEqual(get_work_queue([]), [])


if __name__ == "__main__":
    unittest.main()
