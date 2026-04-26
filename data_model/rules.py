from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
import operator
from data_model.alerts import Alert
from .schemas import Transaction


class RuleOperator(str, Enum):
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    EQ = "=="

    def evaluate(self, a: float, b: float) -> bool:
        ops = {
            RuleOperator.GT: operator.gt,
            RuleOperator.LT: operator.lt,
            RuleOperator.GTE: operator.ge,
            RuleOperator.LTE: operator.le,
            RuleOperator.EQ: operator.eq,
        }
        return ops[self](a, b)


@dataclass(slots=True)
class BudgetRule(ABC):
    alert: Alert
    period: int
    operator: RuleOperator
    threshold: float

    def __post_init__(self) -> None:
        if self.period is not None and self.period <= 0:
            raise ValueError("Period must be positive")

    @abstractmethod
    def evaluate(
        self, transaction: Transaction, history: list[Transaction]
    ) -> bool: ...

    def __str__(self) -> str:
        return self.__class__.__name__

    def get_range(self, ref_date: date) -> tuple[date, date]:
        if self.period is None:
            raise ValueError("This rule doesn't have a set timeframe.")
        return ref_date - timedelta(days=self.period), ref_date

    def to_dict(self) -> dict:
        return {
            "rule_type": str(self),
            "alert_type": str(self.alert),
            "period": self.period,
            "operator": self.operator.value,
            "threshold": self.threshold,
        }

    @classmethod
    def from_dict(
        cls, data: dict, rule_classes_map: dict, alert_classes_map: dict
    ) -> "BudgetRule":
        rule_cls = rule_classes_map.get(data.get("rule_type"))
        alert_cls = alert_classes_map.get(data.get("alert_type"))

        if not rule_cls or not alert_cls:
            raise ValueError(f"Could not resolve the rule or alert type for {data}.")

        kwargs = {"alert": alert_cls()}
        if "period" in data:
            kwargs["period"] = data["period"]
        if "operator" in data:
            kwargs["operator"] = RuleOperator(data["operator"])
        if "threshold" in data:
            kwargs["threshold"] = data["threshold"]

        return rule_cls(**kwargs)
