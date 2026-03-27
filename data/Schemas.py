from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, unique, auto


@unique
class SpedningCategory(StrEnum):
    EDUCATION = auto()
    RENT = auto()
    FOOD = auto()
    GIFT = auto()
    DRINKS = auto()
    TRAFFIC = auto()
    ENTERTAINMENT = auto()
    MEDICAL = auto()
    SOCIAL = auto()
    UNCATEORIED = auto()


@unique
class IncomeCategory(StrEnum):
    SALARY = auto()
    BONUS = auto()
    INVESTMENT = auto()
    TRADE = auto()
    DIVIDEND = auto()
    UNCATEORIED = auto()


@dataclass(slots=True, frozen=True)
class Expense:
    date: datetime
    amount: float
    category: SpedningCategory
    description: str


@dataclass(frozen=True, slots=True)
class Income:
    date: datetime
    amount: float
    category: IncomeCategory
    description: str
