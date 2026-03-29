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
    FREELANCE = auto()
    UNCATEGORIZED = auto()
