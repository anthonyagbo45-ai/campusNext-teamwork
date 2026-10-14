def make_ticket(ticket_id="T001", status="open", assigned_to=None, priority="low",
                category="Other", urgency="low", affected_users=1, notes=None):
    return {
        "id": ticket_id, "title": "Example", "category": category,
        "urgency": urgency, "affected_users": affected_users, "priority": priority,
        "status": status, "assigned_to": assigned_to,
        "notes": notes if notes is not None else [],
    }