# AI learning log

This log records how each engineer used AI to learn, and how each AI claim was checked
before it went into the code. Lines marked **[FILL IN]** must be completed by the engineer
from what they actually did. Do not leave a marker in the final submission, and do not
write an experiment you did not run.

## AI assistance disclosure (team)

- Claude (an AI assistant) was used throughout CampusFlow and CampusFlow Next for
  explanations, test ideas, code review and code drafts.
- Engineer A (Anthony): wrote `validation.py`, `notes.py` and the checked load in
  `storage.py` himself, using failing tests first. Claude supplied the test files for
  notes and hints about check order. **[FILL IN: confirm this matches what you did.]**
- Engineer B (Chekube): `search.py`, the report additions, `understanding_check.py`, the
  menu additions in `cli.py` (including the numbered option lists) and their tests were drafted
  with Claude, then read, run and reviewed by Chekube. **[FILL IN: confirm, and list anything
  you changed yourself.]**
- Every AI suggestion that went into the code was run through `python3 -m unittest
  discover -s tests -v` before being committed.

---

## Engineer A: Anthony

### Cycle 1: booleans pass an "is it an integer" check

- **Concept gap:** I did not know that in Python `True` counts as an integer, so a check
  like `isinstance(value, int)` accepts `True` as a number of affected users.
- **Exact question I asked:** **[FILL IN: paste your question word for word.]**
- **AI guidance (summary):** `bool` is a subclass of `int`, so `isinstance(True, int)` is
  `True`. To reject booleans, test for `bool` first and only then test for `int`, then
  check the value is 1 or more.
- **Tiny unrelated experiment:** **[FILL IN: run `python3 -c "print(isinstance(True, int), True + True)"`
  or a similar example with a library book count, and paste what it printed.]**
- **Independent verification:** `tests/test_validation.py` rejects `0`, `-3`, `2.5`,
  `"5"` and `True`. The tests failed first (`ModuleNotFoundError` for `campusflow.validation`),
  then passed after I wrote `validate_affected_users`.
- **Final engineering decision:** `validate_affected_users` checks `bool` before `int` and is
  used by `create_ticket`, so the rule lives in one place.
- **Reflection:** **[FILL IN: what I believed before, what changed, which test guards it, could
  I explain it without AI?]**

### Cycle 2: validate before you change anything (notes)

- **Concept gap:** I needed `add_note` to reject bad input without leaving a half-changed
  ticket or using up a note ID.
- **Exact question I asked:** **[FILL IN]**
- **AI guidance (summary):** check in a fixed order (find the ticket, validate the input,
  check the ticket's state) and only build and append the note after all three checks pass.
  A rejected action then cannot change the data.
- **Tiny unrelated experiment:** **[FILL IN: a small example with a book library, such as a
  `checkout_book` function that validates first, and what happened when you broke the order.]**
- **Independent verification:** `tests/test_notes.py` has
  `test_rejected_note_changes_nothing_and_does_not_use_an_id` (a `copy.deepcopy` snapshot is
  compared after the failed call), `test_resolved_ticket_rejects_note_and_stays_unchanged`
  and `test_check_order_find_then_validate_then_state`. The first run failed with
  `No module named 'campusflow.notes'`, then passed.
- **Final engineering decision:** `notes.add_note` appends only at the last step, and
  `next_note_id` uses the highest existing note number plus 1.
- **Reflection:** **[FILL IN]**

---

## Engineer B: Chekube

Complete two cycles in your own words. Suggested topics from your own work:
combining filters with AND, `casefold` versus `lower`, why an empty report needs special handling,
or testing a menu with scripted answers instead of typing.

### Cycle 1

- **Concept gap:** **[FILL IN]**
- **Exact question I asked:** **[FILL IN]**
- **AI guidance (summary):** **[FILL IN]**
- **Tiny unrelated experiment:** **[FILL IN: run it yourself and paste the output.]**
- **Independent verification:** **[FILL IN: name the test in `tests/test_search.py` or the other test files that proves it.]**
- **Final engineering decision:** **[FILL IN]**
- **Reflection:** **[FILL IN]**

### Cycle 2

- **Concept gap:** **[FILL IN]**
- **Exact question I asked:** **[FILL IN]**
- **AI guidance (summary):** **[FILL IN]**
- **Tiny unrelated experiment:** **[FILL IN]**
- **Independent verification:** **[FILL IN]**
- **Final engineering decision:** **[FILL IN]**
- **Reflection:** **[FILL IN]**

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
I ran python3 -c "print(isinstance(True, int), True + True)" and i got True 2

Exact question I asked (Cycle 1): “Why does True pass an integer check, and how do I reject it for affected_users?” If you did not ask exactly that, write: “The question came from the guide’s practice item about isinstance(True, int). I did not ask the AI this word for word, and the AI’s hint came while I was writing the test.”

Exact question (Cycle 2): “How do I make add_note reject bad input without changing the ticket or using up a note ID?” Same rule: if you didn’t ask it, say where it came from.
Reflection 1: “I thought True was not a number. Now I know bool is a kind of int, so I check for bool first. test_rejects_bad_values guards it, and I can explain it without AI.”

Reflection 2: “I thought rejecting bad input was enough. Now I know nothing may change until every check passes. test_rejected_note_changes_nothing_and_does_not_use_an_id guards it.”
Disclosure line for you: edit it to the truth. If Claude wrote any of validation.py or notes.py, say so.




- **Chekube:** 
i ran  python3 -c "print('Straße'.lower(), 'Straße'.casefold())"
python3 -c "print(1/0)"
straße strasse and this was the ouput i got:

Traceback (most recent call last):
  File "<string>", line 1, in <module>
ZeroDivisionError: division by zero

Cycle 1 (casefold and lower): verified by test_title_search_ignores_case_and_matches_part_of_a_word in tests/test_search.py. Decision: search_tickets uses casefold.

Cycle 2 (empty report): verified by test_empty_report_is_zero_percent_without_crashing in tests/test_report_insights.py. Decision: build_report returns 0 when there are no tickets.

Exact question: write the real question you asked. If you didn’t ask one, say so honestly.
Improvement from review: only write that Anthony’s review found three crashes (² as a menu answer, Ctrl+C at a sub-prompt, an unwritable notes file) if he really posted those comments.