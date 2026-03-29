from dataclasses import dataclass
from datetime import date
from enum import StrEnum, unique, auto


@unique
class ExpenseCategory(StrEnum):
    EDUCATION = auto()
    RENT = auto()
    FOOD = auto()
    DRINKS = auto()
    TRAFFIC = auto()
    SUBSCRIPTION = auto()
    ENTERTAINMENT = auto()
    MEDICAL = auto()
    UNCATEGORIZED = auto()


@unique
class IncomeCategory(StrEnum):
    SALARY = auto()
    BONUS = auto()
    INVESTMENT = auto()
    TRADE = auto()
    DIVIDEND = auto()
    UNCATEGORIZED = auto()


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
