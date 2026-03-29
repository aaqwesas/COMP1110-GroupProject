from pathlib import Path
from collections.abc import Sequence
from data_model.schemas import Income, Expense
import json
from datetime import date
from typing import TypedDict


class ParsedFormat(TypedDict):
    id: str
    date: str
    amount: float
    category: str
    description: str

class GenericOutputParser[T: (Income, Expense)]:
    def __call__(self, path: Path, records: Sequence[T]) -> None:
        with open(file=path, mode="a", encoding="utf-8") as file:
            for item in records:
                parsed_dict = ParsedFormat(
                    id=item.id,
                    date=item.date.isoformat(),
                    amount=item.amount,
                    category=item.category.name,
                    description=item.description
                )

                json.dump(parsed_dict, file)
                file.write("\n")
