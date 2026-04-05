from pathlib import Path
from data_model.alerts import Alert


class ConsoleAlert(Alert):
    def __init__(self, message_template: str = "ALERT: {message}"):
        self.message_template = message_template

    def send(self, message: str) -> None:
        print(self.message_template.format(message=message))


class FileAlert(Alert):
    def __init__(self, filepath: str = "logs/alerts.log"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def send(self, message: str) -> None:
        with open(file=self.filepath, mode="a") as f:
            f.write(f"ALERT: {message}\n")

class JSONFileAlert(Alert):
    def __init__(self, filepath: str = "logs/alerts.jsonl"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def send(self, message: str) -> None:
        from datetime import datetime
        import json

        alert_data: dict[str, str] = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "type": "alert",
        }

        with open(file=self.filepath, mode="a") as f:
            f.write(json.dumps(alert_data) + "\n")
