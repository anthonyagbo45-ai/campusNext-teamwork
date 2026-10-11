import unittest

from campusflow.reports import build_report
from tests.helpers import make_ticket


class ReportTests(unittest.TestCase):
    def test_empty_report_has_all_keys_at_zero(self):
        r = build_report([])
        self.assertEqual(r["total"], 0)
        self.assertEqual(r["unassigned"], 0)
        self.assertEqual(r["by_status"], {"open": 0, "in_progress": 0, "resolved": 0})
        self.assertEqual(sum(r["by_priority"].values()), 0)
        self.assertEqual(sum(r["by_category"].values()), 0)

    def test_counts(self):
        tickets = [
            make_ticket("T001", priority="critical", category="Network"),
            make_ticket("T002", status="in_progress", assigned_to="A", priority="low", category="Network"),
            make_ticket("T003", status="resolved", assigned_to="B", priority="low", category="Hardware"),
        ]
        r = build_report(tickets)
        self.assertEqual(r["total"], 3)
        self.assertEqual(r["by_status"], {"open": 1, "in_progress": 1, "resolved": 1})
        self.assertEqual(r["by_priority"]["low"], 2)
        self.assertEqual(r["by_priority"]["critical"], 1)
        self.assertEqual(r["by_category"]["Network"], 2)
        self.assertEqual(r["by_category"]["Hardware"], 1)
        self.assertEqual(r["unassigned"], 1)


if __name__ == "__main__":
    unittest.main()
