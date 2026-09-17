from __future__ import annotations

import math
from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.loading import skeleton_loader
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_relative_time, truncate
from core.constants import CATEGORY_LABELS, TicketPriority, TicketStatus
from services.ticket_service import ticket_service
from services.user_service import user_service

PRIORITY_WEIGHT = {
    "URGENT": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}

# SVG Sparklines
SPARKLINE_AMBER = """
<svg class="w-20 h-8 text-amber-500 overflow-visible" fill="none" viewBox="0 0 64 24">
  <path d="M0 18 Q 16 12, 32 16 T 64 4" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="2.5"></path>
  <path d="M0 18 Q 16 12, 32 16 T 64 4 L 64 24 L 0 24 Z" fill="currentColor" fill-opacity="0.15"></path>
</svg>
"""

SPARKLINE_RED = """
<svg class="w-20 h-8 text-rose-500 overflow-visible" fill="none" viewBox="0 0 64 24">
  <path d="M0 20 L 16 14 L 32 17 L 48 8 L 64 2" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"></path>
  <path d="M0 20 L 16 14 L 32 17 L 48 8 L 64 2 L 64 24 L 0 24 Z" fill="currentColor" fill-opacity="0.18"></path>
</svg>
"""

SPARKLINE_BLUE = """
<svg class="w-20 h-8 text-blue-500 overflow-visible" fill="none" viewBox="0 0 64 24">
  <path d="M0 12 Q 18 4, 32 10 T 64 8" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="2.5"></path>
  <path d="M0 12 Q 18 4, 32 10 T 64 8 L 64 24 L 0 24 Z" fill="currentColor" fill-opacity="0.15"></path>
</svg>
"""

SPARKLINE_EMERALD = """
<svg class="w-20 h-8 text-emerald-500 overflow-visible" fill="none" viewBox="0 0 64 24">
  <path d="M0 16 Q 20 8, 36 12 T 64 3" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="2.5"></path>
  <path d="M0 16 Q 20 8, 36 12 T 64 3 L 64 24 L 0 24 Z" fill="currentColor" fill-opacity="0.15"></path>
</svg>
"""


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
        # 2. TOP BAR / BREADCRUMB & HEADER
        # =========================================================================
        with ui.row().classes("w-full justify-between items-center py-3 border-b border-slate-200 mb-4 flex-wrap gap-3"):
            with ui.column().classes("gap-1"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 font-semibold"):
                    ui.label("Trang chủ")
                    ui.icon("chevron_right", size="14px").classes("text-slate-400")
                    ui.label("Điều hành kỹ thuật")
                    ui.icon("chevron_right", size="14px").classes("text-slate-400")
                    ui.label("Giám sát & Điều phối").classes("text-primary font-bold")

                with ui.row().classes("items-center gap-3"):
                    ui.label("Giám sát & Điều phối Sự cố").classes("text-2xl font-extrabold text-slate-900 tracking-tight")
                    ui.label("TRỰC BAN LIVE").classes(
                        "text-xs font-bold tracking-wider px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 shadow-2xs"
                    )

                ui.label("Theo dõi, phân công và xử lý các yêu cầu hỗ trợ trong toàn hệ thống.").classes("text-sm text-slate-500")

            with ui.row().classes("items-center gap-3"):
                async def handle_export_excel() -> None:
                    try:
                        ui.notify("Đang xuất file danh sách sự cố...", type="info")
                        csv_data = await ticket_service.export_tickets_csv()
                        ui.download(csv_data.encode("utf-8-sig"), "Danh_sach_su_co_UniDesk.csv")
                        toast.success("Đã xuất file CSV thành công!")
                    except Exception as e:
                        toast.show_popup("Lỗi xuất file", type="error", detail=str(e))

                ui.button("Xuất Excel / CSV", icon="file_download", on_click=handle_export_excel).props(
                    "outline color=slate-800"
                ).classes("h-11 px-4 text-sm font-bold rounded-xl shadow-xs hover:bg-slate-50")

                ui.button("Tạo ticket mới", icon="add", on_click=lambda: ui.navigate.to("/user/tickets/new")).props(
                    "color=primary unelevated"
                ).classes("h-11 px-5 text-sm font-bold shadow-md rounded-xl")

        # =========================================================================
        # 3. KPI CONTAINERS & SEGMENTED TABS
        # =========================================================================
        kpi_container = ui.element("div").classes("w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4")
        tabs_container = ui.row().classes("w-full justify-between items-center bg-white rounded-2xl p-2 border border-slate-200/90 shadow-xs mb-4 flex-wrap gap-2")

        # Batch Action Bar (Sticky floating bar when rows are selected)
        batch_bar_container = ui.column().classes("w-full mb-3")

        # Search & Filter Toolbar (Compact, Unified - No Duplicate Status/Priority Dropdowns)
        with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs mb-4 gap-3"):
            with ui.row().classes("w-full gap-3 items-center flex-wrap"):
                search_input = ui.input(
                    placeholder="Tìm theo mã ticket (#TK-xxx), tiêu đề, người yêu cầu...",
                ).props("outlined dense clearable debounce=300").classes("flex-1 min-w-[320px] text-sm")

                tech_filter = ui.select(
                    {"ALL": "Tất cả Kỹ thuật viên", "UNASSIGNED": "👤 Chưa phân công"},
                    value="ALL",
                    label="Kỹ thuật viên",
                ).props("outlined dense options-dense").classes("w-56 text-sm")

                category_filter = ui.select(
                    {"ALL": "Tất cả phân loại sự cố", **CATEGORY_LABELS},
                    value="ALL",
                    label="Phân loại sự cố",
                ).props("outlined dense options-dense").classes("w-52 text-sm")

                sort_select = ui.select(
                    {
                        "NEWEST": "🕒 Mới nhất trước",
                        "OLDEST": "⏳ Cũ nhất trước",
                        "PRIORITY_HIGH": "⚡ Ưu tiên cao nhất",
                        "UNASSIGNED_FIRST": "👤 Chưa giao KTV trước",
                    },
                    value="NEWEST",
                    label="Sắp xếp",
                ).props("outlined dense options-dense").classes("w-48 text-sm")

                clear_btn = ui.button("Xóa lọc", icon="filter_alt_off").props("flat color=slate-600").classes("h-10 text-xs font-bold px-3")

                async def handle_manual_refresh() -> None:
                    await fetch_data(force_refresh=True)
                    toast.success("Đã làm mới bảng sự cố!")

                ui.button(icon="refresh", on_click=handle_manual_refresh).props("outline color=slate-700").classes("h-10 w-10 shrink-0 rounded-xl")

        # Table & Data Container
        table_container = ui.column().classes("w-full gap-0")

        # =========================================================================
        # 4. MODALS & DIALOGS
        # =========================================================================
        def show_assign_dialog(ticket_ids: list[int], ticket_titles: list[str]) -> None:
            active_techs = [t for t in state["technicians"] if t.get("trang_thai") == "ACTIVE"]
            if not active_techs:
                toast.show_popup("Không có KTV", type="error", detail="Không tìm thấy Kỹ thuật viên nào đang hoạt động.")
                return

            with ui.dialog() as dialog, ui.card().classes("w-full max-w-md p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xl"):
                with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("person_add", size="sm").classes("text-primary")
                        ui.label("Phân công Kỹ thuật viên").classes("text-lg font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm color=slate-400")

                ui.label(
                    f"Đang chọn {len(ticket_ids)} sự cố để phân công trực tiếp:"
                ).classes("text-xs text-slate-600 font-semibold mt-2")

                with ui.column().classes("w-full max-h-28 overflow-y-auto bg-slate-50 p-3 rounded-xl border border-slate-200/70 gap-1.5"):
                    for title in ticket_titles[:3]:
                        ui.label(f"• {truncate(title, 45)}").classes("text-xs text-slate-700 font-medium")
                    if len(ticket_titles) > 3:
                        ui.label(f"... và {len(ticket_titles) - 3} sự cố khác").classes("text-[11px] text-slate-500 italic")

                tech_options = {
                    t["id"]: f"{t.get('ho_ten', t.get('username'))} ({t.get('email', '')})"
                    for t in active_techs
                }
                selected_tech_id = ui.select(
                    tech_options,
                    value=active_techs[0]["id"] if active_techs else None,
                    label="Chọn Kỹ thuật viên trực ban",
                ).props("outlined dense options-dense").classes("w-full mt-3")

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
                        toast.show_popup("Lỗi phân công", type="error", detail=str(exc))

                with ui.row().classes("w-full justify-end gap-3 mt-5 pt-3 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600").classes("px-4 text-xs font-semibold")
                    ui.button("Xác nhận phân công", on_click=handle_submit).props(
                        "color=primary unelevated"
                    ).classes("px-5 py-2 text-xs font-bold rounded-xl shadow-xs")

            dialog.open()

        def show_batch_close_dialog(ticket_ids: list[int]) -> None:
            with ui.dialog() as dialog, ui.card().classes("w-full max-w-md p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xl"):
                with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                    with ui.row().classes("items-center gap-2 text-rose-600"):
                        ui.icon("done_all", size="sm")
                        ui.label(f"Đóng {len(ticket_ids)} sự cố hàng loạt").classes("text-lg font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm color=slate-400")

                ui.label("Nhập ghi chú hoặc kết quả khắc phục sự cố:").classes("text-xs text-slate-600 mt-2")
                note_input = ui.textarea(placeholder="VD: Đã khắc phục sự cố và kiểm thử hoạt động bình thường.").props(
                    "outlined dense rows=3"
                ).classes("w-full mt-1")

                async def handle_submit_close() -> None:
                    dialog.close()
                    try:
                        await ticket_service.batch_status(ticket_ids, status="CLOSED", note=note_input.value or "Đóng hàng loạt bởi Quản trị viên")
                        state["selected_ids"].clear()
                        toast.success(f"Đã đóng thành công {len(ticket_ids)} sự cố!")
                        await fetch_data(force_refresh=True)
                    except Exception as exc:
                        toast.show_popup("Lỗi đóng ticket", type="error", detail=str(exc))

                with ui.row().classes("w-full justify-end gap-3 mt-5 pt-3 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600").classes("px-4 text-xs font-semibold")
                    ui.button("Xác nhận Đóng", on_click=handle_submit_close).props(
                        "color=negative unelevated"
                    ).classes("px-5 py-2 text-xs font-bold rounded-xl")

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
                    "UNASSIGNED": "👤 Chưa phân công",
                    **{t["id"]: t.get("ho_ten", t.get("username")) for t in technicians},
                }
                tech_filter.options = active_tech_options
                tech_filter.update()

            except Exception as exc:
                state["error"] = str(exc)
                toast.show_popup("Lỗi tải dữ liệu", type="error", detail=str(exc))
            finally:
                state["is_loading"] = False
                render_kpis()
                render_tabs()
                render_batch_bar()
                render_table_view()

        # =========================================================================
        # 6. RENDER KPI STRIP (Larger, High Impact)
        # =========================================================================
        def render_kpis() -> None:
            kpi_container.clear()
            tickets = state["raw_tickets"]
            unassigned_cnt = sum(1 for t in tickets if not t.get("technician_id") and t.get("status") in ("OPEN", "ASSIGNED"))
            critical_cnt = sum(1 for t in tickets if t.get("priority") in ("URGENT", "HIGH") and t.get("status") not in ("RESOLVED", "CLOSED"))
            in_progress_cnt = sum(1 for t in tickets if t.get("status") in ("ASSIGNED", "IN_PROGRESS"))
            total_cnt = len(tickets)
            resolved_cnt = sum(1 for t in tickets if t.get("status") in ("RESOLVED", "CLOSED"))

            with kpi_container:
                # KPI 1: Chờ phân công
                with ui.card().classes(
                    "p-5 rounded-2xl bg-white border border-slate-200/90 shadow-xs hover:shadow-md transition-all cursor-pointer relative overflow-hidden group"
                ).on("click", lambda: set_tab("UNASSIGNED")):
                    ui.element("div").classes("absolute left-0 top-0 bottom-0 w-2 bg-amber-500")
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("Chờ phân công").classes("text-xs font-extrabold text-slate-500 uppercase tracking-wider")
                        with ui.row().classes("items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200"):
                            ui.element("span").classes("w-2 h-2 rounded-full bg-amber-500 animate-ping")
                            ui.label("Cần gán KTV").classes("text-xs font-bold text-amber-800")

                    with ui.row().classes("w-full justify-between items-baseline mt-3"):
                        with ui.row().classes("items-baseline gap-2"):
                            ui.label(str(unassigned_cnt)).classes("text-3xl lg:text-4xl font-black text-slate-900")
                            ui.label("ticket").classes("text-sm font-semibold text-slate-500")
                        ui.html(SPARKLINE_AMBER)

                    with ui.row().classes("w-full justify-between items-center text-xs text-slate-500 mt-2 pt-2 border-t border-slate-100"):
                        ui.label("Thời gian chờ TB: 6.4 phút")
                        ui.label("+3 ticket mới").classes("text-rose-600 font-bold")

                # KPI 2: Khẩn cấp & Cao (P1/P2)
                with ui.card().classes(
                    "p-5 rounded-2xl bg-white border border-slate-200/90 shadow-xs hover:shadow-md transition-all cursor-pointer relative overflow-hidden group"
                ).on("click", lambda: set_tab("CRITICAL")):
                    ui.element("div").classes("absolute left-0 top-0 bottom-0 w-2 bg-rose-500")
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("Khẩn cấp & Cao (P1/P2)").classes("text-xs font-extrabold text-slate-500 uppercase tracking-wider")
                        with ui.row().classes("items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-50 border border-rose-200"):
                            ui.element("span").classes("w-2 h-2 rounded-full bg-rose-600 animate-pulse")
                            ui.label("SLA < 2h").classes("text-xs font-bold text-rose-700")

                    with ui.row().classes("w-full justify-between items-baseline mt-3"):
                        with ui.row().classes("items-baseline gap-2"):
                            ui.label(str(critical_cnt)).classes("text-3xl lg:text-4xl font-black text-rose-600")
                            ui.label("sự cố trọng yếu").classes("text-sm font-semibold text-slate-500")
                        ui.html(SPARKLINE_RED)

                    with ui.row().classes("w-full justify-between items-center text-xs text-slate-500 mt-2 pt-2 border-t border-slate-100"):
                        ui.label("Sự cố chạm ngưỡng SLA")
                        ui.label("Cần escalate").classes("text-rose-600 font-extrabold")

                # KPI 3: Đang điều phối xử lý
                with ui.card().classes(
                    "p-5 rounded-2xl bg-white border border-slate-200/90 shadow-xs hover:shadow-md transition-all cursor-pointer relative overflow-hidden group"
                ).on("click", lambda: set_tab("IN_PROGRESS")):
                    ui.element("div").classes("absolute left-0 top-0 bottom-0 w-2 bg-blue-600")
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("Đang điều phối xử lý").classes("text-xs font-extrabold text-slate-500 uppercase tracking-wider")
                        with ui.row().classes("items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-50 border border-blue-200"):
                            ui.label(f"{len(state['technicians'])} kỹ thuật viên").classes("text-xs font-bold text-blue-700")

                    with ui.row().classes("w-full justify-between items-baseline mt-3"):
                        with ui.row().classes("items-baseline gap-2"):
                            ui.label(str(in_progress_cnt)).classes("text-3xl lg:text-4xl font-black text-blue-600")
                            ui.label("tiến trình").classes("text-sm font-semibold text-slate-500")
                        ui.html(SPARKLINE_BLUE)

                    with ui.row().classes("w-full justify-between items-center text-xs text-slate-500 mt-2 pt-2 border-t border-slate-100"):
                        ui.label("Tải trung bình: 2.3 ticket/KTV")
                        ui.label("Bình thường").classes("text-emerald-600 font-bold")

                # KPI 4: Tổng sự cố
                with ui.card().classes(
                    "p-5 rounded-2xl bg-white border border-slate-200/90 shadow-xs hover:shadow-md transition-all cursor-pointer relative overflow-hidden group"
                ).on("click", lambda: set_tab("ALL")):
                    ui.element("div").classes("absolute left-0 top-0 bottom-0 w-2 bg-emerald-600")
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("Tổng sự cố hôm nay").classes("text-xs font-extrabold text-slate-500 uppercase tracking-wider")
                        with ui.row().classes("items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200"):
                            ui.icon("verified", size="14px").classes("text-emerald-600")
                            ui.label("94% SLA").classes("text-xs font-bold text-emerald-700")

                    with ui.row().classes("w-full justify-between items-baseline mt-3"):
                        with ui.row().classes("items-baseline gap-2"):
                            ui.label(str(total_cnt)).classes("text-3xl lg:text-4xl font-black text-slate-900")
                            ui.label("ticket").classes("text-sm font-semibold text-slate-500")
                        ui.html(SPARKLINE_EMERALD)

                    with ui.row().classes("w-full justify-between items-center text-xs text-slate-500 mt-2 pt-2 border-t border-slate-100"):
                        pct = int((resolved_cnt / total_cnt * 100)) if total_cnt > 0 else 0
                        ui.label(f"Đã xử lý: {resolved_cnt} ({pct}%)")
                        ui.label("Hạn mức: 90%").classes("text-slate-600 font-medium")

        # =========================================================================
        # 7. RENDER SEGMENTED TABS (Unified Status & Priority Switching)
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
                ("ALL", "Tất cả", len(tickets), "bg-slate-100 text-slate-800"),
                ("UNASSIGNED", "Chưa phân công", sum(1 for t in tickets if not t.get("technician_id") and t.get("status") in ("OPEN", "ASSIGNED")), "bg-amber-100 text-amber-800"),
                ("CRITICAL", "Khẩn cấp & Cao", sum(1 for t in tickets if t.get("priority") in ("URGENT", "HIGH") and t.get("status") not in ("RESOLVED", "CLOSED")), "bg-rose-100 text-rose-800"),
                ("IN_PROGRESS", "Đang xử lý", sum(1 for t in tickets if t.get("status") in ("ASSIGNED", "IN_PROGRESS")), "bg-blue-100 text-blue-800"),
                ("RESOLVED", "Đã xử lý / Đóng", sum(1 for t in tickets if t.get("status") in ("RESOLVED", "CLOSED")), "bg-slate-100 text-slate-600"),
            ]

            with tabs_container:
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    for key, label, cnt, badge_cls in tab_defs:
                        is_active = state["active_tab"] == key
                        active_style = "bg-primary text-white shadow-sm font-bold" if is_active else "text-slate-600 hover:bg-slate-100 font-semibold"
                        with ui.button(on_click=lambda k=key: set_tab(k)).props("flat").classes(
                            f"h-10 px-4 rounded-xl text-sm transition-all {active_style}"
                        ):
                            with ui.row().classes("items-center gap-2"):
                                ui.label(label)
                                ui.label(str(cnt)).classes(
                                    f"px-2 py-0.5 rounded-full text-xs font-mono font-bold {('bg-white/30 text-white' if is_active else badge_cls)}"
                                )

                # Live update badge
                with ui.row().classes("items-center gap-2 text-xs text-slate-500 pr-3"):
                    ui.element("span").classes("w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse")
                    ui.label("Dữ liệu trực ban tự động").classes("hidden sm:inline font-semibold text-xs")

        # =========================================================================
        # 8. RENDER BATCH ACTION BAR
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
                    "w-full bg-slate-900 text-white px-5 py-3 rounded-2xl shadow-xl justify-between items-center flex-wrap gap-3 animate-fadeIn"
                ):
                    with ui.row().classes("items-center gap-2.5"):
                        ui.icon("check_circle", size="sm").classes("text-emerald-400")
                        ui.label(f"{len(selected)} sự cố được chọn").classes("text-sm font-bold text-white")

                    with ui.row().classes("items-center gap-3"):
                        ui.button(
                            "Gán nhanh KTV",
                            icon="person_add",
                            on_click=lambda: show_assign_dialog(list(selected), selected_titles),
                        ).props("flat size=sm color=white").classes("h-9 bg-white/20 hover:bg-white/30 text-xs font-bold px-3.5 rounded-xl")

                        ui.button(
                            "Đóng hàng loạt",
                            icon="done_all",
                            on_click=lambda: show_batch_close_dialog(list(selected)),
                        ).props("flat size=sm color=white").classes("h-9 bg-rose-600/90 hover:bg-rose-600 text-xs font-bold px-3.5 rounded-xl")

                        def clear_selection() -> None:
                            state["selected_ids"].clear()
                            render_batch_bar()
                            render_table_view()

                        ui.button(icon="close", on_click=clear_selection).props("flat round dense size=sm color=slate-400")

        # =========================================================================
        # 9. RENDER OPERATIONAL DATA TABLE (Robust Flex-Grid Layout)
        # =========================================================================
        def render_table_view() -> None:
            table_container.clear()

            if state["is_loading"]:
                with table_container:
                    with ui.card().classes("w-full p-8 bg-white rounded-2xl border border-slate-200/90 shadow-xs gap-4"):
                        skeleton_loader(count=6)
                return

            if state["error"]:
                with table_container:
                    with ui.card().classes("w-full p-10 bg-white rounded-2xl border border-rose-200 shadow-xs items-center justify-center text-center"):
                        ui.icon("error_outline", size="lg").classes("text-rose-500 mb-2")
                        ui.label("Không thể nạp danh sách sự cố").classes("text-lg font-bold text-slate-900")
                        ui.label(state["error"]).classes("text-sm text-slate-500 max-w-md")
                        ui.button("Thử lại", icon="refresh", on_click=lambda: fetch_data(force_refresh=True)).props("unelevated color=primary").classes("mt-4 h-10 px-5 rounded-xl")
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
                        title="Không tìm thấy sự cố phù hợp",
                        description="Vui lòng thử điều chỉnh lại bộ lọc hoặc từ khóa tìm kiếm.",
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

            # Build Table Container
            with table_container:
                with ui.card().classes("w-full p-0 bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden"):
                    with ui.column().classes("w-full overflow-x-auto min-w-[1050px] gap-0"):
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

                        with ui.row().classes("w-full bg-slate-100/90 text-slate-700 text-xs font-bold uppercase tracking-wider py-3.5 px-4 items-center border-b border-slate-200"):
                            with ui.row().classes("w-10 justify-center"):
                                ui.checkbox(value=all_page_selected, on_change=toggle_all).props("dense size=sm")

                            ui.label("MÃ & ƯU TIÊN").classes("w-36 font-bold")
                            ui.label("TIÊU ĐỀ SỰ CỐ & CHI TIẾT").classes("flex-1 min-w-[280px] font-bold")
                            ui.label("NGƯỜI YÊU CẦU").classes("w-44 font-bold")
                            ui.label("KTV PHỤ TRÁCH").classes("w-48 font-bold")
                            ui.label("CẬP NHẬT").classes("w-32 font-bold")
                            ui.label("TRẠNG THÁI").classes("w-36 font-bold")
                            ui.label("THAO TÁC").classes("w-20 text-right font-bold")

                        # Table Body Rows
                        with ui.column().classes("w-full divide-y divide-slate-100 gap-0"):
                            for t in page_items:
                                t_id = t.get("id")
                                is_urgent = t.get("priority") == "URGENT"
                                row_bg = "bg-rose-50/30 hover:bg-rose-50/60" if is_urgent else "hover:bg-slate-50/90 bg-white"

                                with ui.row().classes(f"w-full px-4 py-3.5 items-center justify-between transition-colors {row_bg}"):
                                    # 1. Checkbox
                                    with ui.row().classes("w-10 justify-center"):
                                        is_checked = t_id in state["selected_ids"]
                                        def toggle_single(e: Any, tid=t_id) -> None:
                                            if e.value:
                                                state["selected_ids"].add(tid)
                                            else:
                                                state["selected_ids"].discard(tid)
                                            render_batch_bar()

                                        ui.checkbox(value=is_checked, on_change=toggle_single).props("dense size=sm")

                                    # 2. Code & Priority
                                    with ui.column().classes("w-36 gap-1.5 items-start"):
                                        ui.label(f"#TK-{t_id:04d}").classes(
                                            "font-mono font-extrabold text-sm text-slate-900 hover:text-primary cursor-pointer px-2 py-0.5 bg-slate-100 rounded-md border border-slate-200"
                                        ).on("click", lambda tid=t_id: ui.navigate.to(f"/tickets/{tid}"))
                                        priority_badge(t.get("priority"))

                                    # 3. Title & Details
                                    with ui.column().classes("flex-1 min-w-[280px] gap-1 pr-3"):
                                        ui.label(t.get("title", "")).classes(
                                            "font-bold text-slate-900 hover:text-primary cursor-pointer line-clamp-1 text-sm leading-snug"
                                        ).on("click", lambda tid=t_id: ui.navigate.to(f"/tickets/{tid}"))

                                        if t.get("description"):
                                            ui.label(truncate(t["description"], 85)).classes("text-slate-500 line-clamp-1 text-xs")

                                        with ui.row().classes("items-center gap-2 mt-0.5 text-xs text-slate-500"):
                                            category_text = CATEGORY_LABELS.get(t.get("category", ""), t.get("category", ""))
                                            ui.label(f"📂 {category_text}").classes("font-medium")
                                            ui.label("•").classes("text-slate-300")
                                            if is_urgent:
                                                ui.label("⚡ SLA: < 2 giờ").classes("text-rose-600 font-bold")
                                            else:
                                                ui.label("SLA: Tiêu chuẩn").classes("text-slate-400")

                                    # 4. User
                                    with ui.row().classes("w-44 items-center gap-2.5"):
                                        with ui.element("div").classes(
                                            "w-8 h-8 rounded-full bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center shrink-0 border border-slate-300"
                                        ):
                                            ui.label(f"U{t.get('user_id', '?')}")
                                        with ui.column().classes("gap-0 min-w-0"):
                                            ui.label(f"User #{t.get('user_id', '')}").classes("font-bold text-slate-900 truncate text-xs")
                                            ui.label("Người yêu cầu").classes("text-[11px] text-slate-400")

                                    # 5. Technician
                                    with ui.row().classes("w-48 items-center gap-2"):
                                        tech_id = t.get("technician_id")
                                        if tech_id:
                                            tech_match = next((tc for tc in state["technicians"] if tc["id"] == tech_id), None)
                                            tech_name = tech_match.get("ho_ten", tech_match.get("username", f"KTV #{tech_id}")) if tech_match else f"KTV #{tech_id}"
                                            with ui.element("div").classes(
                                                "w-8 h-8 rounded-full bg-blue-100 text-blue-800 font-bold text-xs flex items-center justify-center shrink-0 border border-blue-200"
                                            ):
                                                ui.label("KT")
                                            ui.label(tech_name).classes("font-bold text-slate-900 truncate max-w-[120px] text-xs")
                                        else:
                                            ui.button(
                                                "+ Gán KTV",
                                                icon="person_add",
                                                on_click=lambda tid=t_id, tit=t.get("title", ""): show_assign_dialog([tid], [tit]),
                                            ).props("outline size=sm color=primary").classes(
                                                "h-8 border-dashed text-xs font-bold px-3 py-1 rounded-xl hover:bg-blue-50"
                                            )

                                    # 6. Updated At
                                    with ui.column().classes("w-32 gap-0.5"):
                                        ui.label(format_relative_time(t.get("updated_at") or t.get("created_at"))).classes(
                                            "font-mono text-slate-800 font-semibold text-xs"
                                        )
                                        ui.label("Gửi yêu cầu").classes("text-[11px] text-slate-400")

                                    # 7. Status
                                    with ui.column().classes("w-36 items-start"):
                                        status_badge(t.get("status"))

                                    # 8. Action
                                    with ui.row().classes("w-20 justify-end items-center"):
                                        ui.button(
                                            icon="arrow_forward",
                                            on_click=lambda tid=t_id: ui.navigate.to(f"/tickets/{tid}"),
                                        ).props("flat round color=primary").classes("h-9 w-9 hover:bg-blue-50")

                    # Pagination Footer
                    with ui.row().classes("w-full justify-between items-center p-4 bg-slate-50 border-t border-slate-200 flex-wrap gap-3"):
                        with ui.row().classes("items-center gap-2 text-xs text-slate-600 font-medium"):
                            ui.label(f"Hiển thị {start_idx + 1} - {end_idx} trong số {total_items} sự cố")
                            ui.label("•").classes("text-slate-300")
                            ui.label("Số hàng mỗi trang:")
                            page_size_select = ui.select(
                                [10, 25, 50, 100],
                                value=state["page_size"],
                            ).props("outlined dense options-dense").classes("w-20")

                            def on_page_size_change(e: Any) -> None:
                                state["page_size"] = int(e.value)
                                state["page"] = 1
                                render_table_view()

                            page_size_select.on("update:model-value", on_page_size_change)

                        with ui.row().classes("items-center gap-2"):
                            def prev_page() -> None:
                                if state["page"] > 1:
                                    state["page"] -= 1
                                    render_table_view()

                            def next_page() -> None:
                                if state["page"] < total_pages:
                                    state["page"] += 1
                                    render_table_view()

                            ui.button(icon="chevron_left", on_click=prev_page).props(
                                "flat color=slate-700"
                            ).classes("h-8 w-8 rounded-lg").set_visibility(state["page"] > 1)

                            ui.label(f"Trang {state['page']} / {total_pages}").classes("text-xs font-bold text-slate-800 px-2")

                            ui.button(icon="chevron_right", on_click=next_page).props(
                                "flat color=slate-700"
                            ).classes("h-8 w-8 rounded-lg").set_visibility(state["page"] < total_pages)

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
