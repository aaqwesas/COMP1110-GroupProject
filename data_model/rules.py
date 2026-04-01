from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta

from data_model.alerts import Alert

from .schemas import Transaction


@dataclass(slots=True)
class BudgetRule(ABC):
    schema: Transaction
    period: int
    operator: Callable[[float, float], bool]
    threshold: float
    alert: Alert

    def __post_init__(self) -> None:
        if self.period <= 0:
            raise ValueError("Period must be positive")

    @abstractmethod
    def evaluate(self, transaction: Transaction) -> bool: ...

    def get_range(self, ref_date: date) -> tuple[date, date]:
        return ref_date, ref_date + timedelta(days=self.period)
