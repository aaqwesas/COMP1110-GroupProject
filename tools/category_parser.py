from enum import StrEnum

from data_model.categories import ExpenseCategory, IncomeCategory


class GenericCategoryParser[T: StrEnum]:
    def __init__(self, enum_type: type[T], default_category: T):
        self.enum_type: type[T] = enum_type
        self.default_category = default_category

    def __call__(self, input: str) -> T:
        try:
            return self.enum_type[input.upper()]
        except KeyError:
            print(
                f"No such category '{input}', classifying as {self.default_category.name}"
            )
            return self.default_category


IncomeCategoryParser: GenericCategoryParser[IncomeCategory] = GenericCategoryParser(
    enum_type=IncomeCategory, default_category=IncomeCategory.UNCATEGORIZED
)
ExpenseCategoryParser: GenericCategoryParser[ExpenseCategory] = GenericCategoryParser(
    enum_type=ExpenseCategory, default_category=ExpenseCategory.UNCATEGORIZED
)
