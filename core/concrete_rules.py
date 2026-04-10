from dataclasses import dataclass
from data_model.rules import BudgetRule
from data_model.schemas import Transaction, Expense

@dataclass(slots=True)
class CategoryBudgetRule(BudgetRule):
    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> bool:
        if not isinstance(transaction, Expense):
            return False

        start_date, end_date = self.get_range(transaction.date)
        period_total = 0.0

        for transaction in history:
            if isinstance(transaction, Expense):
                if start_date <= transaction.date <= end_date:
                    period_total += transaction.amount

        total_with_current = period_total + transaction.amount

        if self.operator(total_with_current, self.threshold):
            self.alert(
                message = f"You have exceeded your overall budget from the last {self.period} days!"
                f"Limit: {self.threshold:.2f}, Accumulated: {total_with_current:.2f}"
                f"(includes the new transaction of ${transaction.amount:.2f})"
            )
            return True
        return False

@dataclass(slots=True)
class SingleTransactionRule(BudgetRule):
    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> bool:

        if not isinstance(transaction, Expense):
            return False

        if self.operator(transaction.amount, self.threshold):
            self.alert(
                message = f"Large transaction alert! A single expense of ${transaction.amount:.2f}"
                          f"exceeded the limit of {self.threshold:.2f}"
                          f"(Description: {transaction.description})."
            )
            return True
        return False