import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(log_level: str, log_to_file: bool = False, log_file: str = "logs/backend.log") -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)

    if not any(getattr(handler, "_cs466_console", False) for handler in root_logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        console_handler._cs466_console = True
        root_logger.addHandler(console_handler)

    for handler in root_logger.handlers:
        handler.setLevel(level)

    if not log_to_file:
        for handler in list(root_logger.handlers):
            if getattr(handler, "_cs466_file", None):
                root_logger.removeHandler(handler)
                handler.close()
        return

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_log_path = str(log_path.resolve())

    for handler in root_logger.handlers:
        if getattr(handler, "_cs466_file", None) == resolved_log_path:
            return

    file_handler = RotatingFileHandler(
        resolved_log_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    file_handler._cs466_file = resolved_log_path
    root_logger.addHandler(file_handler)
