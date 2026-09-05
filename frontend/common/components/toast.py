from nicegui import ui


def success(message: str) -> None:
    ui.notify(message, type="positive", position="top-right")


def error(message: str) -> None:
    ui.notify(message, type="negative", position="top-right")


def warning(message: str) -> None:
    ui.notify(message, type="warning", position="top-right")
