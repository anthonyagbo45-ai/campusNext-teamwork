import os
import tempfile
import unittest

from campusflow.understanding_check import QUESTIONS, normalise_choice, run_check, score_answers


def drive(answers, notes_path=None):
    feed = iter(answers)
    lines = []
    result = run_check(lambda prompt: next(feed), lines.append, notes_path=notes_path)
    return result, "\n".join(lines)


KEY = [q["answer"] for q in QUESTIONS]
EXPLAIN = "Because the rule protects the data."


def full_run(letters):
    """Scripted answers: each letter, plus an explanation after Q1 and Q2."""
    script = []
    for number, letter in enumerate(letters, start=1):
        script.append(letter)
        if number <= 2:
            script.append(EXPLAIN)
    return script


class QuestionBankTests(unittest.TestCase):
    def test_bank_has_six_questions_each_with_a_valid_key(self):
        self.assertEqual(len(QUESTIONS), 6)
        for q in QUESTIONS:
            self.assertEqual(sorted(q["options"]), ["A", "B", "C", "D"])
            self.assertIn(q["answer"], q["options"])


class ScoringTests(unittest.TestCase):
    def test_scoring_is_separate_and_counts_one_point_each(self):
        self.assertEqual(score_answers(QUESTIONS, KEY), 6)
        self.assertEqual(score_answers(QUESTIONS, ["A"] * 6), 0)
        wrong_first = ["A" if KEY[0] != "A" else "B"] + KEY[1:]
        self.assertEqual(score_answers(QUESTIONS, wrong_first), 5)

    def test_choice_normalising(self):
        self.assertEqual(normalise_choice(" b "), "B")
        for bad in ("", "E", "AB", "1", None):
            self.assertIsNone(normalise_choice(bad))


class RunCheckTests(unittest.TestCase):
    def test_perfect_run_scores_six(self):
        (score, _), output = drive(full_run(KEY))
        self.assertEqual(score, 6)
        self.assertIn("Final score: 6/6", output)

    def test_invalid_answer_is_rejected_and_asked_again(self):
        script = ["E", "7", "", KEY[0], EXPLAIN, KEY[1], EXPLAIN] + KEY[2:]
        (score, _), output = drive(script)
        self.assertEqual(score, 6)
        self.assertEqual(output.count("Please answer A, B, C or D."), 3)

    def test_score_uses_the_first_valid_answer_not_the_feedback(self):
        wrong = "A" if KEY[0] != "A" else "B"
        (score, _), _ = drive(full_run([wrong] + KEY[1:]))
        self.assertEqual(score, 5)

    def test_two_explanations_are_required_and_short_ones_are_refused(self):
        script = [KEY[0], "no", "too short", EXPLAIN, KEY[1], EXPLAIN] + KEY[2:]
        (_, explanations), output = drive(script)
        self.assertEqual(len(explanations), 2)
        self.assertEqual(explanations[0]["explanation"], EXPLAIN)
        self.assertEqual(output.count("Please write at least"), 2)

    def test_explanations_are_saved_to_the_notes_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "notes.md")
            drive(full_run(KEY), notes_path=path)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        self.assertIn("score 6/6", text)
        self.assertIn(EXPLAIN, text)


if __name__ == "__main__":
    unittest.main()
