import unittest

from campusflow.errors import ValidationError
from campusflow.validation import validate_affected_users


class AffectedUsersTests(unittest.TestCase):
    def test_accepts_positive_integer(self):
        self.assertEqual(validate_affected_users(12), 12)

    def test_rejects_bad_values(self):
        for bad in (0, -3, 2.5, "5", True):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    validate_affected_users(bad)