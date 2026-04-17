import unittest
from datetime import date, timedelta
from data_model.rules import RuleOperator
from data_model.schemas import Expense
from data_model.categories import ExpenseCategory
from core.concrete_alerts import ConsoleAlert
from core.concrete_rules import (
    CategoryBudgetRule,
    SingleTransactionRule,
    PercentageThresholdRule,
    UncategorizedWarningRule,
    ConsecutiveOverspendRule
)

class DummyAlert(ConsoleAlert):
    def __init__(self):
        super().__init__()
        self.triggered = False
        self.message = ""

    def send(self, message: str) -> None:
        self.triggered = True
        self.message = message


class TestBudgetRules(unittest.TestCase):
    def setUp(self):
        self.alert = DummyAlert()
        self.today = date.today()

    def create_expense(self, amount: float, category: ExpenseCategory = ExpenseCategory.FOOD,
                       offset_days: int = 0) -> Expense:
        return Expense(
            id="test_id",
            date=self.today - timedelta(days=offset_days),
            amount=amount,
            category=category,
            description="Test Expense"
        )

    def test_category_budget_empty_history(self):
        rule = CategoryBudgetRule(
            alert=self.alert,
            period=7,
            operator=RuleOperator.GT,
            threshold=100.0
        )

        new_transaction = self.create_expense(50.0)
        is_triggered = rule.evaluate(new_transaction, history=[])

        self.assertFalse(is_triggered)
        self.assertFalse(self.alert.triggered)

        new_transaction_2 = self.create_expense(120.0)
        is_triggered_2 = rule.evaluate(new_transaction_2, history=[])

        self.assertTrue(is_triggered_2)
        self.assertTrue(self.alert.triggered)

    def test_category_budget_discards_old_transactions(self):
        rule = CategoryBudgetRule(
            alert=self.alert,
            period=7,
            operator=RuleOperator.GT,
            threshold=100.0
        )
        history = [
            self.create_expense(40.0, offset_days=10),
            self.create_expense(40.0, offset_days=5),
        ]

        new_tx = self.create_expense(50.0, offset_days=0)
        is_triggered = rule.evaluate(new_tx, history)

        self.assertFalse(is_triggered)

    def test_percentage_threshold_division_by_zero(self):
        rule = PercentageThresholdRule(
            alert=self.alert,
            period=30,
            operator=RuleOperator.GT,
            threshold=0.5
        )

        tx_zero = self.create_expense(0.0, ExpenseCategory.RENT)
        is_triggered = rule.evaluate(tx_zero, history=[])

        self.assertFalse(is_triggered)

    def test_percentage_threshold_calculation(self):
        rule = PercentageThresholdRule(
            alert=self.alert,
            period=30,
            operator=RuleOperator.GT,
            threshold=0.5
        )

        history = [
            self.create_expense(1000.0, ExpenseCategory.RENT, offset_days=2),
            self.create_expense(100.0, ExpenseCategory.FOOD, offset_days=1)
        ]

        new_tx = self.create_expense(1500.0, ExpenseCategory.ENTERTAINMENT)
        is_triggered = rule.evaluate(new_tx, history)

        self.assertTrue(is_triggered)
        self.assertTrue(self.alert.triggered)

    def test_uncategorized_warning(self):
        rule = UncategorizedWarningRule(alert=self.alert)

        tx_valid = self.create_expense(50.0, ExpenseCategory.FOOD)
        self.assertFalse(rule.evaluate(tx_valid, []))

        tx_invalid = self.create_expense(50.0, ExpenseCategory.UNCATEGORIZED)
        self.assertTrue(rule.evaluate(tx_invalid, []))

    def test_single_transaction_large_amount(self):
        rule = SingleTransactionRule(
            alert=self.alert,
            operator=RuleOperator.GT,
            threshold=500.0
        )

        tx_normal = self.create_expense(100.0)
        self.assertFalse(rule.evaluate(tx_normal, []))

        tx_large = self.create_expense(600.0)
        self.assertTrue(rule.evaluate(tx_large, []))

    def test_consecutive_overspend(self):
        rule = ConsecutiveOverspendRule(
            alert=self.alert,
            period=3,
            operator=RuleOperator.GT,
            threshold=100.0
        )

        history = [
            self.create_expense(150.0, offset_days=2),
            self.create_expense(120.0, offset_days=1)
        ]

        tx_safe = self.create_expense(50.0, offset_days=0)
        self.assertFalse(rule.evaluate(tx_safe, history))

        tx_overspend = self.create_expense(110.0, offset_days=0)
        self.assertTrue(rule.evaluate(tx_overspend, history))

if __name__ == "__main__":
    unittest.main()