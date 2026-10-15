import copy
import unittest

from campusflow.errors import ValidationError
from campusflow.search import search_tickets, sort_by_priority
from tests.helpers import make_ticket


def sample():
    a = make_ticket("T001", category="Network", priority="critical")
    a["title"] = "Wi-Fi down in Lab 2"
    b = make_ticket("T002", category="Network", status="in_progress", assigned_to="Amina", priority="high")
    b["title"] = "wi-fi slow in library"
    c = make_ticket("T010", category="Hardware", priority="low")
    c["title"] = "Projector will not start"
    d = make_ticket("T003", category="Network", priority="low")
    d["title"] = "Printer offline"
    return [c, b, a, d]


def ids(tickets):
    return [t["id"] for t in tickets]


class SearchTests(unittest.TestCase):
    def test_title_search_ignores_case_and_matches_part_of_a_word(self):
        self.assertEqual(ids(search_tickets(sample(), "WI-FI")), ["T001", "T002"])
        self.assertEqual(ids(search_tickets(sample(), "  lab ")), ["T001"])

    def test_no_filters_returns_everything_in_id_order(self):
        self.assertEqual(ids(search_tickets(sample())), ["T001", "T002", "T003", "T010"])

    def test_combined_filters_use_and_not_or(self):
        result = search_tickets(sample(), "wi-fi", "network", "open")
        self.assertEqual(ids(result), ["T001"])          # T002 is network+wifi but in_progress

    def test_each_filter_works_alone(self):
        self.assertEqual(ids(search_tickets(sample(), category="hardware")), ["T010"])
        self.assertEqual(ids(search_tickets(sample(), status="IN_PROGRESS")), ["T002"])
        self.assertEqual(ids(search_tickets(sample(), priority=" Low ")), ["T003", "T010"])

    def test_blank_and_none_filters_mean_do_not_filter(self):
        self.assertEqual(len(search_tickets(sample(), "", "", "  ", None)), 4)

    def test_no_match_returns_empty_list(self):
        self.assertEqual(search_tickets(sample(), "nothing like this"), [])

    def test_invalid_filter_is_rejected(self):
        for kwargs in ({"category": "Plumbing"}, {"status": "done"}, {"priority": "urgent"},
                       {"category": 5}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValidationError):
                    search_tickets(sample(), **kwargs)

    def test_search_never_changes_the_tickets(self):
        tickets = sample()
        before = copy.deepcopy(tickets)
        search_tickets(tickets, "wi-fi", "network", "open", "critical")
        self.assertEqual(tickets, before)

    def test_search_returns_a_new_list(self):
        tickets = sample()
        self.assertIsNot(search_tickets(tickets), tickets)


class SortByPriorityTests(unittest.TestCase):
    def test_priority_then_numeric_id(self):
        tickets = [make_ticket("T10", priority="high"), make_ticket("T2", priority="high"),
                   make_ticket("T5", priority="critical"), make_ticket("T1", priority="low")]
        self.assertEqual(ids(sort_by_priority(tickets)), ["T5", "T2", "T10", "T1"])

    def test_sort_does_not_change_input_order(self):
        tickets = [make_ticket("T2", priority="low"), make_ticket("T1", priority="critical")]
        sort_by_priority(tickets)
        self.assertEqual(ids(tickets), ["T2", "T1"])


if __name__ == "__main__":
    unittest.main()
