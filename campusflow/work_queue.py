from campusflow.constants import PRIORITY_RANK
from campusflow.ids import id_number

# Decision: the queue shows work nobody has finished starting. Add "in_progress" here to include it.
QUEUE_STATUSES = ("open",)


def get_work_queue(tickets):
    """Return a NEW list: critical -> low, ties by earlier ID number."""
    waiting = [t for t in tickets if t["status"] in QUEUE_STATUSES]
    return sorted(waiting, key=lambda t: (PRIORITY_RANK[t["priority"]], id_number(t["id"])))
