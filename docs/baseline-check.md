# Baseline check

## Commit tested
<the 40-character SHA from git rev-parse HEAD>

## How I ran it
- Tests: python3 -m unittest discover -s tests -v
- Program: python3 -m campusflow

## Test result
Ran <number> tests: <OK, or list what failed>

## Three inputs I tried
1. Create a ticket: high urgency, 12 users.
   Result: <what you saw, for example "Created T001 [critical]">
2. Move an unassigned open ticket to in_progress.
   Result: <what you saw>
3. Load a file that has two tickets with the same ID.
   Result: <exactly what dup_check.py printed>

## Reproduced gaps
- Pressing Ctrl+C at the menu crashes with a KeyboardInterrupt traceback, instead of a friendly message.
- <Duplicate IDs in a saved file: write "reproduced" or "not reproduced">

## What the audit said needed improvement
- <point 1 from your audit, in your own words>
- <point 2>

## Not yet confirmed
- <anything from the audit you have not tried to reproduce>