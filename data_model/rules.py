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
    schema: str
    period: int
    operator: RuleOperator
    threshold: float
    alert: Alert

    def __post_init__(self) -> None:
        if self.period <= 0:
            raise ValueError("Period must be positive")

    @abstractmethod
    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> bool:
        ...

    def get_range(self, ref_date: date) -> tuple[date, date]:
        return ref_date - timedelta(days=self.period), ref_date

    def to_dict(self) -> dict:
        return {
            "rule_type": self.__class__.__name__,
            "schema": self.schema,
            "period": self.period,
            "operator": self.operator.value,
            "threshold": self.threshold,
            "alert_type": self.alert.__class__.__name__
        }

    @classmethod
    def from_dict(cls, data: dict, rule_classes_map: dict, alert_classes_map: dict) -> 'BudgetRule':
        rule_cls = rule_classes_map.get(data.get("rule_type"))
        alert_cls = alert_classes_map.get(data.get("alert_type"))

        if not rule_cls or not alert_cls:
            raise ValueError(
                f"Could not resolve rule type ({data.get('rule_type')}) o alerta ({data.get('alert_type')}).")

        return rule_cls(
            schema=data["schema"],
            period=data["period"],
            operator=RuleOperator(data["operator"]),
            threshold=data["threshold"],
            alert=alert_cls()
        )
