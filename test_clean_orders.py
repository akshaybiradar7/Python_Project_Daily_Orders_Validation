"""
test_clean_orders.py
---------------------
Quick sanity tests for clean_orders.py using only the standard
library's unittest module (no pytest/pandas needed).

Run with:  python -m unittest test_clean_orders.py
"""

import unittest
from datetime import date
from clean_orders import (
    has_no_empty_fields,
    is_valid_product,
    is_valid_city,
    validate_order_date,
)


class TestFilters(unittest.TestCase):

    def is_exact_today_date(row, today):
        """Returns True ONLY if the order_date matches today's date exactly."""
        date_str = row.get("order_date", "").strip()
        try:
            order_date = datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            return False
        return order_date == today

    def test_has_no_empty_fields_true(self):
        row = {"a": "1", "b": "hello"}
        self.assertTrue(has_no_empty_fields(row))

    def test_has_no_empty_fields_false_on_blank(self):
        row = {"a": "1", "b": "  "}
        self.assertFalse(has_no_empty_fields(row))

    def test_is_valid_product_true(self):
        row = {"product_id": "100"}
        self.assertTrue(is_valid_product(row, {"100", "200"}))

    def test_is_valid_product_false(self):
        row = {"product_id": "999"}
        self.assertFalse(is_valid_product(row, {"100", "200"}))

    def test_is_valid_city_case_insensitive(self):
        self.assertTrue(is_valid_city({"city": "Bangalore"}))
        self.assertTrue(is_valid_city({"city": "mumbai"}))
        self.assertFalse(is_valid_city({"city": "Mysore"}))

    def is_not_future_date(row, today=None):
        """
        Checks that order_date is today or earlier (not a future date).
        Returns False (row rejected) if the date is invalid/unparseable too,
        since an unparseable date can't be verified as valid.

        'today' can be passed as either a datetime.date or a datetime.datetime
        object - both are handled correctly.
        """
        if today is None:
            today = date.today()
        elif isinstance(today, datetime):
            today = today.date()  # normalize datetime -> date

        date_str = row.get("order_date", "")
        try:
            order_date = datetime.strptime(date_str, DATE_FORMAT).date()
        except (ValueError, TypeError):
            return False

        return order_date <= today

    def validate_order_date(row, today=None):
        """
        Same check as is_not_future_date, but instead of a plain True/False
        it returns a descriptive message explaining WHY a date failed.

        Returns:
            (True, "OK")                                     -> valid date
            (False, "<reason>")                               -> invalid date
        """
        if today is None:
            today = date.today()
        elif isinstance(today, datetime):
            today = today.date()

        date_str = row.get("order_date", "")

        try:
            order_date = datetime.strptime(date_str, DATE_FORMAT).date()
        except (ValueError, TypeError):
            return False, f"Error: order_date '{date_str}' is invalid or in the wrong format (expected DD-MM-YYYY)"

        if order_date > today:
            return False, f"Error: order_date '{date_str}' is a future date (today is {today.strftime(DATE_FORMAT)})"

        if order_date < today:
            return False, f"Error: order_date '{date_str}' is a past date (today is {today.strftime(DATE_FORMAT)})"

        return True, "OK"

    def test_is_exact_today_date_bad_format(self):
        today = date(2026, 8, 23)
        self.assertFalse(is_exact_today_date({"order_date": "2026/08/23"}, today))


if __name__ == "__main__":
    unittest.main()
