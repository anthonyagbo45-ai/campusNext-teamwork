# AI learning log

This log records how each engineer used AI to learn, and how each AI claim was checked
before it went into the code.

## AI assistance disclosure (team)

- Claude (an AI assistant) was used throughout CampusFlow and CampusFlow Next for
  explanations, test ideas, code review and code drafts.
- Engineer A (Anthony): `validation.py`, `notes.py` and the checked load in `storage.py`
  were written by Anthony, using failing tests first. Claude supplied the test file for notes
  (`tests/test_notes.py`) and hints about the order of checks.
- Engineer B (Chekube): `search.py`, the report additions, `understanding_check.py`, the menu
  additions in `cli.py` and their tests were drafted with Claude in a session run by Anthony.
  Chekube ran the tests and pushed them as PR #18, and Anthony reviewed that pull request.
- Every AI suggestion that went into the code was run through
  `python3 -m unittest discover -s tests -v` before being committed.

---

## Engineer A: Anthony

### Cycle 1: booleans pass an "is it an integer" check

- **Concept gap:** I did not know that in Python `True` counts as an integer, so a check
  like `isinstance(value, int)` accepts `True` as a number of affected users.
- **Exact question I asked:** I did not type this question word for word. The topic came
  from the guide's practice item about `isinstance(True, int)`, and the AI explained it as a
  hint while I was writing the test for `validate_affected_users`.
- **AI guidance (summary):** `bool` is a subclass of `int`, so `isinstance(True, int)` is
  `True`. To reject booleans, test for `bool` first and only then test for `int`, then
  check the value is 1 or more.
- **Tiny unrelated experiment:** I ran `python3 -c "print(isinstance(True, int), True + True)"`
  and it printed `True 2`. So `True` really behaves as the number 1.
- **Independent verification:** `tests/test_validation.py` rejects `0`, `-3`, `2.5`,
  `"5"` and `True`. The tests failed first (`ModuleNotFoundError` for `campusflow.validation`),
  then passed after I wrote `validate_affected_users`.
- **Final engineering decision:** `validate_affected_users` checks `bool` before `int` and is
  used by `create_ticket`, so the rule lives in one place.
- **Reflection:** I thought `True` was not a number. Now I know `bool` is a kind of `int`, so I
  check for `bool` first. `test_rejects_bad_values` guards it, and I can explain it without AI.

### Cycle 2: validate before you change anything (notes)

- **Concept gap:** I needed `add_note` to reject bad input without leaving a half-changed
  ticket or using up a note ID.
- **Exact question I asked:** I did not type this question word for word. The topic came
  from the guide's "validate before mutate" concept, and the AI explained the order of checks
  when I started on `add_note`.
- **AI guidance (summary):** check in a fixed order (find the ticket, validate the input,
  check the ticket's state) and only build and append the note after all three checks pass.
  A rejected action then cannot change the data.
- **Tiny unrelated experiment:** I wrote a small library function that lowers `book["copies"]`
  by 1 and then checks the request. With a bad request (`0`), it raised the error, and
  `print(book)` printed `{'copies': 0}`. The request was rejected but the data had already
  changed, because the change came before the check. That is the bug the check order prevents.
- **Independent verification:** `tests/test_notes.py` has
  `test_rejected_note_changes_nothing_and_does_not_use_an_id` (a `copy.deepcopy` snapshot is
  compared after the failed call), `test_resolved_ticket_rejects_note_and_stays_unchanged`
  and `test_check_order_find_then_validate_then_state`. The first run failed with
  `No module named 'campusflow.notes'`, then passed.
- **Final engineering decision:** `notes.add_note` appends only at the last step, and
  `next_note_id` uses the highest existing note number plus 1.
- **Reflection:** I thought rejecting bad input was enough. Now I know nothing may change until
  every check has passed. `test_rejected_note_changes_nothing_and_does_not_use_an_id` guards it.

---

## Engineer B: Chekube

Chekube's two learning cycles will be added in a separate pull request. They were not
completed before this submission.

---

## Team: an AI suggestion that was changed after checking the evidence

**First version of CampusFlow: invented priority thresholds.**

- **What the AI suggested:** a priority rule using 50 and 20 affected users as the
  thresholds for critical and high.
- **What the evidence showed:** the assignment's rules say 10 or more users for critical
  and high, and 3 or more for medium. The AI had invented numbers that were not in the brief.
  The CLI run showed a ticket with high urgency and 12 users as `[high]` instead of `[critical]`.
- **What we did:** replaced `compute_priority` with the rules from the brief and rewrote the
  boundary tests in `tests/test_tickets.py` (10 versus 9 users, 3 versus 2 users).
- **Lesson:** an AI answer is a claim to check against the brief and against tests, not a fact.

**CampusFlow Next: an old test that had to change.** Adding the `notes` field made the
old test `test_new_ticket_has_all_eight_fields` fail. The code was right and the test described the old
ticket shape, so we updated the test to nine fields and kept it as regression evidence.

## Individual reflections (one verified mistake, one learning gain, one improvement from review)

- **Anthony:**
  - *Verified mistake:* I pasted a script into the terminal with the closing `EOF` indented, so
    the terminal stayed stuck at `heredoc>`. I fixed it by putting the script in a file instead.
  - *Learning gain:* booleans are integers in Python, so validation must reject `bool` before
    it checks for `int`.
  - *Improvement from review:* a check of PR #18 after it was merged found three inputs that
    still crash the menu (a superscript digit as a menu choice, Ctrl+C at a sub-prompt, and an
    unwritable notes file) even though all 144 tests passed. Passing tests do not mean every
    input is covered, so I am fixing them in a follow-up pull request with a test for each.
- **Chekube:** to be added by Chekube.
