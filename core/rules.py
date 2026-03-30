from collections.abc import Callable
import operator
from datetime import date
from data_model.rules import BudgetRule
from data_model.schemas import Transaction, Expense
from data_model.categories import Categories
from data_model.alerts import Alert

class CategoryBudgetRule(BudgetRule):
    def __init__(self, category: Categories, period: int, operator: Callable[[float, float], bool], threshold: float, alert: Alert):
        self.category = category
        self.period = period
        self.operator = operator
        self.threshold = threshold
        self.alert = alert

    def evaluate(self, transaction: Transaction) -> bool:
        if isinstance(transaction, Expense) and transaction.category == self.category:
            self.current_spending += transaction.amount
            if self.operator(self.current_spending, self.threshold):
                self.alert(message = f"You have exceeded your {self.category.name} budget! "
                                     f"Spent: {self.current_spending}, Limit: {self.threshold}")
                return True
        return False