"""
filters.py
----------
All the business-rule / filtering logic lives here, kept separate from
file-reading and the main script so each piece is easy to test and reuse.

Rules applied to every order row:
    1. product_id must exist in the order_master table.
    2. city must be 'bangalore' or 'mumbai' (case-insensitive).
    3. order_date must NOT be a future date (compared to today).
    4. No row is kept if ANY column in it is empty / null / blank.

Date format in the source file is DD-MM-YYYY (e.g. 23-08-2026).
Change DATE_FORMAT below if your files use a different format.
"""

from datetime import datetime, date

DATE_FORMAT = "%d-%m-%Y"
ALLOWED_CITIES = {"bangalore", "mumbai"}


def has_no_empty_values(row):
    """Returns True if none of the values in the row are empty/None/blank."""
    for value in row.values():
        if value is None or str(value).strip() == "":
            return False
    return True


def product_exists_in_master(row, valid_product_ids):
    """Checks whether row's product_id exists in the master product list."""
    return row.get("product_id") in valid_product_ids


def is_allowed_city(row):
    """Checks whether the city is Bangalore or Mumbai (case-insensitive)."""
    city = row.get("city", "")
    return city.strip().lower() in ALLOWED_CITIES


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

    return True, "OK"


def build_valid_product_ids(master_rows):
    """Builds a set of product_id values from the order_master rows."""
    return {row["product_id"] for row in master_rows if row.get("product_id")}


def filter_orders(order_rows, master_rows, today=None):
    """
    Applies all filtering rules and returns only the rows that pass
    every single condition.
    """
    valid_product_ids = build_valid_product_ids(master_rows)

    valid_rows = []
    for row in order_rows:
        if not has_no_empty_values(row):
            continue
        if not product_exists_in_master(row, valid_product_ids):
            continue
        if not is_allowed_city(row):
            continue
        if not is_not_future_date(row, today):
            continue

        valid_rows.append(row)

    return valid_rows
