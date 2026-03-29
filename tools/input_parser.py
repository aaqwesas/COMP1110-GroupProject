from io import TextIOWrapper
from pathlib import Path
from data_model.schemas import Expense, Income
from collections.abc import Callable, MutableMapping, Generator
from datetime import date
import json
from tools.category_parser import ExpenseCategoryParser, IncomeCategoryParser


class GenericJsonParser[T]:
    def __init__(self, path: Path, item_parser: Callable[[MutableMapping], T]) -> None:
        self._path: Path = path
        self._item_parser: Callable[[MutableMapping], T] = item_parser
        if self._path.suffix.lower() != ".jsonl":
            raise ValueError(f"File must be JSONL format, got: {self._path.suffix}")

    def parse(self) -> Generator[T, None, None]:
        with open(file=self._path, mode="r", encoding="utf-8") as file:
            yield from self._parse_data(file=file)

    def _parse_data(self, file: TextIOWrapper) -> Generator[T, None, None]:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                yield self._item_parser(data)
            except Exception as e:
                print(f"Warning: Line {line_num}: Failed to parse - {e}")
                continue


class ExpenseParser(GenericJsonParser[Expense]):
    def __init__(self, path: Path):
        super().__init__(path=path, item_parser=self._parse_expense)

    @classmethod
    def _parse_expense(cls, item: MutableMapping) -> Expense:
        return Expense(
            id=item["id"],
            date=date.fromisoformat(item["date"]),
            amount=item["amount"],
            category=ExpenseCategoryParser(item["category"]),
            description=item["description"],
        )


class IncomeParser(GenericJsonParser[Income]):
    def __init__(self, path: Path):
        super().__init__(path=path, item_parser=self._parse_income)

    @classmethod
    def _parse_income(cls, item: MutableMapping) -> Income:
        return Income(
            id=item["id"],
            date=date.fromisoformat(item["date"]),
            amount=item["amount"],
            category=IncomeCategoryParser(item["category"]),
            description=item["description"],
        )
