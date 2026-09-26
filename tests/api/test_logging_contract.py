import logging
from pathlib import Path

from app.core.logging import configure_logging


def _cs466_handlers():
    return [
        handler
        for handler in logging.getLogger().handlers
        if getattr(handler, "_cs466_console", False) or getattr(handler, "_cs466_file", None)
    ]


def test_configure_logging_does_not_duplicate_handlers(tmp_path: Path):
    log_file = tmp_path / "backend.log"

    for handler in list(_cs466_handlers()):
        logging.getLogger().removeHandler(handler)
        handler.close()

    configure_logging("INFO", True, str(log_file))
    configure_logging("INFO", True, str(log_file))

    handlers = _cs466_handlers()
    console_handlers = [handler for handler in handlers if getattr(handler, "_cs466_console", False)]
    file_handlers = [handler for handler in handlers if getattr(handler, "_cs466_file", None)]

    assert len(console_handlers) == 1
    assert len(file_handlers) == 1

    configure_logging("INFO", False, str(log_file))

    handlers = _cs466_handlers()
    assert len([handler for handler in handlers if getattr(handler, "_cs466_console", False)]) == 1
    assert not [handler for handler in handlers if getattr(handler, "_cs466_file", None)]
