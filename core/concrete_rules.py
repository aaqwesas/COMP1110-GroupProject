from collections.abc import Callable
from dataclasses import dataclass
import operator
from datetime import date
from typing import Any
from data_model.rules import BudgetRule
from data_model.schemas import Transaction, Expense
from data_model.categories import Categories
from data_model.alerts import Alert


@dataclass(slots=True)
class CategoryBudgetRule(BudgetRule):
    current_spending: float = 0.0

    def evaluate(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, Expense):
            return False

        if transaction.category != self.schema.category:
            return False

        self.current_spending += transaction.amount
        if self.operator(self.current_spending, self.threshold):
            self.alert(
                message=f"You have exceeded your {self.schema.category.name} budget! "
                f"Spent: {self.current_spending}, Limit: {self.threshold}"
            )
            return True
        return False
