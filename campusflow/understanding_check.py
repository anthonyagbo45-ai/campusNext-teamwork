"""Engineering Understanding Check.

The question bank (QUESTIONS) is plain data. The scoring logic (score_answers)
knows nothing about the menu, so each can be tested on its own.
"""

QUESTIONS = [
    {
        "prompt": "Ticket T001 is open and unassigned. A user tries to move it to in_progress.",
        "options": {"A": "Accept", "B": "Reject and preserve all data",
                    "C": "Resolve it automatically", "D": "Remove ticket"},
        "answer": "B",
    },
    {
        "prompt": "The app has zero tickets. What should resolution percentage display?",
        "options": {"A": "Crash", "B": "100%", "C": "0%",
                    "D": "Divide by one without explanation"},
        "answer": "C",
    },
    {
        "prompt": "Filter title='wifi', category='Network', status='open'. Which records should match?",
        "options": {"A": "Any record matching one filter", "B": "Only records matching all supplied filters",
                    "C": "All network records", "D": "All open records"},
        "answer": "B",
    },
    {
        "prompt": "A resolved ticket receives 'Add note'. What should happen?",
        "options": {"A": "Append anyway", "B": "Delete old notes",
                    "C": "Reject until reopened", "D": "Change status silently"},
        "answer": "C",
    },
    {
        "prompt": "The JSON file includes two tickets with the same ID. What should load do?",
        "options": {"A": "Keep both", "B": "Replace memory with duplicates",
                    "C": "Reject the load without changing current memory", "D": "Rename IDs silently"},
        "answer": "C",
    },
    {
        "prompt": "A PR changes validation but has no negative-case tests. Best review action?",
        "options": {"A": "Approve because it runs", "B": "Request focused tests and reasoning",
                    "C": "Merge immediately", "D": "Ask AI to approve it"},
        "answer": "B",
    },
]

VALID_CHOICES = ("A", "B", "C", "D")
EXPLAIN_COUNT = 2          # explanations required for the first two questions
MIN_EXPLANATION_LENGTH = 10


def normalise_choice(text):
    """Return 'A'-'D' for valid input (any case, spaces ignored), otherwise None."""
    if not isinstance(text, str):
        return None
    choice = text.strip().upper()
    return choice if choice in VALID_CHOICES else None


def score_answers(questions, answers):
    """One point for each submitted answer that matches the key. Returns 0..len(questions)."""
    return sum(1 for question, answer in zip(questions, answers) if answer == question["answer"])


def _ask_choice(ask, out):
    while True:
        choice = normalise_choice(ask("Your answer (A/B/C/D): "))
        if choice:
            return choice
        out("Please answer A, B, C or D.")


def _ask_explanation(ask, out):
    while True:
        text = ask("In one or two sentences, explain why: ").strip()
        if len(text) >= MIN_EXPLANATION_LENGTH:
            return text
        out(f"Please write at least {MIN_EXPLANATION_LENGTH} characters.")


def run_check(ask, out, questions=QUESTIONS, notes_path=None):
    """Ask every question, score the FIRST answer given, collect explanations.

    Returns (score, explanations). Explanations are never auto-graded; they are
    saved to notes_path (if given) and shown for mentor discussion.
    """
    answers, explanations = [], []
    for number, question in enumerate(questions, start=1):
        out(f"\nQ{number}. {question['prompt']}")
        for letter, text in question["options"].items():
            out(f"  {letter}) {text}")
        choice = _ask_choice(ask, out)
        answers.append(choice)                       # score uses this first answer
        correct = choice == question["answer"]
        out("Correct." if correct else f"Not quite. The answer is {question['answer']}.")
        if number <= EXPLAIN_COUNT:
            explanations.append({"question": number, "answer": choice,
                                 "explanation": _ask_explanation(ask, out)})
    score = score_answers(questions, answers)
    out(f"\nFinal score: {score}/{len(questions)}")
    if explanations:
        out("Your explanations (for mentor discussion):")
        for item in explanations:
            out(f"  Q{item['question']} ({item['answer']}): {item['explanation']}")
        if notes_path:
            with open(notes_path, "a", encoding="utf-8") as handle:
                handle.write(f"## Understanding check, score {score}/{len(questions)}\n")
                for item in explanations:
                    handle.write(f"- Q{item['question']} (answered {item['answer']}): "
                                 f"{item['explanation']}\n")
                handle.write("\n")
    return score, explanations
