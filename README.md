# Order Cleaning Project (Pure Python, No Pandas)

A tiny project that cleans raw order data using only Python's built-in
`csv`, `datetime`, and `os` modules.

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
