from dataclasses import dataclass
from data_model.rules import BudgetRule
from data_model.schemas import Transaction, Expense
from collections import defaultdict
from datetime import timedelta

@dataclass(slots=True)
class CategoryBudgetRule(BudgetRule):
    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> bool:
        if not isinstance(transaction, Expense):
            return False

        start_date, end_date = self.get_range(transaction.date)
        period_total = 0.0

        for past_transaction in history:
            if isinstance(past_transaction, Expense):
                if start_date <= past_transaction.date <= end_date:
                    period_total += past_transaction.amount

        total_with_current = period_total + transaction.amount

        if self.operator.evaluate(total_with_current, self.threshold):
            self.alert(
                message = f"You have exceeded your overall budget from the last {self.period} days!"
                f"Limit: {self.threshold:.2f}, Accumulated: {total_with_current:.2f}"
                f"(includes the new transaction of ${transaction.amount:.2f})."
            )
            return True
        return False

@dataclass(slots=True)
class SingleTransactionRule(BudgetRule):
    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> bool:
        if not isinstance(transaction, Expense):
            return False

        if self.operator.evaluate(transaction.amount, self.threshold):
            self.alert(
                message = f"Large transaction alert! A single expense of ${transaction.amount:.2f}"
                          f"exceeded the limit of {self.threshold:.2f}"
                          f"(Description: {transaction.description})."
            )
            return True
        return False

@dataclass(slots=True)
class PercentageThresholdRule(BudgetRule):
    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> bool:
        if not isinstance(transaction, Expense):
            return False

        start_date, end_date = self.get_range(transaction.date)
        overall_total = 0.0
        category_total = 0.0

        for past_transaction in history:
            if isinstance(past_transaction, Expense) and start_date <= past_transaction.date <= end_date:
                overall_total += past_transaction.amount
                if past_transaction.category == transaction.category:
                    category_total += past_transaction.amount

        overall_total += transaction.amount
        category_total += transaction.amount

        if overall_total == 0:
            return False

        ratio = category_total / overall_total

        if self.operator.evaluate(ratio, self.threshold):
            self.alert(
                message=f"Percentage threshold alert! Expenses in {transaction.category.name}"
                        f"now make up {ratio:.1%} of your spending in the last {self.period} days"
                        f"(threshold: {self.threshold:.1%})."
            )
            return True
        return False

@dataclass(slots=True)
class UncategorizedWarningRule(BudgetRule):
    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> bool:
        if not isinstance(transaction, Expense):
            return False

        if transaction.category.name == "UNCATEGORIZED":
            self.alert(
                message=f"Uncategorized expense warning! You recorded an expense of ${transaction.amount:.2f} "
                        f"without assigning a proper category."
            )
            return True
        return False


@dataclass(slots=True)
class ConsecutiveOverspendRule(BudgetRule):
    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> bool:
        if not isinstance(transaction, Expense):
            return False

        num_days = self.period
        start_date = transaction.date - timedelta(days=num_days - 1)
        end_date = transaction.date
        daily_totals = defaultdict(float)
        daily_totals[transaction.date] += transaction.amount

        for past_transaction in history:
            if isinstance(past_transaction, Expense) and start_date <= past_transaction.date <= end_date:
                daily_totals[past_transaction.date] += past_transaction.amount

        consecutive_overspend = True
        for i in range(num_days):
            check_date = start_date + timedelta(days=i)
            if not self.operator.evaluate(daily_totals[check_date], self.threshold):
                consecutive_overspend = False
                break

        if consecutive_overspend:
            self.alert(
                message=f"Consecutive overspend alert! You have exceeded the daily limit of ${self.threshold:.2f} "
                        f"for {num_days} consecutive days."
            )
            return True
        return False