from abc import ABC, abstractmethod


class Alert(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...

    def __call__(self, message: str) -> None:
        self.send(message=message)
