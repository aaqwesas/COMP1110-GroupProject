from datetime import date
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from io import StringIO


from data_model.categories import ExpenseCategory
from tools.input_parser import ExpenseParser


class TestExpenseParser(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        self.file_path = Path(self.temp_file.name)

    def tearDown(self):
        self.temp_file.close()
        if self.file_path.exists():
            self.file_path.unlink()

    def _write_jsonl_line(self, data: dict):
        self.temp_file.write(json.dumps(data) + "\n")
        self.temp_file.flush()

    def _write_jsonl_lines(self, data_list: list[dict]):
        for data in data_list:
            self._write_jsonl_line(data)

    def test_parse_single_valid_expense(self):
        self._write_jsonl_line(
            {
                "id": 1,
                "date": "2024-01-15",
                "amount": 45.99,
                "category": "food",
                "description": "Grocery shopping",
            }
        )

        parser = ExpenseParser(self.file_path)
        results = list(parser.parse())

        self.assertEqual(len(results), 1)
        expense = results[0]
        self.assertEqual(expense.id, 1)
        self.assertEqual(expense.date, date(2024, 1, 15))
        self.assertEqual(expense.amount, 45.99)
        self.assertEqual(expense.category, ExpenseCategory.FOOD)
        self.assertEqual(expense.description, "Grocery shopping")

    def test_parse_multiple_valid_expenses(self):
        expenses_data = [
            {
                "id": 1,
                "date": "2024-01-01",
                "amount": 100.50,
                "category": "food",
                "description": "Lunch",
            },
            {
                "id": 2,
                "date": "2024-01-02",
                "amount": 50.25,
                "category": "transport",
                "description": "Bus ticket",
            },
            {
                "id": 3,
                "date": "2024-01-03",
                "amount": 200.00,
                "category": "entertainment",
                "description": "Movie",
            },
        ]
        self._write_jsonl_lines(expenses_data)

        parser = ExpenseParser(self.file_path)
        results = list(parser.parse())

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].amount, 100.50)
        self.assertEqual(results[1].amount, 50.25)
        self.assertEqual(results[2].amount, 200.00)

    def test_parse_expense_with_uppercase_category(self):
        self._write_jsonl_line(
            {
                "id": 1,
                "date": "2024-01-15",
                "amount": 30.00,
                "category": "FOOD",
                "description": "Restaurant",
            }
        )

        parser = ExpenseParser(self.file_path)
        results = list(parser.parse())

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, ExpenseCategory.FOOD)

    def test_parse_expense_with_mixed_case_category(self):
        self._write_jsonl_line(
            {
                "id": 1,
                "date": "2024-01-15",
                "amount": 30.00,
                "category": "FoOd",
                "description": "Restaurant",
            }
        )

        parser = ExpenseParser(self.file_path)
        results = list(parser.parse())

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, ExpenseCategory.FOOD)

    def test_parse_expense_with_uncategorized_category(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self._write_jsonl_line(
                {
                    "id": 1,
                    "date": "2024-01-15",
                    "amount": 100.00,
                    "category": "unknown_category",
                    "description": "Misc expense",
                }
            )

            parser = ExpenseParser(self.file_path)
            results = list(parser.parse())

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].category, ExpenseCategory.UNCATEGORIZED)
            self.assertIn("No such category 'unknown_category'", mock_stdout.getvalue())

    def test_parse_expense_with_empty_lines(self):
        self._write_jsonl_line(
            {
                "id": 1,
                "date": "2024-01-01",
                "amount": 100.50,
                "category": "food",
                "description": "Lunch",
            }
        )
        self.temp_file.write("\n")  # Empty line
        self.temp_file.write("\n")  # Another empty line
        self._write_jsonl_line(
            {
                "id": 2,
                "date": "2024-01-02",
                "amount": 50.25,
                "category": "transport",
                "description": "Bus",
            }
        )
        self.temp_file.flush()

        parser = ExpenseParser(self.file_path)
        results = list(parser.parse())

        self.assertEqual(len(results), 2)

    def test_parse_expense_with_whitespace_only_lines(self):
        self._write_jsonl_line(
            {
                "id": 1,
                "date": "2024-01-01",
                "amount": 100.50,
                "category": "food",
                "description": "Lunch",
            }
        )
        self.temp_file.write("   \n")  # Whitespace line
        self.temp_file.write("\t\n")  # Tab line
        self._write_jsonl_line(
            {
                "id": 2,
                "date": "2024-01-02",
                "amount": 50.25,
                "category": "transport",
                "description": "Bus",
            }
        )
        self.temp_file.flush()

        parser = ExpenseParser(self.file_path)
        results = list(parser.parse())

        self.assertEqual(len(results), 2)

    def test_parse_expense_missing_required_field(self):
        self._write_jsonl_line(
            {
                "id": 1,
                "date": "2024-01-15",
                "amount": 100.00,
                "category": "food",
                # Missing 'description' field
            }
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            parser = ExpenseParser(self.file_path)
            results = list(parser.parse())

            self.assertEqual(len(results), 0)
            self.assertIn("Warning: Line 1: Failed to parse", mock_stdout.getvalue())

    def test_parse_expense_invalid_date_format(self):
        self._write_jsonl_line(
            {
                "id": 1,
                "date": "01/15/2024",  # Wrong format
                "amount": 100.00,
                "category": "food",
                "description": "Lunch",
            }
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            parser = ExpenseParser(self.file_path)
            results = list(parser.parse())

            self.assertEqual(len(results), 0)
            self.assertIn("Warning: Line 1: Failed to parse", mock_stdout.getvalue())

    def test_parse_expense_invalid_amount_type(self):
        self._write_jsonl_line(
            {
                "id": 1,
                "date": "2024-01-15",
                "amount": "not a number",  # String instead of number
                "category": "food",
                "description": "Lunch",
            }
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            parser = ExpenseParser(self.file_path)
            results = list(parser.parse())
            self.assertEqual(len(results), 0)
            self.assertIn("Warning: Line 1: Failed to parse", mock_stdout.getvalue())

    def test_parse_expense_invalid_json(self):
        self.temp_file.write('{"id": 1, "date": "2024-01-15", invalid json here\n')
        self.temp_file.flush()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            parser = ExpenseParser(self.file_path)
            results = list(parser.parse())

            self.assertEqual(len(results), 0)
            self.assertIn("Warning: Line 1: Failed to parse", mock_stdout.getvalue())

    def test_invalid_file_extension_raises_error(self):
        invalid_file = Path("/tmp/test.txt")

        with self.assertRaises(ValueError) as context:
            ExpenseParser(invalid_file)

        self.assertIn("File must be JSONL format", str(context.exception))

    def test_missing_file_raises_error(self):
        non_existent = Path("/tmp/nonexistent_file_12345.jsonl")

        with self.assertRaises(FileNotFoundError):
            parser = ExpenseParser(non_existent)
            list(parser.parse())

    def test_parse_empty_file(self):
        # File is created but empty
        parser = ExpenseParser(self.file_path)
        results = list(parser.parse())

        self.assertEqual(len(results), 0)

    def test_parse_file_with_only_empty_lines(self):
        self.temp_file.write("\n\n\n")
        self.temp_file.flush()

        parser = ExpenseParser(self.file_path)
        results = list(parser.parse())

        self.assertEqual(len(results), 0)

