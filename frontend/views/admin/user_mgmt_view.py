from __future__ import annotations

import csv
from io import StringIO
from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.status_badge import role_badge, status_badge
from common.formatters import format_datetime
from core.constants import ROLE_LABELS, STATUS_LABELS, Role, UserStatus
from services.user_service import user_service


def render_user_mgmt_view() -> None:
    def content(current_user: dict) -> None:
        if current_user.get("vai_tro") != "ADMIN":
            with ui.card().classes("w-full p-8 text-center bg-white border border-rose-200 rounded-xl mt-4"):
                ui.icon("shield_lock", size="48px").classes("text-rose-500 mb-2")
                ui.label("Quyền truy cập bị từ chối").classes("text-lg font-bold text-slate-800")
                ui.label("Bạn không có quyền quản trị người dùng & phân quyền hệ thống.").classes("text-sm text-slate-500 mt-1")
            return

        # =========================================================================
        # 1. STATE MANAGEMENT
        # =========================================================================
        state: dict[str, Any] = {
            "raw_users": [],
            "selected_ids": set(),
            "active_tab": "ALL",
            "is_loading": True,
            "error": None,
            "page": 1,
            "page_size": 25,
            "role_filter": "ALL",
            "status_filter": "ALL",
            "keyword": "",
        }

        # =========================================================================
        # 2. PAGE HEADER (Enterprise Admin Console)
        # =========================================================================
        with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200 mb-2.5 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 font-medium"):
                    ui.label("Trang chủ")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Quản trị hệ thống")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Người dùng & Phân quyền").classes("text-slate-900 font-semibold")

                ui.label("Quản trị Người dùng & Phân quyền").classes("text-xl font-bold text-slate-900 tracking-tight")
                ui.label("Quản lý danh sách tài khoản, vai trò và trạng thái hoạt động hệ thống.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                async def handle_export_users_csv() -> None:
                    try:
                        ui.notify("Đang xuất danh sách người dùng...", type="info")
                        users = filter_users(state["raw_users"])
                        output = StringIO()
                        output.write("\ufeff")  # UTF-8 BOM
                        writer = csv.writer(output)
                        writer.writerow(["ID", "Tên đăng nhập", "Họ và tên", "Email", "Vai trò", "Trạng thái", "Ngày tạo", "Cập nhật cuối"])
                        for u in users:
                            role_text = ROLE_LABELS.get(u.get("vai_tro"), u.get("vai_tro") or "-")
                            status_text = STATUS_LABELS.get(u.get("trang_thai") or u.get("status"), u.get("trang_thai") or "-")
                            writer.writerow([
                                u.get("id"),
                                u.get("username"),
                                u.get("ho_ten"),
                                u.get("email") or "-",
                                role_text,
                                status_text,
                                str(u.get("created_at") or "-"),
                                str(u.get("updated_at") or "-"),
                            ])
                        ui.download(output.getvalue().encode("utf-8-sig"), filename="danh_sach_nguoi_dung.csv")
                        toast.success("Đã xuất file CSV thành công.")
                    except Exception as exc:
                        toast.error(f"Lỗi xuất file: {exc}")

                ui.button("Xuất CSV", icon="file_download", on_click=handle_export_users_csv).props(
                    "outline color=slate-700 size=md"
                ).classes("h-[36px] rounded-lg font-medium px-3 text-xs bg-white")

                ui.button(
                    "Thêm người dùng",
                    icon="person_add",
                    on_click=lambda: show_user_modal(mode="create"),
                ).props("unelevated color=primary size=md").classes("h-[36px] rounded-lg font-medium shadow-2xs px-3.5 text-xs")

        # Container for Real Data Summary Strip
        summary_container = ui.row().classes("w-full gap-2.5 mb-2.5 flex-wrap")

        # Container for Segmented Quick Tabs
        tabs_container = ui.row().classes("w-full mb-2.5")

        # =========================================================================
        # 3. UNIFIED FILTER TOOLBAR
        # =========================================================================
        with ui.card().classes("w-full p-2.5 rounded-lg bg-white border border-slate-200/90 shadow-2xs mb-2.5"):
            with ui.row().classes("w-full items-center gap-2 flex-wrap"):
                search_input = (
                    ui.input(
                        placeholder="Tìm theo tên, username hoặc email...",
                        on_change=lambda e: on_search_changed(e.value),
                    )
                    .props("outlined dense clearable debounce=300")
                    .classes("flex-1 min-w-[260px] text-xs")
                )
                with search_input.add_slot("prepend"):
                    ui.icon("search", size="16px").classes("text-slate-400")

                role_options = {
                    "ALL": "Tất cả vai trò",
                    Role.ADMIN.value: "Quản trị viên",
                    Role.TECHNICIAN.value: "Kỹ thuật viên",
                    Role.USER.value: "Người dùng",
                }
                role_select = (
                    ui.select(
                        role_options,
                        value="ALL",
                        on_change=lambda e: on_role_changed(e.value),
                    )
                    .props("outlined dense")
                    .classes("w-40 text-xs")
                )

                status_options = {
                    "ALL": "Tất cả trạng thái",
                    UserStatus.ACTIVE.value: "Đang hoạt động",
                    UserStatus.INACTIVE.value: "Đã khóa",
                }
                status_select = (
                    ui.select(
                        status_options,
                        value="ALL",
                        on_change=lambda e: on_status_changed(e.value),
                    )
                    .props("outlined dense")
                    .classes("w-40 text-xs")
                )

                clear_filter_btn = (
                    ui.button("Xóa lọc", icon="close", on_click=lambda: clear_filters())
                    .props("flat dense color=slate-600 size=sm")
                    .classes("h-[38px] px-2.5 rounded-lg text-xs font-medium")
                )
                clear_filter_btn.set_visibility(False)

                ui.button(icon="refresh", on_click=lambda: load_users_data(refresh=True)).props(
                    "outline dense color=slate-700 size=sm"
                ).classes("h-[38px] w-[38px] rounded-lg bg-white").tooltip("Tải lại danh sách")

        # Container for Batch Action Bar (Shown when users are selected)
        batch_bar_container = ui.row().classes("w-full mb-2.5")

        # Container for User List Table & Pagination
        table_container = ui.column().classes("w-full gap-0")

        # =========================================================================
        # 4. DATA LOGIC & FILTERING
        # =========================================================================
        def filter_users(users: list[dict[str, Any]]) -> list[dict[str, Any]]:
            res = users

            # Tab filter
            tab = state["active_tab"]
            if tab == "ADMIN":
                res = [u for u in res if u.get("vai_tro") == "ADMIN"]
            elif tab == "TECHNICIAN":
                res = [u for u in res if u.get("vai_tro") == "TECHNICIAN"]
            elif tab == "USER":
                res = [u for u in res if u.get("vai_tro") == "USER"]
            elif tab == "LOCKED":
                res = [u for u in res if (u.get("trang_thai") or u.get("status")) == "INACTIVE"]

            kw = (state["keyword"] or "").strip().lower()
            if kw:
                res = [
                    u
                    for u in res
                    if kw in str(u.get("username", "")).lower()
                    or kw in str(u.get("ho_ten", "")).lower()
                    or kw in str(u.get("email", "")).lower()
                ]

            if state["role_filter"] != "ALL":
                res = [u for u in res if u.get("vai_tro") == state["role_filter"]]

            if state["status_filter"] != "ALL":
                res = [u for u in res if (u.get("trang_thai") or u.get("status")) == state["status_filter"]]

            return res

        def on_search_changed(val: str | None) -> None:
            state["keyword"] = val or ""
            state["page"] = 1
            update_clear_button_visibility()
            render_all()

        def on_role_changed(val: str) -> None:
            state["role_filter"] = val
            state["page"] = 1
            update_clear_button_visibility()
            render_all()

        def on_status_changed(val: str) -> None:
            state["status_filter"] = val
            state["page"] = 1
            update_clear_button_visibility()
            render_all()

        def set_tab(tab_name: str) -> None:
            state["active_tab"] = tab_name
            state["page"] = 1
            update_clear_button_visibility()
            render_all()

        def clear_filters() -> None:
            search_input.value = ""
            role_select.value = "ALL"
            status_select.value = "ALL"
            state["keyword"] = ""
            state["role_filter"] = "ALL"
            state["status_filter"] = "ALL"
            state["active_tab"] = "ALL"
            state["page"] = 1
            update_clear_button_visibility()
            render_all()

        def update_clear_button_visibility() -> None:
            is_active = bool(
                state["keyword"]
                or state["role_filter"] != "ALL"
                or state["status_filter"] != "ALL"
                or state["active_tab"] != "ALL"
            )
            clear_filter_btn.set_visibility(is_active)

        # =========================================================================
        # 5. RENDER REAL DATA SUMMARY STRIP
        # =========================================================================
        def render_summary_strip() -> None:
            summary_container.clear()
            users = state["raw_users"]
            total_count = len(users)
            admin_count = sum(1 for u in users if u.get("vai_tro") == "ADMIN")
            tech_count = sum(1 for u in users if u.get("vai_tro") == "TECHNICIAN")
            user_count = sum(1 for u in users if u.get("vai_tro") == "USER")
            locked_count = sum(1 for u in users if (u.get("trang_thai") or u.get("status")) == "INACTIVE")

            cards = [
                ("Tổng người dùng", total_count, "group", "slate", "Tất cả tài khoản"),
                ("Quản trị viên", admin_count, "admin_panel_settings", "purple", "Toàn quyền hệ thống"),
                ("Kỹ thuật viên", tech_count, "engineering", "amber", "Xử lý sự cố"),
                ("Người dùng", user_count, "person", "blue", "Nhân viên gửi yêu cầu"),
                ("Tài khoản đã khóa", locked_count, "lock", "rose" if locked_count > 0 else "slate", "Ngừng hoạt động"),
            ]

            with summary_container:
                for label, count, icon_name, color, hint in cards:
                    bg_badge = {
                        "slate": "bg-slate-100 text-slate-700",
                        "purple": "bg-purple-50 text-purple-700",
                        "amber": "bg-amber-50 text-amber-700",
                        "blue": "bg-blue-50 text-blue-700",
                        "rose": "bg-rose-50 text-rose-700",
                    }.get(color, "bg-slate-100 text-slate-700")

                    with ui.card().classes(
                        "flex-1 min-w-[160px] p-2.5 rounded-lg bg-white border border-slate-200/90 shadow-2xs flex flex-col justify-between"
                    ):
                        with ui.row().classes("w-full justify-between items-center no-wrap"):
                            ui.label(label).classes("text-[11px] font-semibold text-slate-500 uppercase tracking-tight")
                            with ui.row().classes(f"w-6 h-6 rounded-md items-center justify-center {bg_badge}"):
                                ui.icon(icon_name, size="14px")

                        with ui.row().classes("items-baseline gap-1.5 mt-1"):
                            ui.label(str(count)).classes("text-xl font-bold text-slate-900 tracking-tight")
                            ui.label(hint).classes("text-[10px] text-slate-400 truncate")

        # =========================================================================
        # 6. RENDER SEGMENTED QUICK TABS
        # =========================================================================
        def render_tabs() -> None:
            tabs_container.clear()
            users = state["raw_users"]
            active_tab = state["active_tab"]

            counts = {
                "ALL": len(users),
                "ADMIN": sum(1 for u in users if u.get("vai_tro") == "ADMIN"),
                "TECHNICIAN": sum(1 for u in users if u.get("vai_tro") == "TECHNICIAN"),
                "USER": sum(1 for u in users if u.get("vai_tro") == "USER"),
                "LOCKED": sum(1 for u in users if (u.get("trang_thai") or u.get("status")) == "INACTIVE"),
            }

            tab_items = [
                ("ALL", "Tất cả", counts["ALL"]),
                ("ADMIN", "Quản trị viên", counts["ADMIN"]),
                ("TECHNICIAN", "Kỹ thuật viên", counts["TECHNICIAN"]),
                ("USER", "Người dùng", counts["USER"]),
                ("LOCKED", "Đã khóa", counts["LOCKED"]),
            ]

            with tabs_container:
                with ui.row().classes(
                    "w-full justify-between items-center bg-white p-1 rounded-lg border border-slate-200/90 shadow-2xs flex-wrap gap-2"
                ):
                    with ui.row().classes("items-center gap-1 flex-wrap"):
                        for key, label, count in tab_items:
                            is_selected = active_tab == key
                            tab_classes = (
                                "bg-slate-900 text-white font-medium shadow-xs"
                                if is_selected
                                else "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                            )
                            pill_classes = (
                                "bg-slate-800 text-slate-100"
                                if is_selected
                                else "bg-slate-100 text-slate-600 font-semibold"
                            )

                            with (
                                ui.button(on_click=lambda k=key: set_tab(k))
                                .props("flat dense")
                                .classes(f"px-3 py-1 rounded-md text-xs transition-all {tab_classes}")
                            ):
                                with ui.row().classes("items-center gap-1.5 no-wrap"):
                                    ui.label(label)
                                    ui.label(str(count)).classes(
                                        f"text-[10px] px-1.5 py-0.2 rounded-full {pill_classes}"
                                    )

                    with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 pr-2 hidden sm:flex"):
                        ui.icon("check_circle", size="14px").classes("text-emerald-600")
                        ui.label(f"Đã tải {len(users)} người dùng").classes("text-[11px] font-medium")

        # =========================================================================
        # 7. RENDER BATCH ACTIONS BAR
        # =========================================================================
        def render_batch_actions() -> None:
            batch_bar_container.clear()
            selected = state["selected_ids"]
            if not selected:
                return

            with batch_bar_container:
                with ui.row().classes(
                    "w-full items-center justify-between bg-slate-900 text-white px-4 py-2 rounded-lg shadow-md transition-all animate-fade-in"
                ):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle", size="18px").classes("text-emerald-400")
                        ui.label(f"{len(selected)} người dùng đã chọn").classes("text-xs font-semibold text-white")

                    with ui.row().classes("items-center gap-2"):
                        async def batch_toggle_lock(lock: bool) -> None:
                            new_status = "INACTIVE" if lock else "ACTIVE"
                            success_count = 0
                            for uid in list(selected):
                                if uid == current_user.get("id"):
                                    continue  # Protect self
                                try:
                                    await user_service.update_user_status(uid, new_status)
                                    success_count += 1
                                except Exception:
                                    pass
                            action_name = "Khóa" if lock else "Kích hoạt"
                            toast.success(f"Đã {action_name.lower()} {success_count} tài khoản.")
                            state["selected_ids"].clear()
                            await load_users_data(refresh=True)

                        ui.button(
                            "Khóa đã chọn",
                            icon="lock",
                            on_click=lambda: batch_toggle_lock(True),
                        ).props("flat dense color=white size=sm").classes("text-xs rounded bg-slate-800 hover:bg-slate-700 px-2.5 py-1")

                        ui.button(
                            "Mở khóa đã chọn",
                            icon="lock_open",
                            on_click=lambda: batch_toggle_lock(False),
                        ).props("flat dense color=white size=sm").classes("text-xs rounded bg-slate-800 hover:bg-slate-700 px-2.5 py-1")

                        def clear_selection() -> None:
                            state["selected_ids"].clear()
                            render_all()

                        ui.button("Bỏ chọn", icon="close", on_click=clear_selection).props("flat dense color=slate-300 size=sm").classes("text-xs")

        # =========================================================================
        # 8. RENDER USER TABLE
        # =========================================================================
        def render_table() -> None:
            table_container.clear()

            if state["is_loading"]:
                with table_container:
                    with ui.card().classes("w-full p-0 rounded-lg bg-white border border-slate-200/90 overflow-hidden shadow-2xs"):
                        with ui.column().classes("w-full divide-y divide-slate-100"):
                            for _ in range(7):
                                with ui.row().classes("w-full p-3 items-center justify-between"):
                                    with ui.row().classes("items-center gap-3"):
                                        ui.skeleton().classes("w-4 h-4 rounded")
                                        ui.skeleton().classes("w-8 h-8 rounded-full")
                                        with ui.column().classes("gap-1"):
                                            ui.skeleton().classes("w-32 h-3.5 rounded")
                                            ui.skeleton().classes("w-44 h-2.5 rounded")
                                    ui.skeleton().classes("w-24 h-5 rounded-full")
                                    ui.skeleton().classes("w-20 h-5 rounded-full")
                                    ui.skeleton().classes("w-28 h-3 rounded")
                                    ui.skeleton().classes("w-16 h-6 rounded")
                return

            if state["error"]:
                with table_container:
                    with ui.card().classes("w-full p-8 text-center bg-white border border-rose-200 rounded-lg shadow-2xs"):
                        ui.icon("error_outline", size="40px").classes("text-rose-500 mb-2")
                        ui.label("Không thể tải danh sách người dùng").classes("text-base font-bold text-slate-900")
                        ui.label("Đã xảy ra lỗi khi kết nối máy chủ dữ liệu.").classes("text-xs text-slate-500 mt-0.5 mb-3")
                        ui.button("Thử lại", icon="refresh", on_click=lambda: load_users_data(refresh=True)).props(
                            "unelevated color=primary size=sm"
                        ).classes("rounded-lg px-4")
                return

            filtered = filter_users(state["raw_users"])

            if not filtered:
                with table_container:
                    with ui.card().classes("w-full p-8 bg-white border border-slate-200/90 rounded-lg shadow-2xs"):
                        if state["keyword"] or state["role_filter"] != "ALL" or state["status_filter"] != "ALL" or state["active_tab"] != "ALL":
                            empty_state(
                                title="Không tìm thấy người dùng phù hợp",
                                subtitle="Không có tài khoản nào khớp với bộ lọc hiện tại. Thử thay đổi từ khóa hoặc bộ lọc.",
                                icon="person_search",
                                action_label="Xóa bộ lọc",
                                on_action=clear_filters,
                            )
                        else:
                            empty_state(
                                title="Chưa có người dùng",
                                subtitle="Hệ thống chưa có tài khoản người dùng nào được tạo.",
                                icon="group",
                                action_label="+ Thêm người dùng",
                                on_action=lambda: show_user_modal(mode="create"),
                            )
                return

            # Pagination slice
            total_items = len(filtered)
            page_size = state["page_size"]
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            if state["page"] > total_pages:
                state["page"] = total_pages

            start_idx = (state["page"] - 1) * page_size
            end_idx = min(start_idx + page_size, total_items)
            paged_users = filtered[start_idx:end_idx]

            all_paged_selected = bool(paged_users) and all(u["id"] in state["selected_ids"] for u in paged_users)

            with table_container:
                with ui.card().classes("w-full p-0 rounded-lg bg-white border border-slate-200/90 shadow-2xs overflow-hidden"):
                    # Table Header
                    with ui.row().classes("w-full px-4 py-2.5 bg-slate-50/90 border-b border-slate-200/80 items-center text-[11px] font-semibold text-slate-600 uppercase tracking-wider no-wrap gap-2"):
                        def toggle_select_all(val: bool) -> None:
                            if val:
                                for u in paged_users:
                                    state["selected_ids"].add(u["id"])
                            else:
                                for u in paged_users:
                                    state["selected_ids"].discard(u["id"])
                            render_all()

                        ui.checkbox(value=all_paged_selected, on_change=lambda e: toggle_select_all(e.value)).props(
                            "dense"
                        ).classes("w-8 shrink-0")

                        ui.label("NGƯỜI DÙNG & TÀI KHOẢN").classes("flex-1 min-w-[220px]")
                        ui.label("VAI TRÒ").classes("w-36 shrink-0")
                        ui.label("TRẠNG THÁI").classes("w-36 shrink-0")
                        ui.label("NGÀY TẠO").classes("w-36 shrink-0")
                        ui.label("THAO TÁC").classes("w-24 shrink-0 text-right")

                    # Table Rows
                    with ui.column().classes("w-full divide-y divide-slate-100 gap-0"):
                        for u in paged_users:
                            render_user_row(u, current_user)

                    # Pagination Footer
                    with ui.row().classes("w-full justify-between items-center px-4 py-2 bg-slate-50/50 border-t border-slate-200/80 text-xs text-slate-600 flex-wrap gap-2"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(f"Hiển thị {start_idx + 1}–{end_idx} trong số {total_items} người dùng").classes("font-medium text-slate-700")

                            def on_page_size_change(val: int) -> None:
                                state["page_size"] = val
                                state["page"] = 1
                                render_all()

                            ui.select(
                                [10, 25, 50, 100],
                                value=state["page_size"],
                                on_change=lambda e: on_page_size_change(e.value),
                            ).props("outlined dense options-dense").classes("w-20 text-xs")

                        with ui.row().classes("items-center gap-1"):
                            def go_prev() -> None:
                                if state["page"] > 1:
                                    state["page"] -= 1
                                    render_all()

                            def go_next() -> None:
                                if state["page"] < total_pages:
                                    state["page"] += 1
                                    render_all()

                            prev_btn = ui.button(icon="chevron_left", on_click=go_prev).props("flat dense size=sm").classes("h-7 w-7 rounded")
                            if state["page"] <= 1:
                                prev_btn.props("disable")

                            ui.label(f"Trang {state['page']} / {total_pages}").classes("px-2 font-medium text-slate-700 text-xs")

                            next_btn = ui.button(icon="chevron_right", on_click=go_next).props("flat dense size=sm").classes("h-7 w-7 rounded")
                            if state["page"] >= total_pages:
                                next_btn.props("disable")

        # =========================================================================
        # 9. RENDER USER ROW
        # =========================================================================
        def render_user_row(u: dict[str, Any], logged_in_admin: dict[str, Any]) -> None:
            user_id = u.get("id")
            username = u.get("username") or ""
            full_name = u.get("ho_ten") or username
            email = u.get("email") or "Chưa cập nhật email"
            role = u.get("vai_tro") or "USER"
            status = u.get("trang_thai") or u.get("status") or "ACTIVE"
            is_active = status == "ACTIVE"
            is_self = logged_in_admin.get("id") == user_id or logged_in_admin.get("username") == username
            is_selected = user_id in state["selected_ids"]

            # Deterministic avatar initials & subtle background
            initials = "".join([part[0] for part in full_name.split() if part][:2]).upper() if full_name else "U"
            if len(initials) < 2 and username:
                initials = username[:2].upper()

            avatar_bg = {
                "ADMIN": "bg-purple-100 text-purple-700 border border-purple-200",
                "TECHNICIAN": "bg-amber-100 text-amber-800 border border-amber-200",
                "USER": "bg-blue-50 text-blue-700 border border-blue-200",
            }.get(role, "bg-slate-100 text-slate-700 border border-slate-200")

            row_bg = "bg-blue-50/20" if is_selected else ("bg-slate-50/40" if not is_active else "")

            with ui.row().classes(
                f"w-full px-4 py-2.5 items-center justify-between hover:bg-slate-50/80 transition-colors duration-150 text-xs no-wrap gap-2 {row_bg}"
            ):
                # 0. Checkbox
                def toggle_select(val: bool) -> None:
                    if val:
                        state["selected_ids"].add(user_id)
                    else:
                        state["selected_ids"].discard(user_id)
                    render_batch_actions()

                ui.checkbox(value=is_selected, on_change=lambda e: toggle_select(e.value)).props("dense").classes("w-8 shrink-0")

                # 1. Identity Cell
                with ui.row().classes("flex-1 min-w-[220px] items-center gap-3 no-wrap cursor-pointer").on(
                    "click", lambda: show_user_detail_drawer(u)
                ):
                    with ui.row().classes(
                        f"w-8 h-8 rounded-full items-center justify-center font-bold text-[11px] shrink-0 {avatar_bg}"
                    ):
                        ui.label(initials)

                    with ui.column().classes("gap-0 min-w-0"):
                        with ui.row().classes("items-center gap-1.5 no-wrap"):
                            ui.label(full_name).classes("font-semibold text-slate-900 text-[13px] truncate hover:text-primary")
                            if is_self:
                                ui.label("(Bạn)").classes("text-[10px] font-semibold text-primary px-1.5 py-0.2 bg-blue-50 rounded")
                        ui.label(f"@{username} · {email}").classes("text-[11px] text-slate-500 truncate")

                # 2. Role Cell
                with ui.row().classes("w-36 shrink-0 items-center no-wrap"):
                    role_badge(role)

                # 3. Status Cell
                with ui.row().classes("w-36 shrink-0 items-center no-wrap"):
                    status_badge(status)

                # 4. Created Date Cell
                with ui.column().classes("w-36 shrink-0 gap-0 text-slate-500 text-[11px]"):
                    ui.label(format_datetime(u.get("created_at"))).classes("truncate")

                # 5. Contextual Action Menu
                with ui.row().classes("w-24 shrink-0 justify-end items-center gap-1"):
                    # Quick detail button
                    ui.button(
                        icon="visibility",
                        on_click=lambda u=u: show_user_detail_drawer(u),
                    ).props("flat dense round size=xs color=slate-600").tooltip("Xem chi tiết")

                    # Context Menu ⋯
                    with ui.button(icon="more_vert").props("flat dense round size=xs color=slate-700"):
                        with ui.menu().classes("rounded-lg shadow-md border border-slate-200 text-xs p-1"):
                            ui.menu_item(
                                "Xem chi tiết",
                                on_click=lambda u=u: show_user_detail_drawer(u),
                            ).classes("rounded text-xs")

                            ui.menu_item(
                                "Chỉnh sửa thông tin",
                                on_click=lambda u=u: show_user_modal(mode="edit", user_data=u),
                            ).classes("rounded text-xs")

                            ui.separator().classes("my-1")

                            if is_self:
                                ui.menu_item("Không thể khóa chính mình").props("disable").classes("text-slate-400 text-xs")
                            else:
                                lock_label = "Khóa tài khoản" if is_active else "Kích hoạt tài khoản"
                                text_color = "text-rose-600" if is_active else "text-emerald-600"

                                ui.menu_item(
                                    lock_label,
                                    on_click=lambda u=u: show_toggle_status_dialog(u),
                                ).classes(f"rounded text-xs font-semibold {text_color}")

        # =========================================================================
        # 10. USER DETAIL DRAWER / DIALOG
        # =========================================================================
        def show_user_detail_drawer(u: dict[str, Any]) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-xl p-0 bg-white border border-slate-200 shadow-xl overflow-hidden"):
                # Header
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("account_circle", size="20px").classes("text-slate-700")
                        ui.label("Hồ sơ tài khoản").classes("text-sm font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                # Body
                with ui.column().classes("w-full p-5 gap-4"):
                    # Identity Banner
                    with ui.row().classes("items-center gap-3 w-full pb-3 border-b border-slate-100"):
                        full_name = u.get("ho_ten") or u.get("username") or "U"
                        initials = "".join([part[0] for part in full_name.split() if part][:2]).upper()
                        role = u.get("vai_tro") or "USER"

                        with ui.avatar(color="primary" if role != "ADMIN" else "purple", text_color="white").props(
                            "size=44px font-size=16px"
                        ).classes("font-bold shadow-2xs"):
                            ui.label(initials)

                        with ui.column().classes("gap-0.5 flex-1"):
                            ui.label(full_name).classes("text-base font-bold text-slate-900")
                            ui.label(f"@{u.get('username')}").classes("text-xs font-mono text-slate-500")

                    # Metadata List
                    with ui.column().classes("w-full gap-2.5 text-xs"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Vai trò hệ thống:").classes("text-slate-500 font-medium")
                            role_badge(u.get("vai_tro"))

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Trạng thái hoạt động:").classes("text-slate-500 font-medium")
                            status_badge(u.get("trang_thai") or u.get("status"))

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Email:").classes("text-slate-500 font-medium")
                            ui.label(u.get("email") or "Chưa cập nhật").classes("text-slate-800 font-medium")

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("ID tài khoản:").classes("text-slate-500 font-medium")
                            ui.label(f"#{u.get('id')}").classes("font-mono text-slate-600")

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Thời gian tạo:").classes("text-slate-500 font-medium")
                            ui.label(format_datetime(u.get("created_at"))).classes("text-slate-700")

                        if u.get("updated_at"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("Cập nhật cuối:").classes("text-slate-500 font-medium")
                                ui.label(format_datetime(u.get("updated_at"))).classes("text-slate-700")

                # Footer Actions
                with ui.row().classes("w-full justify-end items-center gap-2 p-4 bg-slate-50 border-t border-slate-200"):
                    is_self = current_user.get("id") == u.get("id") or current_user.get("username") == u.get("username")
                    is_active = (u.get("trang_thai") or u.get("status")) == "ACTIVE"

                    if not is_self:
                        ui.button(
                            "Khóa tài khoản" if is_active else "Kích hoạt",
                            icon="lock" if is_active else "lock_open",
                            on_click=lambda: (dialog.close(), show_toggle_status_dialog(u)),
                        ).props(f"flat dense size=sm color={'negative' if is_active else 'positive'}").classes("rounded-lg px-2.5")

                    ui.button(
                        "Chỉnh sửa",
                        icon="edit",
                        on_click=lambda: (dialog.close(), show_user_modal(mode="edit", user_data=u)),
                    ).props("unelevated color=primary size=sm").classes("rounded-lg px-3")

            dialog.open()

        # =========================================================================
        # 11. CREATE / EDIT USER MODAL
        # =========================================================================
        def show_user_modal(mode: str = "create", user_data: dict[str, Any] | None = None) -> None:
            is_edit = mode == "edit" and user_data is not None
            dialog = ui.dialog()

            with dialog, ui.card().classes("w-full max-w-md rounded-xl p-0 bg-white border border-slate-200 shadow-xl overflow-hidden"):
                # Header
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("edit" if is_edit else "person_add", size="18px").classes("text-slate-700")
                        ui.label("Chỉnh sửa tài khoản" if is_edit else "Thêm người dùng mới").classes("text-sm font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                # Form Fields
                with ui.column().classes("w-full p-5 gap-3.5 text-xs"):
                    if not is_edit:
                        with ui.column().classes("w-full gap-1"):
                            ui.label("Tên đăng nhập *").classes("font-semibold text-slate-700")
                            username_input = ui.input(placeholder="Ví dụ: nguyenvana").props("outlined dense").classes("w-full")

                        with ui.column().classes("w-full gap-1"):
                            ui.label("Mật khẩu ban đầu *").classes("font-semibold text-slate-700")
                            password_input = ui.input(placeholder="Tối thiểu 8 ký tự", password=True).props("outlined dense").classes("w-full")

                    with ui.column().classes("w-full gap-1"):
                        ui.label("Họ và tên *").classes("font-semibold text-slate-700")
                        name_val = user_data.get("ho_ten", "") if is_edit else ""
                        full_name_input = ui.input(value=name_val, placeholder="Ví dụ: Nguyễn Văn A").props("outlined dense").classes("w-full")

                    with ui.column().classes("w-full gap-1"):
                        ui.label("Email liên hệ").classes("font-semibold text-slate-700")
                        email_val = user_data.get("email", "") or "" if is_edit else ""
                        email_input = ui.input(value=email_val, placeholder="Ví dụ: a.nguyen@cs466.local").props("outlined dense").classes("w-full")

                    with ui.column().classes("w-full gap-1"):
                        ui.label("Vai trò hệ thống *").classes("font-semibold text-slate-700")
                        role_options = {
                            Role.USER.value: "Người dùng (Gửi yêu cầu hỗ trợ)",
                            Role.TECHNICIAN.value: "Kỹ thuật viên (Tiếp nhận & xử lý sự cố)",
                            Role.ADMIN.value: "Quản trị viên (Toàn quyền hệ thống)",
                        }
                        current_role = user_data.get("vai_tro", "USER") if is_edit else "USER"
                        role_select_input = ui.select(role_options, value=current_role).props("outlined dense").classes("w-full")

                # Footer Buttons
                with ui.row().classes("w-full justify-end items-center gap-2 p-4 bg-slate-50 border-t border-slate-200"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded-lg px-3")

                    submit_btn = ui.button(
                        "Lưu thay đổi" if is_edit else "Tạo người dùng",
                    ).props("unelevated color=primary size=sm").classes("rounded-lg px-4 font-medium")

                    async def on_submit() -> None:
                        name = (full_name_input.value or "").strip()
                        email = (email_input.value or "").strip() or None
                        selected_role = role_select_input.value

                        if not name:
                            toast.warning("Vui lòng nhập Họ và tên.")
                            return

                        if email and ("@" not in email or email.startswith("@") or email.endswith("@")):
                            toast.warning("Địa chỉ Email không hợp lệ.")
                            return

                        submit_btn.props("loading")

                        try:
                            if is_edit:
                                user_id = user_data["id"]
                                await user_service.update_user(
                                    user_id,
                                    {
                                        "ho_ten": name,
                                        "email": email,
                                        "vai_tro": selected_role,
                                    },
                                )
                                toast.success("Đã cập nhật thông tin người dùng.")
                            else:
                                uname = (username_input.value or "").strip()
                                pwd = (password_input.value or "").strip()

                                if not uname:
                                    toast.warning("Vui lòng nhập Tên đăng nhập.")
                                    submit_btn.props(remove="loading")
                                    return
                                if not pwd or len(pwd) < 8:
                                    toast.warning("Mật khẩu phải có tối thiểu 8 ký tự.")
                                    submit_btn.props(remove="loading")
                                    return

                                await user_service.create_user(
                                    {
                                        "username": uname,
                                        "password": pwd,
                                        "ho_ten": name,
                                        "email": email,
                                        "vai_tro": selected_role,
                                    }
                                )
                                toast.success("Đã tạo người dùng mới thành công.")

                            dialog.close()
                            await load_users_data(refresh=True)
                        except Exception as exc:
                            toast.error(f"Lỗi: {exc}")
                        finally:
                            submit_btn.props(remove="loading")

                    submit_btn.on("click", on_submit)

            dialog.open()

        # =========================================================================
        # 12. LOCK / UNLOCK USER DIALOG
        # =========================================================================
        def show_toggle_status_dialog(u: dict[str, Any]) -> None:
            user_id = u["id"]
            username = u.get("username", "")
            full_name = u.get("ho_ten") or username
            current_s = u.get("trang_thai") or u.get("status") or "ACTIVE"
            new_s = "INACTIVE" if current_s == "ACTIVE" else "ACTIVE"
            is_locking = new_s == "INACTIVE"

            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-sm rounded-xl p-5 bg-white border border-slate-200 shadow-xl"):
                with ui.row().classes("items-center gap-2 mb-2"):
                    ui.icon("warning" if is_locking else "check_circle", size="22px").classes(
                        "text-rose-600" if is_locking else "text-emerald-600"
                    )
                    ui.label(f"{'Khóa' if is_locking else 'Kích hoạt'} tài khoản?").classes("text-base font-bold text-slate-900")

                msg = (
                    f"Người dùng “{full_name}” (@{username}) sẽ bị vô hiệu hóa quyền truy cập hệ thống cho đến khi được mở khóa lại."
                    if is_locking
                    else f"Khôi phục quyền truy cập hệ thống cho người dùng “{full_name}” (@{username})."
                )
                ui.label(msg).classes("text-xs text-slate-600 mb-4 leading-relaxed")

                async def do_toggle() -> None:
                    try:
                        await user_service.update_user_status(user_id, new_s)
                        action_text = "đã khóa" if is_locking else "đã kích hoạt lại"
                        toast.success(f"Tài khoản @{username} {action_text} thành công.")
                        dialog.close()
                        await load_users_data(refresh=True)
                    except Exception as exc:
                        toast.error(f"Lỗi: {exc}")

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded-lg")
                    ui.button(
                        "Khóa tài khoản" if is_locking else "Kích hoạt",
                        on_click=do_toggle,
                    ).props(f"unelevated color={'negative' if is_locking else 'positive'} size=sm").classes("rounded-lg font-medium")

            dialog.open()

        # =========================================================================
        # 13. DATA LOADER
        # =========================================================================
        def render_all() -> None:
            render_summary_strip()
            render_tabs()
            render_batch_actions()
            render_table()

        async def load_users_data(refresh: bool = False) -> None:
            state["is_loading"] = True
            state["error"] = None
            render_table()

            try:
                users = await user_service.list_users(refresh=refresh)
                state["raw_users"] = users
                state["is_loading"] = False
            except Exception as exc:
                state["error"] = str(exc)
                state["is_loading"] = False

            render_all()

        ui.timer(0.05, lambda: load_users_data(refresh=True), once=True)

    app_shell("Người dùng", content)
