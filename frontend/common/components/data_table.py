from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui import ui

from common.components.responsive_card import ticket_card
from common.styles.breakpoints import DESKTOP_ONLY, MOBILE_ONLY


def adaptive_ticket_list(
    tickets: list[dict[str, Any]],
    columns: list[dict[str, str]],
    *,
    on_detail: Callable[[dict[str, Any]], None] | None = None,
    on_action: Callable[[dict[str, Any]], None] | None = None,
) -> None:
    with ui.element("div").classes(f"w-full {DESKTOP_ONLY}"):
        ui.table(columns=columns, rows=tickets, row_key="id", pagination=10).classes("w-full")

    with ui.column().classes(f"w-full gap-3 {MOBILE_ONLY}"):
        if not tickets:
            ui.label("Chưa có dữ liệu.").classes("text-sm text-slate-500")
        for ticket in tickets:
            ticket_card(ticket, on_detail=on_detail, on_action=on_action)
