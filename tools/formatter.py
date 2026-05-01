import logging
from typing import Union

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[95m",
    }
    RESET = "\033[0m"

    def format(self, record) -> str:

        if record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            record.msg = f"{color}{record.msg}{self.RESET}"

        result = super().format(record)

        return result


def set_logger(
    level: Union[int, str] = logging.DEBUG,
    fmt: str = "%(asctime)s | %(levelname)-8s | %(message)s",
) -> logging.Logger:

    logger = logging.getLogger()
    logger.setLevel(level=level)

    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter(fmt=fmt))
    logger.addHandler(handler)
    return logger


# Test
if __name__ == "__main__":
    logger = set_logger(logging.DEBUG)

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
