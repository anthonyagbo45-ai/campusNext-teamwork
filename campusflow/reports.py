from campusflow.constants import CATEGORIES, PRIORITIES, STATUSES


def build_report(tickets):
    """Counts for the Head of Campus. Every ticket is counted once, by CURRENT status."""
    report = {
        "total": len(tickets),
        "by_status": {s: 0 for s in STATUSES},
        "by_priority": {p: 0 for p in PRIORITIES},
        "by_category": {c: 0 for c in CATEGORIES},
        "unassigned": 0,
    }
    for ticket in tickets:
        report["by_status"][ticket["status"]] += 1
        report["by_priority"][ticket["priority"]] += 1
        report["by_category"][ticket["category"]] += 1
        if not ticket["assigned_to"]:
            report["unassigned"] += 1
    resolved = report["by_status"]["resolved"]
    report["resolved"] = resolved
    report["unresolved"] = report["by_status"]["open"] + report["by_status"]["in_progress"]
    # An empty dataset reports 0 percent, never a division by zero.
    report["resolution_percentage"] = (
        round(resolved / report["total"] * 100, 1) if report["total"] else 0.0
    )
    return report
