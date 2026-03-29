from dataclasses import dataclass
from datetime import date
from .categories import ExpenseCategory, IncomeCategory


@dataclass(slots=True)
class Expense:
    id: str
    date: date
    amount: float
    category: ExpenseCategory
    description: str


@dataclass(slots=True)
class Income:
    id: str
    date: date
    amount: float
    category: IncomeCategory
    description: str
