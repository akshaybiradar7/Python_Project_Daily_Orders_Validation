"""
clean_orders.py
----------------
A small, dependency-free (no pandas) project that:

1. Reads order_master.csv (list of valid products)
2. Reads order1.csv (raw orders)
3. Keeps only orders that satisfy ALL of these rules:
   a. product_id exists in order_master.csv
   b. city is 'bangalore' or 'mumbai'   (case-insensitive)
   c. order_date is NOT a future date (compared to today)
   d. no column in the row is empty / null
4. Writes the cleaned rows to output/cleaned_orders.csv
5. Prints a short summary of what was dropped and why

Only the Python standard library is used: csv, datetime, os.
"""

import csv
import os
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"  # e.g., smtp.office365.com for Outlook
SMTP_PORT = 587
SENDER_EMAIL = "akshay.biradar7@gmail.com"
SENDER_PASSWORD = "amkh mrtf fpsi nmxi"  # Use an App Password (not your personal login password)
RECIPIENT_EMAIL = "ajeet.patil7@gmail.com, ajaysn1991@gmail.com"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_DIR = "incoming files"
OUTPUT_DIR = "output files/successful files"
OUTPUT_DIR1 = "output files/rejected files"

timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

# Create the file name with the timestamp
file_name = f"successful_orders_{timestamp}.csv"

file_name1 = f"rejected_orders_{timestamp}.csv"

# Build the full file path
SUCCESSFUL_ORDERS_FILE = os.path.join(OUTPUT_DIR, file_name)

ORDER_MASTER_FILE = os.path.join(DATA_DIR, "order_master.csv")
ORDER_FILE = os.path.join(DATA_DIR, "order1.csv")
SUCCESSFUL_ORDERS_FILE = os.path.join(OUTPUT_DIR, file_name)
REJECTED_ORDERS_FILE = os.path.join(OUTPUT_DIR1, file_name1)

# Change this to match your CSV date format (e.g., "%Y-%m-%d" or "%d-%m-%Y")
DATE_FORMAT = "%d-%m-%Y"

VALID_CITIES = {"bangalore", "mumbai"}


# ---------------------------------------------------------------------------
# Step 1: Load valid product_ids from order_master.csv
# ---------------------------------------------------------------------------
def load_valid_product_ids(path):
    """Return a set of product_id strings found in order_master.csv."""
    valid_ids = set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_id = row.get("product_id", "").strip()
            if product_id:
                valid_ids.add(product_id)
    return valid_ids


# ---------------------------------------------------------------------------
# Step 2: Row-level validation helpers
# ---------------------------------------------------------------------------
def has_no_empty_fields(row):
    """True if every value in the row is non-empty after stripping spaces."""
    return all(value is not None and str(value).strip() != "" for value in row.values())


def is_valid_product(row, valid_product_ids):
    product_id = row.get("product_id", "").strip()
    return product_id in valid_product_ids


def is_valid_city(row):
    city = row.get("city", "").strip().lower()
    return city in VALID_CITIES


def validate_order_date(row, today):
    """
    Validates order_date against today's date.
    Returns: (is_valid: bool, error_message: str or None)
    """
    date_str = row.get("order_date", "").strip()

    if not date_str:
        return False, "Order date is empty"

    try:
        order_date = datetime.strptime(date_str, DATE_FORMAT).date()
    except ValueError:
        return False, f"Invalid date format (expected {DATE_FORMAT})"

    if order_date > today:
        return False, f"Date '{date_str}' is a future date (greater than today)"
    elif order_date < today:
        return False, f"Date '{date_str}' is a past date (less than today)"

    return True, None


# ---------------------------------------------------------------------------
# Step 3: Main cleaning pipeline
# ---------------------------------------------------------------------------
def clean_orders(order_master_path, order_file_path, today=None):
    """Read orders, split into clean/unclean, and return data with stats."""
    if today is None:
        today = datetime.today().date()

    valid_product_ids = load_valid_product_ids(order_master_path)

    clean_rows = []
    unclean_rows = []

    stats = {
        "total": 0,
        "dropped_empty_field": 0,
        "dropped_invalid_product": 0,
        "dropped_invalid_city": 0,
        "dropped_future_date": 0,
        "clean_total": 0,
        "unclean_total": 0,
    }

    with open(order_file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        clean_fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        unclean_fieldnames = clean_fieldnames + ["rejection_reasons"]

        for row in reader:
            stats["total"] += 1
            reasons = []

            # Check 1: Empty fields
            if not has_no_empty_fields(row):
                stats["dropped_empty_field"] += 1
                reasons.append("Empty or whitespace field")

            # Check 2: Product ID
            if not is_valid_product(row, valid_product_ids):
                stats["dropped_invalid_product"] += 1
                reasons.append("Invalid product ID")

            # Check 3: City
            if not is_valid_city(row):
                stats["dropped_invalid_city"] += 1
                reasons.append("Invalid city name")

            # Check 4: Date
            is_valid, date_error = validate_order_date(row, today)
            if not is_valid:
                stats["dropped_future_date"] += 1
                reasons.append("Future or malformed date")

            # Route row exactly once
            if reasons:
                row_copy = dict(row)
                row_copy["rejection_reasons"] = " ; ".join(reasons)
                unclean_rows.append(row_copy)
                stats["unclean_total"] += 1
            else:
                clean_rows.append(row)
                stats["clean_total"] += 1

        return clean_rows, unclean_rows, clean_fieldnames, unclean_fieldnames, stats


# ---------------------------------------------------------------------------
# Step 4: Write CSV helper functions
# ---------------------------------------------------------------------------
def write_clean_csv(clean_rows, fieldnames, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)


def write_unclean_csv(unclean_rows, fieldnames, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unclean_rows)


def send_summary_email(stats, recipient_email):
    """Formats and sends the summary report via email."""
    today_str = datetime.now().strftime("%d-%m-%Y")

    subject = f"Orders Report of ({today_str}) - ({stats['clean_total']} - Successful Orders & {stats['unclean_total']} - Rejected Orders)"

    body = f"""Hello Team,

This is the automated orders validation summary of ({today_str}) date:

========================================
             ORDER SUMMARY
========================================
• Total Orders Processed : {stats['total']}
• Successful Orders      : {stats['clean_total']}
• Rejected Orders        : {stats['unclean_total']}

----------------------------------------
          REJECTION BREAKDOWN
----------------------------------------
• Rejected because of Empty Field        : {stats['dropped_empty_field']}
• Rejected because of Invalid Product_ID : {stats['dropped_invalid_product']}
• Rejected because of Wrong City Name    : {stats['dropped_invalid_city']}
• Rejected because of Wrong Order Date   : {stats['dropped_future_date']}
========================================

This is an automated system email.

Thank you for your valuable time.
"""

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure TLS
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"\nSummary email successfully sent to: {recipient_email}")
    except Exception as e:
        print(f"\nFailed to send email: {e}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    clean_rows, unclean_rows, clean_fieldnames, unclean_fieldnames, stats = clean_orders(
        ORDER_MASTER_FILE, ORDER_FILE
    )

    write_clean_csv(clean_rows, clean_fieldnames, SUCCESSFUL_ORDERS_FILE)
    write_unclean_csv(unclean_rows, unclean_fieldnames, REJECTED_ORDERS_FILE)

    print("=== Rejected Orders Summary ===")
    print(f"Dropped because of empty field : {stats['dropped_empty_field']}")
    print(f"Dropped because invalid product_id : {stats['dropped_invalid_product']}")
    print(f"Dropped because wrong city name : {stats['dropped_invalid_city']}")
    print(f"Dropped because wrong order date : {stats['dropped_future_date']}")
    print(f"\nSuccessful table no_of rows : {stats['clean_total']}")
    print(f"Total rejected no_of rows : {stats['unclean_total']}")
    print(f"Total no_of rows our table had : {stats['total']}")
    print(f"\nSuccessful file data written to : {SUCCESSFUL_ORDERS_FILE}")
    print(f"\nRejected file data written to: {REJECTED_ORDERS_FILE}")

    # Send summary email
    send_summary_email(stats, RECIPIENT_EMAIL)

if __name__ == "__main__":
    main()