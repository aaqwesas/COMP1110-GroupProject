from datetime import date
import json
import unittest
import tempfile
from pathlib import Path

from data_model.categories import ExpenseCategory, IncomeCategory
from data_model.schemas import Expense, Income
from tools.output_parser import GenericOutputParser


class TestOutputParser(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        self.temp_path = Path(self.temp_file.name)
        self.parser = GenericOutputParser()

    def tearDown(self):
        self.temp_file.close()
        if self.temp_path.exists():
            self.temp_path.unlink()

    def _read_non_empty_lines(self) -> list[str]:
        with open(self.temp_path, "r", encoding="utf-8") as f:    
            return [line.strip() for line in f.readlines() if line.strip()]

    def test_write_single_income_record(self):
        records = [
            Income(
                id="inc_001",
                date=date(2024, 1, 15),
                amount=5000.00,
                category=IncomeCategory.SALARY,
                description="Monthly salary",
            )
        ]
        self.parser(self.temp_path, records)

        with open(self.temp_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 1)
        data = json.loads(lines[0])
        self.assertEqual(data["id"], "inc_001")
        self.assertEqual(data["amount"], 5000.00)
        self.assertEqual(data["category"], "SALARY")
        self.assertEqual(data["description"], "Monthly salary")
        self.assertEqual(data["date"], "2024-01-15")

    def test_write_single_expense_record(self):
        records = [
            Expense(
                id="exp_001",
                date=date(2024, 1, 10),
                amount=150.75,
                category=ExpenseCategory.FOOD,
                description="Grocery shopping",
            )
        ]
        self.parser(self.temp_path, records)

        with open(self.temp_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 1)
        data = json.loads(lines[0])
        self.assertEqual(data["id"], "exp_001")
        self.assertEqual(data["amount"], 150.75)
        self.assertEqual(data["category"], "FOOD")

    def test_write_multiple_records(self):
        records = [
            Expense(
                id="exp_001",
                date=date(2024, 1, 10),
                amount=100.0,
                category=ExpenseCategory.RENT,
                description="Rent",
            ),
            Expense(
                id="exp_002",
                date=date(2024, 1, 11),
                amount=50.0,
                category=ExpenseCategory.FOOD,
                description="Food",
            ),
            Expense(
                id="exp_003",
                date=date(2024, 1, 12),
                amount=30.0,
                category=ExpenseCategory.TRAFFIC,
                description="Gas",
            ),
        ]
        self.parser(self.temp_path, records)

        with open(self.temp_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 3)
        for i, line in enumerate(lines):
            data = json.loads(line)
            self.assertEqual(data["id"], f"exp_00{i + 1}")

    def test_append_mode(self):
        records1 = [
            Income(
                id="inc_001",
                date=date(2024, 1, 1),
                amount=1000.0,
                category=IncomeCategory.SALARY,
                description="First",
            )
        ]
        records2 = [
            Income(
                id="inc_002",
                date=date(2024, 1, 2),
                amount=2000.0,
                category=IncomeCategory.BONUS,
                description="Second",
            )
        ]

        self.parser(self.temp_path, records1)
        self.parser(self.temp_path, records2)

        with open(self.temp_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["id"], "inc_001")
        self.assertEqual(json.loads(lines[1])["id"], "inc_002")

    def test_empty_records_list(self):
        self.parser(self.temp_path, [])

        self.assertTrue(self.temp_path.exists())
        with open(self.temp_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "")

    def test_date_serialization(self):
        records = [
            Income(
                id="inc_001",
                date=date(2024, 12, 25),
                amount=500.0,
                category=IncomeCategory.BONUS,
                description="Christmas bonus",
            )
        ]
        self.parser(self.temp_path, records)

        with open(self.temp_path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        self.assertEqual(data["date"], "2024-12-25")

    def test_enum_serialization(self):
        records = [
            Expense(
                id="exp_001",
                date=date(2024, 1, 1),
                amount=100.0,
                category=ExpenseCategory.ENTERTAINMENT,
                description="Movie",
            )
        ]
        self.parser(self.temp_path, records)

        with open(self.temp_path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        self.assertEqual(data["category"], "ENTERTAINMENT")
        self.assertIsInstance(data["category"], str)

    def test_float_precision(self):
        records = [
            Expense(
                id="exp_001",
                date=date(2024, 1, 1),
                amount=99.99,
                category=ExpenseCategory.SUBSCRIPTION,
                description="Test",
            )
        ]
        self.parser(self.temp_path, records)

        with open(self.temp_path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        self.assertEqual(data["amount"], 99.99)

    def test_all_expense_categories(self):
        records = [
            Expense(
                id=f"exp_{cat.value}",
                date=date(2024, 1, 1),
                amount=10.0,
                category=cat,
                description=f"Test {cat.value}",
            )
            for cat in ExpenseCategory
        ]
        self.parser(self.temp_path, records)

        lines = self._read_non_empty_lines()

        self.assertEqual(len(lines), len(ExpenseCategory))
        categories_in_file = {json.loads(line)["category"] for line in lines}
        self.assertEqual(categories_in_file, {cat.name for cat in ExpenseCategory})
