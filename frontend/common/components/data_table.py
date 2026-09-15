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

        with ui.card().classes("w-full p-0 rounded-2xl bg-white border border-slate-200/80 shadow-xs overflow-hidden"):
            table = ui.table(columns=table_cols, rows=tickets, row_key="id", pagination=10).classes("w-full shadow-none border-none")
            
            # Custom ID slot
            table.add_slot(
                "body-cell-id",
                """
                <q-td :props="props">
                    <span class="font-mono text-xs font-bold text-slate-700">#{{ props.row.id }}</span>
                </q-td>
                """,
            )

            # Custom Priority slot
            table.add_slot(
                "body-cell-priority",
                """
                <q-td :props="props">
                    <span v-if="props.row.priority === 'URGENT'" class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-100">Khẩn cấp</span>
                    <span v-else-if="props.row.priority === 'HIGH'" class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-100">Cao</span>
                    <span v-else-if="props.row.priority === 'MEDIUM'" class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-100">Trung bình</span>
                    <span v-else class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600 border border-slate-200">Thấp</span>
                </q-td>
                """,
            )

            # Custom Status slot
            table.add_slot(
                "body-cell-status",
                """
                <q-td :props="props">
                    <span v-if="props.row.status === 'IN_PROGRESS'" class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-100 flex items-center justify-center gap-1 w-fit mx-auto">
                        <span class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span> Đang xử lý
                    </span>
                    <span v-else-if="props.row.status === 'ASSIGNED'" class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100 flex items-center justify-center gap-1 w-fit mx-auto">
                        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500"></span> Đã tiếp nhận
                    </span>
                    <span v-else-if="props.row.status === 'RESOLVED'" class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100 flex items-center justify-center gap-1 w-fit mx-auto">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Đã giải quyết
                    </span>
                    <span v-else-if="props.row.status === 'CLOSED'" class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-600 border border-slate-200 flex items-center justify-center gap-1 w-fit mx-auto">
                        Đã đóng
                    </span>
                    <span v-else class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-100 flex items-center justify-center gap-1 w-fit mx-auto">
                        <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Chờ xử lý
                    </span>
                </q-td>
                """,
            )

            table.add_slot('body-cell-actions', '''
                <q-td :props="props">
                    <div class="flex items-center justify-center gap-1">
                        <q-btn v-if="''' + str(bool(on_detail)).lower() + '''" flat round size="sm" color="info" icon="visibility" @click="() => $parent.$emit('detail', props.row)">
                            <q-tooltip>Chi tiết ticket</q-tooltip>
                        </q-btn>
                        <q-btn v-if="''' + str(bool(on_action)).lower() + '''" flat round size="sm" color="primary" icon="edit" @click="() => $parent.$emit('action', props.row)">
                            <q-tooltip>Cập nhật/Assign</q-tooltip>
                        </q-btn>
                    </div>
                </q-td>
            ''')
            if on_detail:
                table.on('detail', lambda e: on_detail(e.args))
            if on_action:
                table.on('action', lambda e: on_action(e.args))

    with ui.column().classes(f"w-full gap-3 {MOBILE_ONLY}"):
        for ticket in tickets:
            ticket_card(ticket, on_detail=on_detail, on_action=on_action)
