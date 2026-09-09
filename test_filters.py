"""
test_filters.py
----------------
Run with:
    python -m unittest test_filters.py
or:
    pytest test_filters.py
"""

import unittest
from datetime import date
from filters import is_not_future_date, validate_order_date


class TestFilters(unittest.TestCase):

    def test_is_not_future_date(self):
        today = date(2026, 8, 23)
        self.assertTrue(is_not_future_date({"order_date": "23-08-2026"}, today))   # equal to today -> OK
        self.assertFalse(is_not_future_date({"order_date": "25-08-2026"}, today))  # future -> rejected
        self.assertTrue(is_not_future_date({"order_date": "20-08-2026"}, today))   # past -> OK

    def test_validate_order_date_shows_error_message(self):
        today = date(2026, 8, 23)

        # Valid date -> True, "OK"
        ok, msg = validate_order_date({"order_date": "23-08-2026"}, today)
        self.assertTrue(ok)
        self.assertEqual(msg, "OK")

        # Future date -> False, with a descriptive error message
        ok, msg = validate_order_date({"order_date": "25-08-2026"}, today)
        self.assertFalse(ok)
        self.assertIn("future date", msg)

        # Bad format -> False, with a descriptive error message
        ok, msg = validate_order_date({"order_date": "2026-08-25"}, today)
        self.assertFalse(ok)
        self.assertIn("invalid", msg)


if __name__ == "__main__":
    unittest.main()
