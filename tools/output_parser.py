from io import TextIOWrapper
from pathlib import Path
from collections.abc import Iterable
from data_model.schemas import Transaction
import json
from datetime import date
from typing import TypedDict


class ParsedFormat(TypedDict):
    id: str
    date: str
    amount: float
    category: str
    description: str


class GenericOutputParser[T: Transaction]:
    def __call__(self, path: Path, records: Iterable[T]) -> None:
        with open(file=path, mode="a", encoding="utf-8") as file:
            for item in records:
                self._handle_record(item=item, file=file)

    def _handle_record(self, item: T, file: TextIOWrapper) -> None:
        parsed_dict = ParsedFormat(
            id=item.id,
            date=item.date.isoformat(),
            amount=item.amount,
            category=item.category.name,
            description=item.description,
        )

        json.dump(parsed_dict, file)
        file.write("\n")
