from nicegui import ui


def success(message: str) -> None:
    ui.notify(message, type="positive", position="top-right")


def error(message: str) -> None:
    ui.notify(message, type="negative", position="top-right")


def warning(message: str) -> None:
    ui.notify(message, type="warning", position="top-right")


def show(message: str, type: str = "info") -> None:
    t = "positive" if type in ("positive", "success") else ("negative" if type in ("negative", "error") else ("warning" if type == "warning" else "info"))
    ui.notify(message, type=t, position="top-right")
