from pathlib import Path
from collections.abc import Sequence
from data_model.schemas import Income, Expense
from dataclasses import asdict
import json
from datetime import date


class GenericOutputParser[T: (Income, Expense)]:
    def __call__(self, path: Path, records: Sequence[T]) -> None:
        with open(file=path, mode="a", encoding="utf-8") as file:
            for item in records:
                json.dump(asdict(item), file)
                file.write("\n")

    @staticmethod
    def _parse_date(record_date: date) -> str:
        return record_date.isoformat()
