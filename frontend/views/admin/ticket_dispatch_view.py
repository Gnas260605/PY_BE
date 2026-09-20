from __future__ import annotations

import math
from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.loading import skeleton_loader
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, format_relative_time, truncate
from core.constants import CATEGORY_LABELS, TicketPriority, TicketStatus
from services.ticket_service import ticket_service
from services.user_service import user_service

PRIORITY_WEIGHT = {
    "URGENT": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}


def render_ticket_dispatch_view() -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro")
        if role != "ADMIN":
            ui.label("Bạn không có quyền truy cập màn hình giám sát sự cố.").classes("text-red-600 font-bold p-6")
            return

        # =========================================================================
        # 1. STATE MANAGEMENT
        # =========================================================================
        state: dict[str, Any] = {
            "raw_tickets": [],
            "technicians": [],
            "selected_ids": set(),
            "active_tab": "ALL",
            "is_loading": True,
            "error": None,
            "page": 1,
            "page_size": 25,
        }

        # =========================================================================
        # 2. PAGE HEADER (Compact, Professional Workspace)
        # =========================================================================
        with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200 mb-2.5 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 font-medium"):
                    ui.label("Trang chủ")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Điều hành kỹ thuật")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Giám sát sự cố").classes("text-slate-900 font-semibold")

                ui.label("Giám sát & Điều phối Sự cố").classes("text-xl font-bold text-slate-900 tracking-tight")
                ui.label("Theo dõi, phân công và xử lý các yêu cầu hỗ trợ trong toàn hệ thống.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                async def handle_export_excel() -> None:
                    try:
                        ui.notify("Đang xuất file CSV...", type="info")
                        csv_data = await ticket_service.export_tickets_csv()
                        if isinstance(csv_data, str):
                            encoded_bytes = csv_data.encode("utf-8-sig")
                        elif isinstance(csv_data, bytes):
                            encoded_bytes = csv_data
                        else:
                            encoded_bytes = str(csv_data).encode("utf-8-sig")
                        ui.download(encoded_bytes, "Danh_sach_su_co_UniDesk.csv")
                        toast.success("Đã xuất file CSV thành công!")
                    except Exception as e:
                        toast.show_popup("Lỗi xuất file", "Không thể xuất file CSV từ máy chủ.", type="error", detail=str(e))

                ui.button("Xuất CSV", icon="file_download", on_click=handle_export_excel).props(
                    "outline color=slate-700 dense size=sm"
                ).classes("h-9 px-3.5 text-xs font-semibold rounded-lg bg-white border border-slate-300 shadow-2xs hover:bg-slate-50")

                async def handle_export_excel_true() -> None:
                    try:
                        ui.notify("Đang xuất file Excel...", type="info")
                        excel_data = await ticket_service.export_tickets_excel()
                        ui.download(excel_data, "Danh_sach_su_co_UniDesk.xlsx")
                        toast.success("Đã xuất file Excel thành công!")
                    except Exception as e:
                        toast.show_popup("Lỗi xuất file", "Không thể xuất file Excel từ máy chủ.", type="error", detail=str(e))

                ui.button("Xuất Excel", icon="table_view", on_click=handle_export_excel_true).props(
                    "outline color=green-700 dense size=sm"
                ).classes("h-9 px-3.5 text-xs font-semibold rounded-lg bg-white border border-slate-300 shadow-2xs hover:bg-slate-50")

                ui.button("Tạo ticket mới", icon="add", on_click=lambda: ui.navigate.to("/user/tickets/new")).props(
                    "color=primary unelevated dense size=sm"
                ).classes("h-9 px-4 text-xs font-bold rounded-lg shadow-2xs")

        # =========================================================================
        # 3. KPI SUMMARY & SEGMENTED TABS CONTAINERS
        # =========================================================================
        kpi_container = ui.element("div").classes("w-full grid grid-cols-2 lg:grid-cols-4 gap-2.5 mb-3")
        tabs_container = ui.row().classes("w-full bg-slate-100 p-1 rounded-lg border border-slate-200/80 mb-3 items-center justify-between flex-wrap gap-1")

        # Batch Action Bar (Sticky action bar above table when rows are selected)
        batch_bar_container = ui.column().classes("w-full mb-2.5")

        # Filter Toolbar (Single Row, 38px Height, 8px Radius)
        with ui.card().classes("w-full p-2.5 rounded-lg bg-white border border-slate-200 shadow-2xs mb-3 gap-2"):
            with ui.row().classes("w-full gap-2 items-center flex-wrap"):
                search_input = ui.input(
                    placeholder="Tìm theo mã ticket, tiêu đề, mô tả, người yêu cầu...",
                ).props("outlined dense clearable debounce=300").classes("flex-1 min-w-[280px] text-xs h-9")

                tech_filter = ui.select(
                    {"ALL": "Tất cả Kỹ thuật viên", "UNASSIGNED": "Chưa phân công"},
                    value="ALL",
                    label="Kỹ thuật viên",
                ).props("outlined dense options-dense").classes("w-48 text-xs h-9")

                category_filter = ui.select(
                    {"ALL": "Tất cả phân loại", **CATEGORY_LABELS},
                    value="ALL",
                    label="Phân loại",
                ).props("outlined dense options-dense").classes("w-44 text-xs h-9")

                sort_select = ui.select(
                    {
                        "NEWEST": "Mới nhất trước",
                        "OLDEST": "Cũ nhất trước",
                        "PRIORITY_HIGH": "Ưu tiên cao nhất",
                        "UNASSIGNED_FIRST": "Chưa giao KTV trước",
                    },
                    value="NEWEST",
                    label="Sắp xếp",
                ).props("outlined dense options-dense").classes("w-44 text-xs h-9")

                clear_btn = ui.button("Xóa lọc", icon="filter_alt_off").props("flat dense size=sm color=slate-600").classes("text-xs font-semibold px-2.5 h-9")

                async def handle_manual_refresh() -> None:
                    await fetch_data(force_refresh=True)
                    toast.success("Đã làm mới dữ liệu!")

                ui.button(icon="refresh", on_click=handle_manual_refresh).props("outline dense size=sm color=slate-600").classes("h-9 w-9 shrink-0 rounded-lg")

        # Main Table / List Container
        table_container = ui.column().classes("w-full gap-0")

        # =========================================================================
        # 4. MODALS & DIALOGS (Clean Form Layout & No Raw Exceptions)
        # =========================================================================
        def show_assign_dialog(ticket_ids: list[int], ticket_titles: list[str]) -> None:
            active_techs = [t for t in state["technicians"] if t.get("trang_thai") == "ACTIVE"]
            if not active_techs:
                toast.show_popup("Không có KTV", "Không tìm thấy Kỹ thuật viên nào đang hoạt động trong hệ thống.", type="error")
                return

            with ui.dialog() as dialog, ui.card().classes("w-full max-w-md p-5 rounded-xl bg-white border border-slate-200 shadow-lg"):
                with ui.row().classes("w-full justify-between items-center pb-2.5 border-b border-slate-100"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("person_add", size="sm").classes("text-primary")
                        ui.label("Phân công Kỹ thuật viên").classes("text-base font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm color=slate-400")

                ui.label(
                    f"Chọn Kỹ thuật viên để phân công {len(ticket_ids)} sự cố:"
                ).classes("text-xs text-slate-600 font-medium mt-2")

                with ui.column().classes("w-full max-h-24 overflow-y-auto bg-slate-50 p-2.5 rounded-lg border border-slate-200/70 gap-1"):
                    for title in ticket_titles[:3]:
                        ui.label(f"• {truncate(title, 50)}").classes("text-xs text-slate-700")
                    if len(ticket_titles) > 3:
                        ui.label(f"... và {len(ticket_titles) - 3} sự cố khác").classes("text-[11px] text-slate-500 italic")

                tech_options = {
                    t["id"]: f"{t.get('ho_ten', t.get('username'))} ({t.get('email', '')})"
                    for t in active_techs
                }
                selected_tech_id = ui.select(
                    tech_options,
                    value=active_techs[0]["id"] if active_techs else None,
                    label="Kỹ thuật viên phụ trách",
                ).props("outlined dense options-dense").classes("w-full mt-2.5 text-xs")

                async def handle_submit() -> None:
                    if not selected_tech_id.value:
                        return
                    dialog.close()
                    try:
                        if len(ticket_ids) == 1:
                            await ticket_service.assign_ticket(ticket_ids[0], int(selected_tech_id.value))
                        else:
                            await ticket_service.batch_assign(ticket_ids, int(selected_tech_id.value))

                        state["selected_ids"].clear()
                        toast.success(f"Đã phân công thành công {len(ticket_ids)} sự cố!")
                        await fetch_data(force_refresh=True)
                    except Exception as exc:
                        toast.show_popup("Lỗi phân công", "Không thể cập nhật kỹ thuật viên phụ trách.", type="error", detail=str(exc))

                with ui.row().classes("w-full justify-end gap-2 mt-4 pt-2 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 dense").classes("px-3 text-xs")
                    ui.button("Xác nhận", on_click=handle_submit).props(
                        "color=primary unelevated dense"
                    ).classes("px-4 py-1.5 text-xs font-bold rounded-lg shadow-2xs")

            dialog.open()

        def show_batch_close_dialog(ticket_ids: list[int]) -> None:
            with ui.dialog() as dialog, ui.card().classes("w-full max-w-md p-5 rounded-xl bg-white border border-slate-200 shadow-lg"):
                with ui.row().classes("w-full justify-between items-center pb-2.5 border-b border-slate-100"):
                    with ui.row().classes("items-center gap-2 text-rose-600"):
                        ui.icon("done_all", size="sm")
                        ui.label(f"Đóng {len(ticket_ids)} sự cố hàng loạt").classes("text-base font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm color=slate-400")

                ui.label("Ghi chú đóng sự cố:").classes("text-xs text-slate-600 mt-2")
                note_input = ui.textarea(placeholder="VD: Đã xử lý hoàn tất và xác nhận hoạt động bình thường.").props(
                    "outlined dense rows=3"
                ).classes("w-full mt-1 text-xs")

                async def handle_submit_close() -> None:
                    dialog.close()
                    try:
                        await ticket_service.batch_status(ticket_ids, status="CLOSED", note=note_input.value or "Đóng hàng loạt bởi Admin")
                        state["selected_ids"].clear()
                        toast.success(f"Đã đóng thành công {len(ticket_ids)} sự cố!")
                        await fetch_data(force_refresh=True)
                    except Exception as exc:
                        toast.show_popup("Lỗi đóng sự cố", "Không thể đóng các sự cố đã chọn.", type="error", detail=str(exc))

                with ui.row().classes("w-full justify-end gap-2 mt-4 pt-2 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 dense").classes("px-3 text-xs")
                    ui.button("Đóng sự cố", on_click=handle_submit_close).props(
                        "color=negative unelevated dense"
                    ).classes("px-4 py-1.5 text-xs font-bold rounded-lg")

            dialog.open()

        # =========================================================================
        # 5. DATA FETCHING
        # =========================================================================
        async def fetch_data(force_refresh: bool = False) -> None:
            state["is_loading"] = True
            render_kpis()
            render_tabs()
            render_batch_bar()
            render_table_view()

            try:
                tickets = await ticket_service.list_tickets(refresh=force_refresh)
                technicians = await user_service.list_technicians(refresh=force_refresh)

                state["raw_tickets"] = tickets
                state["technicians"] = technicians
                state["error"] = None

                # Update Tech Filter Dropdown
                active_tech_options = {
                    "ALL": "Tất cả Kỹ thuật viên",
                    "UNASSIGNED": "Chưa phân công",
                    **{t["id"]: t.get("ho_ten", t.get("username")) for t in technicians},
                }
                tech_filter.options = active_tech_options
                tech_filter.update()

            except Exception as exc:
                state["error"] = "Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại dịch vụ Backend."
                toast.show_popup("Lỗi nạp dữ liệu", "Không thể tải danh sách sự cố.", type="error", detail=state["error"])
            finally:
                state["is_loading"] = False
                render_kpis()
                render_tabs()
                render_batch_bar()
                render_table_view()

        # =========================================================================
        # 6. RENDER COMPACT KPI SUMMARY (Height ~85px, Real Data Only, No Fake Sparklines)
        # =========================================================================
        def render_kpis() -> None:
            kpi_container.clear()
            tickets = state["raw_tickets"]
            unassigned_cnt = sum(1 for t in tickets if not t.get("technician_id") and t.get("status") in ("OPEN", "ASSIGNED"))
            critical_cnt = sum(1 for t in tickets if t.get("priority") in ("URGENT", "HIGH") and t.get("status") not in ("RESOLVED", "CLOSED"))
            in_progress_cnt = sum(1 for t in tickets if t.get("status") in ("ASSIGNED", "IN_PROGRESS"))
            open_total_cnt = sum(1 for t in tickets if t.get("status") not in ("RESOLVED", "CLOSED"))
            active_techs_cnt = sum(1 for tc in state["technicians"] if tc.get("trang_thai") == "ACTIVE")

            with kpi_container:
                # 1. Chưa phân công
                with ui.card().classes(
                    "p-3.5 rounded-lg bg-white border border-slate-200 shadow-2xs hover:border-slate-300 transition-all cursor-pointer relative overflow-hidden"
                ).on("click", lambda: set_tab("UNASSIGNED")):
                    ui.element("div").classes("absolute left-0 top-0 bottom-0 w-1 bg-amber-500")
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("CHƯA PHÂN CÔNG").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                        ui.icon("person_search", size="18px").classes("text-amber-500")

                    with ui.row().classes("w-full justify-between items-baseline mt-1.5"):
                        ui.label(str(unassigned_cnt)).classes("text-2xl font-bold text-slate-900")
                        hint_text = "Cần gán KTV" if unassigned_cnt > 0 else "Đã phân công hết"
                        ui.label(hint_text).classes(
                            f"text-[11px] font-semibold {('text-amber-700' if unassigned_cnt > 0 else 'text-slate-400')}"
                        )

                # 2. Khẩn cấp & Cao
                with ui.card().classes(
                    "p-3.5 rounded-lg bg-white border border-slate-200 shadow-2xs hover:border-slate-300 transition-all cursor-pointer relative overflow-hidden"
                ).on("click", lambda: set_tab("CRITICAL")):
                    ui.element("div").classes("absolute left-0 top-0 bottom-0 w-1 bg-rose-500")
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("KHẨN CẤP & CAO").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                        ui.icon("priority_high", size="18px").classes("text-rose-500")

                    with ui.row().classes("w-full justify-between items-baseline mt-1.5"):
                        ui.label(str(critical_cnt)).classes("text-2xl font-bold text-rose-600")
                        hint_text = "Cần ưu tiên xử lý" if critical_cnt > 0 else "Không có vé gấp"
                        ui.label(hint_text).classes(
                            f"text-[11px] font-semibold {('text-rose-700' if critical_cnt > 0 else 'text-slate-400')}"
                        )

                # 3. Đang xử lý
                with ui.card().classes(
                    "p-3.5 rounded-lg bg-white border border-slate-200 shadow-2xs hover:border-slate-300 transition-all cursor-pointer relative overflow-hidden"
                ).on("click", lambda: set_tab("IN_PROGRESS")):
                    ui.element("div").classes("absolute left-0 top-0 bottom-0 w-1 bg-blue-600")
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("ĐANG XỬ LÝ").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                        ui.icon("pending_actions", size="18px").classes("text-blue-500")

                    with ui.row().classes("w-full justify-between items-baseline mt-1.5"):
                        ui.label(str(in_progress_cnt)).classes("text-2xl font-bold text-blue-600")
                        ui.label(f"{active_techs_cnt} KTV trực ban").classes("text-[11px] font-medium text-slate-500")

                # 4. Tổng ticket đang mở
                with ui.card().classes(
                    "p-3.5 rounded-lg bg-white border border-slate-200 shadow-2xs hover:border-slate-300 transition-all cursor-pointer relative overflow-hidden"
                ).on("click", lambda: set_tab("ALL")):
                    ui.element("div").classes("absolute left-0 top-0 bottom-0 w-1 bg-slate-400")
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("TỔNG TICKET ĐANG MỞ").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                        ui.icon("inventory_2", size="18px").classes("text-slate-500")

                    with ui.row().classes("w-full justify-between items-baseline mt-1.5"):
                        ui.label(str(open_total_cnt)).classes("text-2xl font-bold text-slate-900")
                        ui.label(f"Tổng {len(tickets)} sự cố").classes("text-[11px] font-medium text-slate-500")

        # =========================================================================
        # 7. RENDER SEGMENTED TABS (Compact, Solid Dark Active, Neutral Inactive)
        # =========================================================================
        def set_tab(tab_name: str) -> None:
            state["active_tab"] = tab_name
            state["page"] = 1
            render_tabs()
            render_table_view()

        def render_tabs() -> None:
            tabs_container.clear()
            tickets = state["raw_tickets"]
            tab_defs = [
                ("ALL", "Tất cả", len(tickets)),
                ("UNASSIGNED", "Chưa phân công", sum(1 for t in tickets if not t.get("technician_id") and t.get("status") in ("OPEN", "ASSIGNED"))),
                ("CRITICAL", "Khẩn cấp & Cao", sum(1 for t in tickets if t.get("priority") in ("URGENT", "HIGH") and t.get("status") not in ("RESOLVED", "CLOSED"))),
                ("IN_PROGRESS", "Đang xử lý", sum(1 for t in tickets if t.get("status") in ("ASSIGNED", "IN_PROGRESS"))),
                ("RESOLVED", "Đã xử lý / Đóng", sum(1 for t in tickets if t.get("status") in ("RESOLVED", "CLOSED"))),
            ]

            with tabs_container:
                with ui.row().classes("items-center gap-1 flex-wrap"):
                    for key, label, cnt in tab_defs:
                        is_active = state["active_tab"] == key
                        active_style = "bg-slate-900 text-white shadow-2xs font-semibold" if is_active else "text-slate-600 hover:text-slate-900 hover:bg-slate-200/70 font-medium"
                        with ui.button(on_click=lambda k=key: set_tab(k)).props("flat dense").classes(
                            f"h-8 px-3 rounded-md text-xs transition-colors {active_style}"
                        ):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.label(label)
                                ui.label(str(cnt)).classes(
                                    f"px-1.5 py-0.2 rounded-full text-[10px] font-mono {('bg-slate-700 text-slate-100' if is_active else 'bg-slate-200 text-slate-700')}"
                                )

        # =========================================================================
        # 8. RENDER BATCH ACTION BAR (Compact Sticky Header Bar)
        # =========================================================================
        def render_batch_bar() -> None:
            batch_bar_container.clear()
            selected = state["selected_ids"]
            if not selected:
                return

            selected_tickets = [t for t in state["raw_tickets"] if t["id"] in selected]
            selected_titles = [t.get("title", "") for t in selected_tickets]

            with batch_bar_container:
                with ui.row().classes(
                    "w-full bg-slate-900 text-white px-3.5 py-2 rounded-lg shadow-sm justify-between items-center flex-wrap gap-2 animate-fadeIn"
                ):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle", size="16px").classes("text-emerald-400")
                        ui.label(f"{len(selected)} ticket đã chọn").classes("text-xs font-bold text-white")

                    with ui.row().classes("items-center gap-2"):
                        ui.button(
                            "Gán KTV",
                            icon="person_add",
                            on_click=lambda: show_assign_dialog(list(selected), selected_titles),
                        ).props("flat dense size=sm color=white").classes("h-7 bg-white/15 hover:bg-white/25 text-xs font-medium px-2.5 rounded")

                        ui.button(
                            "Đóng ticket",
                            icon="done_all",
                            on_click=lambda: show_batch_close_dialog(list(selected)),
                        ).props("flat dense size=sm color=white").classes("h-7 bg-rose-600/80 hover:bg-rose-600 text-xs font-medium px-2.5 rounded")

                        def clear_selection() -> None:
                            state["selected_ids"].clear()
                            render_batch_bar()
                            render_table_view()

                        ui.button(icon="close", on_click=clear_selection).props("flat round dense size=sm color=slate-400")

        # =========================================================================
        # 9. RENDER OPERATIONAL DATA TABLE (High Density, Clean Enterprise Style)
        # =========================================================================
        def render_table_view() -> None:
            table_container.clear()

            if state["is_loading"]:
                with table_container:
                    with ui.card().classes("w-full p-5 bg-white rounded-lg border border-slate-200 shadow-2xs gap-3"):
                        skeleton_loader(count=8)
                return

            if state["error"]:
                with table_container:
                    with ui.card().classes("w-full p-8 bg-white rounded-lg border border-rose-200 shadow-2xs items-center justify-center text-center"):
                        ui.icon("error_outline", size="md").classes("text-rose-500 mb-1")
                        ui.label("Không thể tải danh sách sự cố").classes("text-base font-bold text-slate-900")
                        ui.label(state["error"]).classes("text-xs text-slate-500 max-w-md")
                        ui.button("Thử lại", icon="refresh", on_click=lambda: fetch_data(force_refresh=True)).props("unelevated color=primary size=sm").classes("mt-3")
                return

            # Filtering & Sorting
            kw = (search_input.value or "").strip().lower()
            tc = tech_filter.value
            cg = category_filter.value
            tab = state["active_tab"]

            filtered = []
            for t in state["raw_tickets"]:
                if tab == "UNASSIGNED" and (t.get("technician_id") or t.get("status") not in ("OPEN", "ASSIGNED")):
                    continue
                if tab == "CRITICAL" and (t.get("priority") not in ("URGENT", "HIGH") or t.get("status") in ("RESOLVED", "CLOSED")):
                    continue
                if tab == "IN_PROGRESS" and t.get("status") not in ("ASSIGNED", "IN_PROGRESS"):
                    continue
                if tab == "RESOLVED" and t.get("status") not in ("RESOLVED", "CLOSED"):
                    continue

                if cg != "ALL" and t.get("category") != cg:
                    continue
                if tc == "UNASSIGNED" and t.get("technician_id"):
                    continue
                if tc not in ("ALL", "UNASSIGNED") and t.get("technician_id") != tc:
                    continue

                if kw:
                    text_corpus = f"{t.get('id', '')} {t.get('title', '')} {t.get('description', '')} {t.get('user_id', '')}".lower()
                    if kw not in text_corpus:
                        continue

                filtered.append(t)

            # Sort
            sort_mode = sort_select.value
            if sort_mode == "PRIORITY_HIGH":
                filtered.sort(key=lambda x: PRIORITY_WEIGHT.get(x.get("priority", ""), 0), reverse=True)
            elif sort_mode == "OLDEST":
                filtered.sort(key=lambda x: x.get("id", 0))
            elif sort_mode == "UNASSIGNED_FIRST":
                filtered.sort(key=lambda x: (x.get("technician_id") is not None, -x.get("id", 0)))
            else:  # NEWEST
                filtered.sort(key=lambda x: x.get("id", 0), reverse=True)

            clear_btn.set_visibility(bool(kw or tc != "ALL" or cg != "ALL" or tab != "ALL"))

            if not filtered:
                with table_container:
                    empty_state(
                        title="Không tìm thấy sự cố",
                        subtitle="Không có ticket nào phù hợp với bộ lọc hiện tại.",
                        icon="search_off",
                    )
                return

            # Pagination
            page_size = state["page_size"]
            total_items = len(filtered)
            total_pages = max(1, math.ceil(total_items / page_size))
            state["page"] = min(state["page"], total_pages)
            start_idx = (state["page"] - 1) * page_size
            end_idx = min(start_idx + page_size, total_items)
            page_items = filtered[start_idx:end_idx]

            # Build Desktop Table Container
            with table_container:
                with ui.card().classes("w-full p-0 bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden"):
                    with ui.column().classes("w-full overflow-x-auto min-w-[1000px] gap-0"):
                        # Table Header Row
                        all_page_selected = bool(page_items and all(t["id"] in state["selected_ids"] for t in page_items))
                        def toggle_all(e: Any) -> None:
                            if e.value:
                                for itm in page_items:
                                    state["selected_ids"].add(itm["id"])
                            else:
                                for itm in page_items:
                                    state["selected_ids"].discard(itm["id"])
                            render_batch_bar()
                            render_table_view()

                        with ui.row().classes("w-full bg-slate-50/90 text-slate-500 text-[11px] font-semibold uppercase tracking-wider py-2.5 px-3.5 items-center border-b border-slate-200"):
                            with ui.row().classes("w-9 justify-center"):
                                ui.checkbox(value=all_page_selected, on_change=toggle_all).props("dense size=xs")

                            ui.label("Mã / Ưu tiên").classes("w-32 font-semibold")
                            ui.label("Sự cố & Nội dung").classes("flex-1 min-w-[260px] font-semibold")
                            ui.label("Người yêu cầu").classes("w-40 font-semibold")
                            ui.label("KTV phụ trách").classes("w-48 font-semibold")
                            ui.label("Cập nhật").classes("w-32 font-semibold")
                            ui.label("Trạng thái").classes("w-36 font-semibold")
                            ui.label("Thao tác").classes("w-16 text-right font-semibold")

                        # Table Body Rows (64-72px Row Height)
                        with ui.column().classes("w-full divide-y divide-slate-100 gap-0"):
                            for t in page_items:
                                t_id = t.get("id")
                                priority = t.get("priority", "MEDIUM")
                                is_urgent = priority == "URGENT"
                                is_high = priority == "HIGH"

                                border_accent = ""
                                if is_urgent:
                                    border_accent = "border-l-4 border-l-rose-500 bg-rose-50/15"
                                elif is_high:
                                    border_accent = "border-l-4 border-l-amber-500 bg-amber-50/10"
                                else:
                                    border_accent = "hover:bg-slate-50/80 bg-white"

                                with ui.row().classes(f"w-full px-3.5 py-2.5 items-center justify-between transition-colors {border_accent}"):
                                    # 1. Checkbox
                                    with ui.row().classes("w-9 justify-center"):
                                        is_checked = t_id in state["selected_ids"]
                                        def toggle_single(e: Any, tid=t_id) -> None:
                                            if e.value:
                                                state["selected_ids"].add(tid)
                                            else:
                                                state["selected_ids"].discard(tid)
                                            render_batch_bar()

                                        ui.checkbox(value=is_checked, on_change=toggle_single).props("dense size=xs")

                                    # 2. Ticket ID & Priority Badge
                                    with ui.column().classes("w-32 gap-1 items-start"):
                                        ui.label(f"#TK-{t_id:04d}").classes(
                                            "font-mono font-bold text-xs text-slate-900 hover:text-primary cursor-pointer"
                                        ).on("click", lambda tid=t_id: ui.navigate.to(f"/tickets/{tid}"))
                                        priority_badge(priority)

                                    # 3. Title & Subtitle Metadata
                                    with ui.column().classes("flex-1 min-w-[260px] gap-0.5 pr-2"):
                                        ui.label(t.get("title", "")).classes(
                                            "font-semibold text-slate-900 hover:text-primary cursor-pointer line-clamp-1 text-sm leading-snug"
                                        ).on("click", lambda tid=t_id: ui.navigate.to(f"/tickets/{tid}"))

                                        if t.get("description"):
                                            ui.label(truncate(t["description"], 80)).classes("text-slate-500 line-clamp-1 text-xs")

                                        category_text = CATEGORY_LABELS.get(t.get("category", ""), t.get("category", ""))
                                        ui.label(category_text).classes("text-[11px] text-slate-400 font-medium")

                                    # 4. User
                                    with ui.row().classes("w-40 items-center gap-2"):
                                        with ui.element("div").classes(
                                            "w-7 h-7 rounded-full bg-slate-100 text-slate-700 font-bold text-xs flex items-center justify-center shrink-0 border border-slate-200"
                                        ):
                                            ui.label(f"U{t.get('user_id', '?')}")
                                        with ui.column().classes("gap-0 min-w-0"):
                                            ui.label(f"Người dùng #{t.get('user_id', '')}").classes("font-medium text-slate-900 truncate text-xs")

                                    # 5. Technician
                                    with ui.row().classes("w-48 items-center gap-2"):
                                        tech_id = t.get("technician_id")
                                        if tech_id:
                                            tech_match = next((tc for tc in state["technicians"] if tc["id"] == tech_id), None)
                                            tech_name = tech_match.get("ho_ten", tech_match.get("username", f"KTV #{tech_id}")) if tech_match else f"KTV #{tech_id}"
                                            with ui.element("div").classes(
                                                "w-6 h-6 rounded-full bg-blue-50 text-blue-700 font-bold text-[10px] flex items-center justify-center shrink-0 border border-blue-200"
                                            ):
                                                ui.label("KT")
                                            ui.label(tech_name).classes("font-medium text-slate-800 truncate max-w-[130px] text-xs")
                                        else:
                                            ui.button(
                                                "+ Gán KTV",
                                                icon="person_add",
                                                on_click=lambda tid=t_id, tit=t.get("title", ""): show_assign_dialog([tid], [tit]),
                                            ).props("outline size=sm color=primary dense").classes(
                                                "h-8.5 border-dashed text-xs font-bold px-3 rounded-lg hover:bg-blue-50 shadow-2xs"
                                            )

                                    # 6. Updated Relative Time (With exact datetime tooltip)
                                    with ui.column().classes("w-32 gap-0"):
                                        exact_dt = format_datetime(t.get("updated_at") or t.get("created_at"))
                                        rel_label = ui.label(format_relative_time(t.get("updated_at") or t.get("created_at"))).classes(
                                            "font-mono text-slate-700 text-xs"
                                        )
                                        rel_label.tooltip(f"Cập nhật: {exact_dt}")

                                    # 7. Status
                                    with ui.column().classes("w-36 items-start"):
                                        status_badge(t.get("status"))

                                    # 8. Row Action (Contextual Navigation)
                                    with ui.row().classes("w-16 justify-end items-center"):
                                        ui.button(
                                            icon="arrow_forward",
                                            on_click=lambda tid=t_id: ui.navigate.to(f"/tickets/{tid}"),
                                        ).props("outline dense size=sm color=slate-600").classes("w-8.5 h-8.5 rounded-lg border-slate-300 text-slate-700 hover:bg-slate-100 hover:text-primary shrink-0").tooltip("Xem chi tiết sự cố")

                    # Pagination Footer (Compact 1–25 / Total format)
                    with ui.row().classes("w-full justify-between items-center px-4 py-2.5 bg-slate-50/70 border-t border-slate-200 flex-wrap gap-2 text-xs text-slate-600"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(f"{start_idx + 1}–{end_idx} / {total_items} sự cố").classes("font-medium")
                            ui.label("•").classes("text-slate-300")
                            ui.label("Hiển thị:")
                            page_size_select = ui.select(
                                [10, 25, 50, 100],
                                value=state["page_size"],
                            ).props("outlined dense options-dense").classes("w-16 text-xs")

                            def on_page_size_change(e: Any) -> None:
                                state["page_size"] = int(e.value)
                                state["page"] = 1
                                render_table_view()

                            page_size_select.on("update:model-value", on_page_size_change)

                        with ui.row().classes("items-center gap-1"):
                            def prev_page() -> None:
                                if state["page"] > 1:
                                    state["page"] -= 1
                                    render_table_view()

                            def next_page() -> None:
                                if state["page"] < total_pages:
                                    state["page"] += 1
                                    render_table_view()

                            prev_btn = ui.button(icon="chevron_left", on_click=prev_page).props("flat dense size=sm color=slate-700").classes("h-7 w-7 rounded")
                            if state["page"] <= 1:
                                prev_btn.props("disable")

                            ui.label(f"Trang {state['page']} / {total_pages}").classes("text-xs font-semibold text-slate-700 px-2")

                            next_btn = ui.button(icon="chevron_right", on_click=next_page).props("flat dense size=sm color=slate-700").classes("h-7 w-7 rounded")
                            if state["page"] >= total_pages:
                                next_btn.props("disable")

        # Connect event listeners
        search_input.on("update:model-value", lambda _: render_table_view())
        tech_filter.on("update:model-value", lambda _: render_table_view())
        category_filter.on("update:model-value", lambda _: render_table_view())
        sort_select.on("update:model-value", lambda _: render_table_view())

        def reset_all_filters() -> None:
            search_input.value = ""
            tech_filter.value = "ALL"
            category_filter.value = "ALL"
            sort_select.value = "NEWEST"
            state["active_tab"] = "ALL"
            state["page"] = 1
            render_tabs()
            render_table_view()

        clear_btn.on("click", reset_all_filters)

        # Initial Load
        ui.timer(0.05, lambda: fetch_data(), once=True)

    app_shell("Giám sát & Điều phối Sự cố", content)
