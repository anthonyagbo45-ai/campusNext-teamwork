import unittest

from campusflow.errors import ValidationError
from campusflow.validation import (
    validate_affected_users,
    validate_category,
    validate_staff_label,
    validate_title,
    validate_urgency,
)


class AffectedUsersTests(unittest.TestCase):
    def test_accepts_positive_integer(self):
        self.assertEqual(validate_affected_users(12), 12)

    def test_rejects_bad_values(self):
        for bad in (0, -3, 2.5, "5", True):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    validate_affected_users(bad)


class CategoryTests(unittest.TestCase):
    def test_accepts_exact_and_messy_input(self):
        for given, expected in (
            ("Network", "Network"),
            ("  hardware ", "Hardware"),
            ("SOFTWARE", "Software"),
            ("other", "Other"),
        ):
            with self.subTest(value=given):
                self.assertEqual(validate_category(given), expected)

    def test_rejects_bad_values(self):
        for bad in ("Printer", "", "   ", None, 5, ["Network"]):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    validate_category(bad)


class UrgencyTests(unittest.TestCase):
    def test_accepts_exact_and_messy_input(self):
        for given, expected in (
            ("low", "low"),
            (" Medium ", "medium"),
            ("HIGH", "high"),
        ):
            with self.subTest(value=given):
                self.assertEqual(validate_urgency(given), expected)

    def test_rejects_bad_values(self):
        for bad in ("urgent", "", "   ", None, 3):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    validate_urgency(bad)


class TitleTests(unittest.TestCase):
    def test_accepts_and_strips(self):
        self.assertEqual(validate_title("  Wi-Fi down  "), "Wi-Fi down")

    def test_rejects_bad_values(self):
        for bad in ("", "   ", None, 7, ["x"]):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    validate_title(bad)


class StaffLabelTests(unittest.TestCase):
    def test_accepts_and_strips(self):
        self.assertEqual(validate_staff_label("  Nese "), "Nese")

    def test_rejects_bad_values(self):
        for bad in ("", "   ", None, 7, ["x"]):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    validate_staff_label(bad)


if __name__ == "__main__":
    unittest.main()
