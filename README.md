# CampusFlow

A command-line IT support ticket tracker, written in Python 3 with no outside packages.

## Requirements

- Python 3.9 or newer (check with `python3 --version`)

## How to run it from the zip

    unzip campusflow-teamwork.zip
    cd campusflow-teamwork
    python3 -m campusflow

Tickets are saved in `tickets.json` in the current folder. To use a different file:

    python3 -m campusflow mytickets.json

If `tickets.json` does not exist, the program starts with no tickets.

## Menu

| Choice | Action |
|---|---|
| 1 | Create ticket |
| 2 | List tickets |
| 3 | View ticket |
| 4 | Assign ticket |
| 5 | Change status |
| 6 | Reopen ticket |
| 7 | Work queue |
| 8 | Report |
| 9 | Add follow-up note |
| 10 | View ticket notes |
| 11 | Search tickets |
| 12 | Understanding check |
| 0 | Exit |

## How to run the tests

    python3 -m unittest discover -s tests -v

All tests should pass (`OK`).

## Rules

- Status flow: open -> in_progress -> resolved.
- A ticket must be assigned before it can move to in_progress.
- A resolved ticket cannot change until it is reopened (reopening sets it to open).
- Priority, checked in order, first match wins:
  1. high urgency and 10 or more affected users: critical
  2. high urgency or 10 or more affected users: high
  3. medium urgency or 3 or more affected users: medium
  4. everything else: low
- Work queue: open tickets only, ordered critical to low, ties broken by earlier ID number.
- Ticket IDs look like T001. Case and spaces are ignored when you type an ID.
- Category, urgency and status ignore case and extra spaces.
- Notes: a note can be added only while a ticket is open or in_progress. Message 5 to 300 characters after trimming. Note IDs (N001, N002 ...) count per ticket, and a rejected note uses no ID.
- Search: title text (any case, part of a word) plus optional category, status and priority. Every supplied filter must match (AND). A blank filter means any. Search never changes tickets. Results can be sorted by priority, then numeric ticket ID.
- Report: total, counts by status, priority and category, resolved, unresolved (open + in_progress) and resolution percentage. An empty list shows 0%.
- Creating a ticket and searching show numbered choices for category (Network, Hardware, Software, Other), urgency (low, medium, high) and status/priority, each with a short hint. Type the number or the name.
- Understanding check: menu option 12, six questions (A/B/C/D), score 0 to 6, and two short explanations saved to `understanding-check-notes.md`.

## Project layout

    campusflow/
      constants.py   shared categories, urgency levels, statuses, priorities
      errors.py      shared error types
      ids.py         ticket ID helpers
      tickets.py     create, list and view tickets
      workflow.py    assign, change status, reopen
      work_queue.py  sorted work queue
      reports.py     report counts and resolution percentage
      search.py      combined search filters and priority sort
      notes.py       follow-up notes
      validation.py  shared input checks
      understanding_check.py  question bank, scoring and the quiz
      storage.py     load and save tickets.json
      cli.py         menu (the only file that calls input())
    tests/           unit tests for every module
    docs/design-decisions.md   the agreed design

## Team

- Anthony: assign, status workflow, work queue, reports, CLI menu
- Nese: create, list/view, persistence
