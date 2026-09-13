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
    if not tickets:
        with ui.column().classes("w-full items-center py-10"):
            ui.icon("receipt_long", size="4rem").classes("text-slate-300")
            ui.label("Chưa có dữ liệu.").classes("text-slate-500 mt-2")
        return

    with ui.element("div").classes(f"w-full {DESKTOP_ONLY}"):
        table_cols = list(columns)
        if on_action or on_detail:
            table_cols.append({"name": "actions", "label": "Thao tác", "field": "actions", "align": "center"})

        table = ui.table(columns=table_cols, rows=tickets, row_key="id", pagination=10).classes("w-full")
        table.add_slot('body-cell-actions', '''
            <q-td :props="props">
                <q-btn v-if="''' + str(bool(on_detail)).lower() + '''" flat round size="sm" color="info" icon="visibility" @click="() => $parent.$emit('detail', props.row)">
                    <q-tooltip>Chi tiết</q-tooltip>
                </q-btn>
                <q-btn v-if="''' + str(bool(on_action)).lower() + '''" flat round size="sm" color="primary" icon="edit" @click="() => $parent.$emit('action', props.row)">
                    <q-tooltip>Cập nhật/Assign</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        if on_detail:
            table.on('detail', lambda e: on_detail(e.args))
        if on_action:
            table.on('action', lambda e: on_action(e.args))

    with ui.column().classes(f"w-full gap-3 {MOBILE_ONLY}"):
        for ticket in tickets:
            ticket_card(ticket, on_detail=on_detail, on_action=on_action)
