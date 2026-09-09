# Python_Project_Daily_Orders_Validation (Pure Python, No Pandas)

## Overview

A tiny project that cleans raw order data using only Python's built-in
`csv`, `datetime`, and `os` modules.\
Processing raw transaction logs manually creates bottlenecks and delays reconciliation. This pipeline automates the end-to-end workflow:

1. **Ingestion:** Reads inbound daily order records (e.g., CSV, JSON, or database input).
2. **Rule Evaluation:** Assesses each order against configured validation conditions (e.g., payment status, inventory availability, address completeness).
3. **Data Segregation:**
   - **Successful Orders:** Clean records ready for downstream fulfillment.
   - **Rejected Orders:** Unmet records appended with an explicit `reason_for_rejection` column for auditing.
4. **Email Notification:** Generates and dispatches a summary digest detailing counts of accepted versus rejected transactions.

---

## Features
**Automated Batch Processing:** Handles daily transaction logs without manual intervention.\
**Audit-Ready Error Logging:** Rejected records capture exact failure reasons directly in a dedicated column.\
**Instant Monitoring:** Delivers high-level transactional health metrics via email upon job completion.\
**Configurable Thresholds:** Validation logic and rules can be customized in one place.

---

## Folder structure

```
order_project/
├── data/
│   ├── order_master.csv     # product_id, product_name, price, category
│   └── order1.csv           # order_id, order_date, product_id, quantity, sales, city
├── output/
│   └── cleaned_orders.csv   # generated after running the script
├── clean_orders.py          # main script
├── test_clean_orders.py     # unit tests
└── README.md
```

## Rules applied to every order row

A row is kept only if **all** of the following are true:

1. `product_id` exists in `order_master.csv`
2. `city` is `bangalore` or `mumbai` (case-insensitive)
3. `order_date` is not a future date (compared to today)
4. No column in the row is empty / null

---
## Getting Started
**Prerequisites**\
Python 3.8+\
An SMTP server (e.g., Gmail App Password, AWS SES, SendGrid)

## How to run

```bash
cd order_project
python clean_orders.py
```

This prints a summary (how many rows were dropped and why) and writes the
cleaned data to `output/cleaned_orders.csv`.

## How to run the tests

```bash
python -m unittest test_clean_orders.py
```

## Customizing

- If your `order_date` column uses a different format (e.g. `2026-08-23`
  instead of `23-08-2026`), update `DATE_FORMAT` at the top of
  `clean_orders.py` (uses standard `strptime` codes, e.g. `"%Y-%m-%d"`).
- To allow more cities, add them (lowercase) to the `VALID_CITIES` set.
- `today` defaults to the real current date, but `clean_orders()` accepts
  a `today` argument so you can test with a fixed date.

## Ideas to extend this project

- Add a `--summary` flag to also print sales totals by city/category.
- Join in `product_name`/`category` from `order_master.csv` into the
  cleaned output.
- Log dropped rows (with reasons) to a separate `output/rejected_orders.csv`
  for auditing.
  
  ---

  ## Project Structure

  ```
  daily-order-validator/
  ├── data/
  │   ├── input/
  │   └── output/
  ├── src/
  │   ├── filters.py
  │   ├── test_filters.py      # Core rule-checking logic
  │   ├── clean_orders.py   # Ingestion and split export
  │   └── test_clean_orders.py       # SMTP/Email formatting service
  ├── .env.example
  ├── .gitignore
  ├── main.py               # Application entry point
  ├── sales_Summary_report.csv
  └── README.md
  ```
