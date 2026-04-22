# Sample test data

Run:

```bash
python scripts/generate_test_data.py
```

Files in this folder:

- `sample_expenses_30days.jsonl`: main demo dataset for `ExpenseParser`, `SummaryStatistics`, and menu-based manual testing
- `case_budget_exceeded.jsonl`: recent expenses that can exceed a period budget threshold
- `case_single_large_transaction.jsonl`: contains one large expense for `SingleTransactionRule`
- `case_percentage_threshold.jsonl`: one category dominates total spending for `PercentageThresholdRule`
- `case_consecutive_overspend.jsonl`: three high-spending days in a row for `ConsecutiveOverspendRule`
- `case_uncategorized.jsonl`: includes `UNCATEGORIZED` expenses for `UncategorizedWarningRule`
- `invalid_date.jsonl`: invalid ISO date format for parser validation
- `invalid_amount.jsonl`: invalid amount type for parser validation
- `missing_field.jsonl`: missing `description` field for parser validation
- `unknown_category.jsonl`: unsupported category value that should fall back to `UNCATEGORIZED`
- `empty.jsonl`: empty file edge case

All files use the same JSONL transaction shape used by the current repository:

```json
{"id":"e001","date":"2026-04-01","amount":32.0,"category":"FOOD","description":"Breakfast"}
```
