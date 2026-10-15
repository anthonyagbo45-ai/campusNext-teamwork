import unittest

from campusflow.reports import build_report
from campusflow.work_queue import get_work_queue
from campusflow.workflow import assign_ticket, change_status, reopen_ticket
from tests.helpers import make_ticket


def fixture():
    return [make_ticket("T001", category="Network", priority="critical"),
            make_ticket("T002", category="Network", priority="high"),
            make_ticket("T003", category="Hardware", priority="low"),
            make_ticket("T004", category="Other", priority="low")]


class ReportInsightTests(unittest.TestCase):
    def test_empty_report_is_zero_percent_without_crashing(self):
        r = build_report([])
        self.assertEqual((r["total"], r["resolved"], r["unresolved"]), (0, 0, 0))
        self.assertEqual(r["resolution_percentage"], 0)

    def test_percentage_is_resolved_over_total(self):
        tickets = fixture()
        assign_ticket(tickets, "T001", "Amina")
        change_status(tickets, "T001", "in_progress")
        change_status(tickets, "T001", "resolved")
        r = build_report(tickets)
        self.assertEqual((r["resolved"], r["unresolved"], r["total"]), (1, 3, 4))
        self.assertEqual(r["resolution_percentage"], 25.0)

    def test_in_progress_counts_as_unresolved(self):
        tickets = fixture()
        assign_ticket(tickets, "T002", "Amina")
        change_status(tickets, "T002", "in_progress")
        r = build_report(tickets)
        self.assertEqual(r["unresolved"], 4)
        self.assertEqual(r["by_status"], {"open": 3, "in_progress": 1, "resolved": 0})

    def test_counts_follow_current_status_after_resolve_and_reopen(self):
        tickets = fixture()
        assign_ticket(tickets, "T001", "Amina")
        change_status(tickets, "T001", "in_progress")
        change_status(tickets, "T001", "resolved")
        self.assertEqual(build_report(tickets)["by_status"]["resolved"], 1)
        reopen_ticket(tickets, "T001")
        r = build_report(tickets)
        self.assertEqual(r["by_status"], {"open": 4, "in_progress": 0, "resolved": 0})
        self.assertEqual(r["resolution_percentage"], 0)

    def test_every_ticket_is_counted_exactly_once(self):
        r = build_report(fixture())
        for key in ("by_status", "by_priority", "by_category"):
            with self.subTest(group=key):
                self.assertEqual(sum(r[key].values()), r["total"])
        self.assertEqual(r["resolved"] + r["unresolved"], r["total"])

    def test_original_work_queue_still_shows_only_open_tickets(self):
        tickets = fixture()
        assign_ticket(tickets, "T001", "Amina")
        change_status(tickets, "T001", "in_progress")
        self.assertEqual([t["id"] for t in get_work_queue(tickets)], ["T002", "T003", "T004"])


if __name__ == "__main__":
    unittest.main()
