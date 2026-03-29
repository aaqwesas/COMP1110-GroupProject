from enum import StrEnum
import json
from pathlib import Path
from collections.abc import Sequence
import dataclasses




class GenericOutputParser[T: dataclasses.]:
    def __call__(self, path: Path, records: Sequence[type[T]] ) -> None:
        with open(file=path, mode="a", encoding="utf-8") as file:
            for item in records:
                file.write(item.to_dict(), )