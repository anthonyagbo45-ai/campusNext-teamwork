import unittest

from campusflow.errors import ValidationError
from campusflow.validation import validate_status


class StatusTests(unittest.TestCase):
    def test_accepts_exact_and_messy_input(self):
        for given, expected in (
            ("open", "open"),
            ("  In_Progress ", "in_progress"),
            ("RESOLVED", "resolved"),
        ):
            with self.subTest(value=given):
                self.assertEqual(validate_status(given), expected)

    def test_rejects_bad_values(self):
        for bad in ("done", "", "   ", None, 4):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    validate_status(bad)


if __name__ == "__main__":
    unittest.main()
