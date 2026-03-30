from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import date, timedelta

from data_model.alerts import Alert

from .categories import Categories
from .schemas import Transaction


class BudgetRule(ABC):
    schema: Transaction
    period: int
    operator: Callable[[int, int], bool]
    threshold: int
    alert: Alert

    @abstractmethod
    def evaluate(self, Transaction) -> bool: ...

    def get_range(self, ref_date: date) -> tuple[date, date]:
        return ref_date, ref_date + timedelta(days=self.period)
