from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import date, timedelta
from .schemas import Transcation


class BudgetRule(ABC):
    category: Transcation
    period: int
    operator: Callable[[int, int], bool]

    @abstractmethod
    def evaluate(self, Transcation) -> bool: ...

    def get_range(self, ref_date: date) -> tuple[date, date]:
        return ref_date, ref_date + timedelta(days=self.period)
