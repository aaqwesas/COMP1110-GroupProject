import unittest
from unittest.mock import patch
from io import StringIO
from data_model.categories import ExpenseCategory, IncomeCategory
from tools.category_parser import (
    ExpenseCategoryParser,
    GenericCategoryParser,
    IncomeCategoryParser,
)


class TestGenericCategoryParser(unittest.TestCase):
    def setUp(self) -> None:
        self.income_parser = GenericCategoryParser(
            enum_type=IncomeCategory, default_category=IncomeCategory.UNCATEGORIZED
        )
        self.expense_parser = GenericCategoryParser(
            enum_type=ExpenseCategory, default_category=ExpenseCategory.UNCATEGORIZED
        )

    def test_parse_valid_category_lowercase(self):
        result = self.income_parser("salary")
        self.assertEqual(result, IncomeCategory.SALARY)

    def test_parse_valid_category_uppercase(self):
        result = self.income_parser("SALARY")
        self.assertEqual(result, IncomeCategory.SALARY)

    def test_parse_valid_category_mixed_case(self):
        result = self.income_parser("SaLaRy")
        self.assertEqual(result, IncomeCategory.SALARY)

    def test_parse_invalid_category_returns_default(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.income_parser("invalid_category")
            self.assertEqual(result, IncomeCategory.UNCATEGORIZED)
            self.assertIn("No such category 'invalid_category'", mock_stdout.getvalue())

    def test_parse_empty_string_returns_default(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.income_parser("")
            self.assertEqual(result, IncomeCategory.UNCATEGORIZED)
            self.assertIn("No such category ''", mock_stdout.getvalue())

    def test_parse_whitespace_only_returns_default(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.income_parser("   ")
            self.assertEqual(result, IncomeCategory.UNCATEGORIZED)

    def test_parse_none_raises_error(self):
        with self.assertRaises(AttributeError):
            self.income_parser(None)  # type: ignore

    def test_different_enum_types(self):
        income_result = self.income_parser("investment")
        self.assertEqual(income_result, IncomeCategory.INVESTMENT)

        expense_result = self.expense_parser("food")
        self.assertEqual(expense_result, ExpenseCategory.FOOD)

    def test_default_category_per_parser(self):
        income_result = self.income_parser("nonexistent")
        self.assertEqual(income_result, IncomeCategory.UNCATEGORIZED)

        expense_result = self.expense_parser("nonexistent")
        self.assertEqual(expense_result, ExpenseCategory.UNCATEGORIZED)

    def test_all_valid_categories(self):
        for category in IncomeCategory:
            if category != IncomeCategory.UNCATEGORIZED:
                result = self.income_parser(category.value)
                self.assertEqual(result, category)

    def test_category_with_special_chars_returns_default(self):
        with patch("sys.stdout", new_callable=StringIO):
            result = self.expense_parser("food!")
            self.assertEqual(result, ExpenseCategory.UNCATEGORIZED)


class TestParserInstances(unittest.TestCase):
    def test_income_parser_instance(self):
        self.assertIsInstance(IncomeCategoryParser, GenericCategoryParser)
        self.assertEqual(IncomeCategoryParser.enum_type, IncomeCategory)
        self.assertEqual(
            IncomeCategoryParser.default_category, IncomeCategory.UNCATEGORIZED
        )

    def test_expense_parser_instance(self):
        self.assertIsInstance(ExpenseCategoryParser, GenericCategoryParser)
        self.assertEqual(ExpenseCategoryParser.enum_type, ExpenseCategory)
        self.assertEqual(
            ExpenseCategoryParser.default_category, ExpenseCategory.UNCATEGORIZED
        )

    def test_income_parser_functionality(self):
        result = IncomeCategoryParser("SALARY")
        self.assertEqual(result, IncomeCategory.SALARY)

        with patch("sys.stdout", new_callable=StringIO):
            invalid_result = IncomeCategoryParser("invalid")
            self.assertEqual(invalid_result, IncomeCategory.UNCATEGORIZED)

    def test_expense_parser_functionality(self):
        result = ExpenseCategoryParser("TRAFFIC")
        self.assertEqual(result, ExpenseCategory.TRAFFIC)

        with patch("sys.stdout", new_callable=StringIO):
            invalid_result = ExpenseCategoryParser("invalid")
            self.assertEqual(invalid_result, ExpenseCategory.UNCATEGORIZED)


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        self.parser = GenericCategoryParser(
            enum_type=IncomeCategory, default_category=IncomeCategory.UNCATEGORIZED
        )

    def test_unicode_characters(self):
        with patch("sys.stdout", new_callable=StringIO):
            result = self.parser("café")
            self.assertEqual(result, IncomeCategory.UNCATEGORIZED)

    def test_very_long_string(self):
        long_string = "a" * 1000
        with patch("sys.stdout", new_callable=StringIO):
            result = self.parser(long_string)
            self.assertEqual(result, IncomeCategory.UNCATEGORIZED)

    def test_case_sensitivity_not_an_issue(self):
        test_cases = ["SALARY", "Salary", "sAlArY", "salary"]
        for test in test_cases:
            result = self.parser(test)
            self.assertEqual(result, IncomeCategory.SALARY)

    def test_parser_reusability(self):
        results = []
        for _ in range(10):
            results.append(self.parser("salary"))

        for result in results:
            self.assertEqual(result, IncomeCategory.SALARY)


class TestPrintBehavior(unittest.TestCase):
    def setUp(self):
        self.parser = GenericCategoryParser(
            enum_type=IncomeCategory, default_category=IncomeCategory.UNCATEGORIZED
        )

    def test_warning_printed_for_invalid_category(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.parser("invalid_category")
            output = mock_stdout.getvalue()
            self.assertIn("No such category 'invalid_category'", output)
            self.assertIn("classifying as UNCATEGORIZED", output)

    def test_no_warning_for_valid_category(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.parser("salary")
            output = mock_stdout.getvalue()
            self.assertEqual(output, "")

    def test_warning_printed_once_per_invalid_call(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.parser("invalid1")
            self.parser("invalid2")
            output = mock_stdout.getvalue()
            self.assertEqual(output.count("No such category"), 2)


if __name__ == "__main__":
    unittest.main()

# @description
