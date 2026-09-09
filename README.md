# Python_Project_Daily_Orders_Validation

An automated Python script that ingests daily batch orders, validates business rules, segregates transactions into distinct output reports, and dispatches an automated summary email with validation metrics.

---

## Overview

Processing raw transaction logs manually creates bottlenecks and delays reconciliation. This pipeline automates the end-to-end workflow:

1. **Ingestion:** Reads inbound daily order records (e.g., CSV, JSON, or database input).
2. **Rule Evaluation:** Assesses each order against configured validation conditions (e.g., payment status, inventory availability, address completeness).
3. **Data Segregation:**
   - **Successful Orders:** Clean records ready for downstream fulfillment.
   - **Rejected Orders:** Unmet records appended with an explicit `reason_for_rejection` column for auditing.
4. **Email Notification:** Generates and dispatches a summary digest detailing counts of accepted versus rejected transactions.

---

## Features
**Automated Batch Processing:** Handles daily transaction logs without manual intervention.

**Audit-Ready Error Logging:** Rejected records capture exact failure reasons directly in a dedicated column.

**Instant Monitoring:** Delivers high-level transactional health metrics via email upon job completion.

**Configurable Thresholds:** Validation logic and rules can be customized in one place.

## Getting Started
**Prerequisites**\
    Python 3.8+\
    An SMTP server (e.g., Gmail App Password).

## Architecture Flow

```text
[ Daily Raw Orders ]
         │
         ▼
[ Validation Engine ] ─── Checks business rules & constraints
         │
         ├─── Valid   ───► [ Successful Orders Record ]
         │
         └─── Invalid ───► Appends "reason_for_rejection" ───► [ Rejected Orders Record ]
                                                                       │
                                                                       ▼
                                                          [ Email Dispatch Service ]
                                                          (Total Valid vs. Rejected Summary)
```

---

## Project Structure

```text
daily-order-validator/
├── data/
│   ├── input/
│   └── output/
├── src/
│   ├── __init__.py
│   ├── validator.py      # Core rule-checking logic
│   ├── file_handler.py   # Ingestion and split export
│   └── notifier.py       # SMTP/Email formatting service
├── .env.example
├── .gitignore
├── main.py               # Application entry point
├── requirements.txt
└── README.md
```
