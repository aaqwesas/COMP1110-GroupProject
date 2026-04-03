from dataclasses import dataclass
import operator
from data_model.rules import BudgetRule
from data_model.schemas import Transaction, Expense


@dataclass(slots=True)
class CategoryBudgetRule(BudgetRule):
    def evaluate(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, Expense):
            return False

        if transaction.category != self.schema.category:
            return False

        if self.operator(transaction.amount, self.threshold):
            self.alert(
                message=f"You have exceeded your {self.schema.category.name} budget! "
                f"Spent: {transaction.amount}, Limit: {self.threshold}"
            )
            return True
        return False
