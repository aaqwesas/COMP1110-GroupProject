from typing import Any
from data_model.alerts import Alert
class ConsoleAlert(Alert):

    def __init__(self, message_template: str = "ALERT: {message}"):
        self.message_template = message_template

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        message = kwds.get("message", "Budget threshold exceeded!")
        print(self.message_template.format(message=message))

    class FileAlert(Alert):
        def __init__(self, filepath: str = "data/alerts.log"):
            self.filepath = filepath
        def __call__(self, *args: Any, **kwds: Any) -> Any:
            message = kwds.get("message", "Budget threshold exceeded!")
            with open(self.filepath, "a") as f:
                f.write(f"ALERT: {message}\n")