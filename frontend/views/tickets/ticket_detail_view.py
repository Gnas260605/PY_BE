from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
# pyrefly: ignore [missing-import]
from nicegui import ui

from common.components import toast
from common.components.comments_thread import comments_thread
from common.components.layout import app_shell
from common.components.status_badge import priority_badge, status_badge
from common.components.timeline import audit_timeline
from common.formatters import format_datetime, format_relative_time
from core.i18n import (
    get_category_label,
    get_priority_label,
    get_status_label,
    get_ticket_desc,
    get_ticket_title,
    t,
)
from services.ticket_service import ticket_service
from services.user_service import user_service


# SLA Thresholds in hours according to priority
SLA_HOURS = {
    "URGENT": 4,
    "HIGH": 8,
    "MEDIUM": 24,
    "LOW": 48,
}


def compute_sla_info(created_at_val: Any, priority: str, cur_status: str) -> dict[str, str]:
    if cur_status in ("RESOLVED", "CLOSED") or not created_at_val:
        return {"text": "Đã hoàn thành", "badge_cls": "bg-slate-100 text-slate-600 border-slate-200", "icon": "check_circle"}

    try:
        if isinstance(created_at_val, str):
            clean_str = created_at_val.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
        elif isinstance(created_at_val, datetime):
            dt = created_at_val
        else:
            return {"text": "SLA Tiêu chuẩn", "badge_cls": "bg-slate-100 text-slate-600 border-slate-200", "icon": "schedule"}

        if dt.tzinfo is None:
            # Assume local/naive
            now = datetime.now()
        else:
            now = datetime.now(timezone.utc)

        allowed_hours = SLA_HOURS.get(priority.upper(), 24)
        elapsed_seconds = (now - dt).total_seconds()
        remaining_seconds = (allowed_hours * 3600) - elapsed_seconds

        if remaining_seconds < 0:
            overdue_mins = int(abs(remaining_seconds) // 60)
            if overdue_mins >= 60:
                hours = overdue_mins // 60
                mins = overdue_mins % 60
                text = f"Quá hạn SLA {hours}h{mins}m"
            else:
                text = f"Quá hạn SLA {overdue_mins}m"
            return {"text": text, "badge_cls": "bg-rose-50 text-rose-700 border-rose-300 font-bold", "icon": "warning"}

        rem_mins = int(remaining_seconds // 60)
        if rem_mins < 60:
            return {"text": f"SLA còn {rem_mins} phút", "badge_cls": "bg-amber-50 text-amber-800 border-amber-300 font-bold", "icon": "alarm"}
        
        hours = rem_mins // 60
        mins = rem_mins % 60
        return {"text": f"SLA còn {hours}h{mins}m", "badge_cls": "bg-blue-50 text-blue-700 border-blue-200 font-medium", "icon": "schedule"}
    except Exception:
        return {"text": "SLA Tiêu chuẩn", "badge_cls": "bg-slate-100 text-slate-600 border-slate-200", "icon": "schedule"}


def render_ticket_detail_view(ticket_id: int) -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")
        role = user.get("vai_tro", "USER")
        can_assign = role == "ADMIN"
        is_technician = role == "TECHNICIAN"

        # Active Tab state: 'OVERVIEW' | 'ACTIVITY' | 'ATTACHMENTS'
        view_state: dict[str, Any] = {
            "active_tab": "OVERVIEW",
        }

        # Main Workspace Container
        main_container = ui.column().classes("w-full max-w-7xl mx-auto gap-5 pb-16")

        async def load_detail() -> None:
            try:
                ticket = await ticket_service.get_ticket(ticket_id)
                if not ticket:
                    raise Exception(f"Không tìm thấy dữ liệu Ticket #{ticket_id}")
                history = await ticket_service.get_history(ticket_id)
                attachments = await ticket_service.list_attachments(ticket_id)
            except Exception as exc:
                main_container.clear()
                with main_container:
                    with ui.card().classes("w-full max-w-lg mx-auto p-8 rounded-2xl bg-white border border-red-200 shadow-lg gap-4 items-center text-center mt-10"):
                        ui.icon("error_outline", size="48px").classes("text-red-500")
                        ui.label(f"Không thể mở phiếu sự cố #{ticket_id}").classes("text-xl font-bold text-slate-900")
                        ui.label(f"Chi tiết lỗi: {exc}").classes("text-xs text-slate-600 font-mono bg-slate-50 p-3 rounded-xl border border-slate-200 w-full whitespace-pre-wrap")
                        with ui.row().classes("gap-3 mt-3"):
                            ui.button("Quay lại danh sách", icon="arrow_back", on_click=lambda: ui.navigate.to("/dashboard")).props("outline color=slate-700")
                            ui.button("Thử lại", icon="refresh", on_click=lambda: load_detail()).props("unelevated color=primary")
                return

            cur_status = ticket.get("status", "OPEN")
            priority = ticket.get("priority", "MEDIUM")
            category = ticket.get("category", "INCIDENT")
            category_label = get_category_label(category)
            ticket_title = get_ticket_title(ticket.get("title"))
            ticket_desc = get_ticket_desc(ticket.get("description"))
            created_at = ticket.get("created_at")
            updated_at = ticket.get("updated_at")
            resolved_at = ticket.get("resolved_at")
            closed_at = ticket.get("closed_at")

            creator_info = ticket.get("creator") or ticket.get("user") or {}
            tech_info = ticket.get("technician") or {}
            device_info = ticket.get("device") or {}

            assigned_tech_id = ticket.get("technician_id")
            sla_data = compute_sla_info(created_at, priority, cur_status)

            main_container.clear()
            with main_container:
                # =============================================================
                # 1. TICKET HEADER (Comprehensive Enterprise Overview)
                # =============================================================
                with ui.card().classes("w-full p-5 sm:p-6 rounded-2xl bg-white border border-slate-200 shadow-sm gap-4"):
                    # Row 1: Back Button, Title, Badges
                    with ui.row().classes("w-full justify-between items-start flex-wrap gap-3"):
                        with ui.row().classes("items-center gap-3 flex-1 min-w-[280px]"):
                            ui.button(icon="arrow_back", on_click=lambda: ui.navigate.back()).props("flat round dense size=md color=slate-700").classes("hover:bg-slate-100")
                            with ui.column().classes("gap-0.5"):
                                with ui.row().classes("items-center gap-2 flex-wrap"):
                                    ui.label(f"Ticket #{ticket_id}").classes("text-sm font-extrabold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-lg border border-blue-200 font-mono")
                                    ui.label(category_label).classes("text-xs font-bold text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-lg border border-slate-200 uppercase")
                                    ui.label(f"Tạo lúc: {format_datetime(created_at)}").classes("text-xs text-slate-400 font-medium")

                                ui.label(ticket_title).classes("text-xl sm:text-2xl font-black text-slate-900 tracking-tight leading-snug")

                        # Badges & Quick Action
                        with ui.row().classes("items-center gap-2.5 flex-wrap"):
                            status_badge(cur_status)
                            priority_badge(priority)
                            with ui.row().classes(f"items-center gap-1.5 px-3 py-1 rounded-full border text-xs {sla_data['badge_cls']}"):
                                ui.icon(sla_data["icon"], size="16px")
                                ui.label(sla_data["text"])
                            ui.button(icon="refresh", on_click=load_detail).props("flat round dense size=sm color=slate-600").tooltip("Làm mới thông tin")

                    # Row 2: Metadata Strip
                    with ui.row().classes("w-full items-center justify-between pt-3 border-t border-slate-100 flex-wrap gap-4 text-xs sm:text-sm text-slate-600"):
                        with ui.row().classes("items-center gap-6 flex-wrap"):
                            # Creator
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("person", size="18px").classes("text-slate-400")
                                ui.label("Người yêu cầu:").classes("text-slate-500 font-medium")
                                ui.label(creator_info.get("ho_ten") or f"User #{ticket.get('user_id')}").classes("font-bold text-slate-800")

                            # Assignee
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("support_agent", size="18px").classes("text-slate-400")
                                ui.label("Kỹ thuật viên:").classes("text-slate-500 font-medium")
                                if tech_info.get("ho_ten"):
                                    ui.label(tech_info["ho_ten"]).classes("font-bold text-blue-700")
                                else:
                                    ui.label("Chưa phân công").classes("font-semibold text-amber-700 italic")

                            # Device
                            if device_info.get("ten_thiet_bi") or device_info.get("ma_thiet_bi"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("devices", size="18px").classes("text-slate-400")
                                    ui.label("Thiết bị:").classes("text-slate-500 font-medium")
                                    ui.label(f"{device_info.get('ma_thiet_bi', '')} · {device_info.get('ten_thiet_bi', '')}").classes("font-bold text-slate-800")

                # =============================================================
                # 2. MAIN 2-COLUMN WORKSPACE
                # =============================================================
                with ui.row().classes("w-full gap-6 items-start flex-col lg:flex-row"):
                    # ---------------------------------------------------------
                    # LEFT COLUMN (Main Content Tabs ~65%)
                    # ---------------------------------------------------------
                    with ui.column().classes("w-full lg:flex-[3] gap-5"):
                        # Tabs Navigation Bar
                        left_tabs_row = ui.row().classes("w-full border-b border-slate-200 gap-2 overflow-x-auto no-wrap")

                        MAIN_TABS = [
                            ("OVERVIEW", "Tổng quan", "dashboard", None),
                            ("ACTIVITY", "Hoạt động & Lịch sử", "history", len(history)),
                            ("ATTACHMENTS", "Tệp đính kèm", "attach_file", len(attachments)),
                        ]

                        def render_left_tabs():
                            left_tabs_row.clear()
                            with left_tabs_row:
                                for tab_key, tab_name, icon_name, count_val in MAIN_TABS:
                                    is_sel = view_state["active_tab"] == tab_key
                                    active_cls = (
                                        "border-b-2 border-blue-600 text-blue-600 font-bold bg-blue-50/50"
                                        if is_sel
                                        else "text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-semibold border-b-2 border-transparent"
                                    )

                                    def make_tab_handler(k=tab_key):
                                        return lambda: select_tab(k)

                                    with ui.button(on_click=make_tab_handler()).props("flat dense").classes(
                                        f"px-5 py-3 text-sm rounded-t-xl transition-all {active_cls}"
                                    ):
                                        with ui.row().classes("items-center gap-2 no-wrap"):
                                            ui.icon(icon_name, size="18px").classes("text-inherit")
                                            ui.label(tab_name)
                                            if count_val is not None:
                                                ui.label(str(count_val)).classes(
                                                    f"text-xs px-2 py-0.2 rounded-full font-bold { 'bg-blue-100 text-blue-700' if is_sel else 'bg-slate-100 text-slate-600' }"
                                                )

                        def select_tab(k: str):
                            view_state["active_tab"] = k
                            render_left_tabs()
                            render_left_content()

                        render_left_tabs()

                        left_content_pane = ui.column().classes("w-full gap-5")

                        # TAB 1: TỔNG QUAN
                        def render_overview():
                            with left_content_pane:
                                # Mô tả sự cố
                                with ui.card().classes("w-full p-6 sm:p-7 rounded-2xl bg-white border border-slate-200 shadow-sm gap-4"):
                                    with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                                        ui.icon("description", size="20px").classes("text-slate-600")
                                        ui.label("Mô tả chi tiết sự cố").classes("text-base font-bold text-slate-900")

                                    with ui.element("div").classes(
                                        "w-full p-5 bg-slate-50/80 rounded-xl border border-slate-200 text-sm text-slate-800 font-normal leading-relaxed whitespace-pre-wrap break-words"
                                    ):
                                        ui.label(ticket_desc)

                                # Bảng thông tin chi tiết (2-Column Metadata List)
                                with ui.card().classes("w-full p-6 sm:p-7 rounded-2xl bg-white border border-slate-200 shadow-sm gap-4"):
                                    with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                                        ui.icon("info", size="20px").classes("text-slate-600")
                                        ui.label("Thông tin thuộc tính phiếu").classes("text-base font-bold text-slate-900")

                                    with ui.element("div").classes("w-full grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm"):
                                        # Người yêu cầu
                                        with ui.column().classes("p-3.5 rounded-xl bg-slate-50 border border-slate-100 gap-1"):
                                            ui.label("Người yêu cầu").classes("text-xs font-bold text-slate-400 uppercase tracking-wider")
                                            ui.label(creator_info.get("ho_ten") or f"User #{ticket.get('user_id')}").classes("font-bold text-slate-900")
                                            ui.label(f"Email: {creator_info.get('email') or 'Chưa cập nhật'}").classes("text-xs text-slate-500")

                                        # Kỹ thuật viên
                                        with ui.column().classes("p-3.5 rounded-xl bg-slate-50 border border-slate-100 gap-1"):
                                            ui.label("Kỹ thuật viên phụ trách").classes("text-xs font-bold text-slate-400 uppercase tracking-wider")
                                            if tech_info.get("ho_ten"):
                                                ui.label(tech_info["ho_ten"]).classes("font-bold text-blue-700")
                                                ui.label(f"Email: {tech_info.get('email') or 'N/A'}").classes("text-xs text-slate-500")
                                            else:
                                                ui.label("Chưa phân công").classes("font-bold text-amber-700 italic")
                                                ui.label("Chờ phân bổ KTV").classes("text-xs text-amber-600")

                                        # Loại & Mức ưu tiên
                                        with ui.column().classes("p-3.5 rounded-xl bg-slate-50 border border-slate-100 gap-1"):
                                            ui.label("Phân loại & Mức độ").classes("text-xs font-bold text-slate-400 uppercase tracking-wider")
                                            with ui.row().classes("items-center gap-2 mt-0.5"):
                                                ui.label(category_label).classes("font-bold text-slate-800")
                                                ui.label("•").classes("text-slate-400")
                                                ui.label(get_priority_label(priority)).classes("font-bold text-slate-800")

                                        # Thời gian xử lý
                                        with ui.column().classes("p-3.5 rounded-xl bg-slate-50 border border-slate-100 gap-1"):
                                            ui.label("Thời gian & Tiến độ").classes("text-xs font-bold text-slate-400 uppercase tracking-wider")
                                            ui.label(f"Tạo: {format_datetime(created_at)}").classes("text-xs text-slate-700 font-mono")
                                            if resolved_at:
                                                ui.label(f"Đã giải quyết: {format_datetime(resolved_at)}").classes("text-xs text-emerald-700 font-mono")
                                            elif closed_at:
                                                ui.label(f"Đã đóng: {format_datetime(closed_at)}").classes("text-xs text-slate-500 font-mono")
                                            else:
                                                ui.label(f"Cập nhật: {format_datetime(updated_at)}").classes("text-xs text-slate-500 font-mono")

                                # Thông tin thiết bị liên quan (nếu có)
                                with ui.card().classes("w-full p-6 sm:p-7 rounded-2xl bg-white border border-slate-200 shadow-sm gap-4"):
                                    with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                                        ui.icon("computer", size="20px").classes("text-slate-600")
                                        ui.label("Thiết bị CNTT liên quan").classes("text-base font-bold text-slate-900")

                                    if device_info.get("ten_thiet_bi") or device_info.get("ma_thiet_bi"):
                                        with ui.row().classes("w-full justify-between items-center p-4 rounded-xl bg-slate-50 border border-slate-200 flex-wrap gap-3"):
                                            with ui.row().classes("items-center gap-4"):
                                                with ui.element("div").classes("w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold"):
                                                    ui.icon("devices", size="24px")
                                                with ui.column().classes("gap-0.5"):
                                                    with ui.row().classes("items-center gap-2"):
                                                        ui.label(device_info.get("ma_thiet_bi", "DEV-UNKNOWN")).classes("text-sm font-extrabold text-blue-800 font-mono")
                                                        ui.label(device_info.get("loai_thiet_bi", "Thiết bị")).classes("text-xs px-2 py-0.2 rounded bg-slate-200 text-slate-700")
                                                    ui.label(device_info.get("ten_thiet_bi", "")).classes("text-base font-bold text-slate-900")
                                                    ui.label(f"Vị trí lắp đặt: {device_info.get('vi_tri') or 'Chưa xác định'}").classes("text-xs text-slate-600")

                                            ui.label(device_info.get("trang_thai", "ACTIVE")).classes("text-xs font-bold px-3 py-1 rounded-full bg-emerald-100 text-emerald-800")
                                    else:
                                        with ui.row().classes("w-full py-6 items-center justify-center text-center gap-2 text-slate-400"):
                                            ui.icon("device_unknown", size="28px")
                                            ui.label("Phiếu sự cố này không gắn kèm mã thiết bị cụ thể.").classes("text-sm font-medium")

                        # TAB 2: HOẠT ĐỘNG (TIMELINE)
                        def render_activity():
                            with left_content_pane:
                                with ui.card().classes("w-full p-6 sm:p-7 rounded-2xl bg-white border border-slate-200 shadow-sm gap-5"):
                                    with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-100"):
                                        with ui.row().classes("items-center gap-2"):
                                            ui.icon("history", size="20px").classes("text-blue-600")
                                            ui.label("Nhật ký hoạt động & Thay đổi").classes("text-base font-bold text-slate-900")
                                        ui.label(f"{len(history)} sự kiện ghi nhận").classes("text-xs text-slate-500 font-semibold")

                                    audit_timeline(history)

                        # TAB 3: TỆP ĐÍNH KÈM (ATTACHMENTS)
                        def render_attachments():
                            with left_content_pane:
                                with ui.card().classes("w-full p-6 sm:p-7 rounded-2xl bg-white border border-slate-200 shadow-sm gap-6"):
                                    with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-100"):
                                        with ui.row().classes("items-center gap-2"):
                                            ui.icon("attach_file", size="20px").classes("text-blue-600")
                                            ui.label("Tệp đính kèm sự cố").classes("text-base font-bold text-slate-900")
                                        ui.label(f"Đã lưu: {len(attachments)} tệp").classes("text-xs text-slate-500 font-semibold")

                                    # Upload Box
                                    async def handle_upload(e: Any) -> None:
                                        try:
                                            content_bytes = e.content.read()
                                            if len(content_bytes) > 10 * 1024 * 1024:
                                                toast.warning("Dung lượng tệp vượt quá giới hạn (tối đa 10MB).")
                                                return
                                            toast.info(f"Đang tải lên tệp: {e.name}...")
                                            await ticket_service.upload_attachment(ticket_id, e.name, content_bytes, e.type)
                                            toast.success(f"Đã tải lên tệp '{e.name}' thành công!")
                                            await load_detail()
                                        except Exception as exc:
                                            toast.error(f"Lỗi tải lên tệp: {exc}")

                                    with ui.column().classes("w-full p-4 rounded-xl bg-slate-50 border border-dashed border-slate-300 gap-2 items-center text-center"):
                                        ui.icon("cloud_upload", size="36px").classes("text-blue-600")
                                        ui.label("Kéo thả tệp vào đây hoặc chọn tải lên từ máy tính").classes("text-sm font-bold text-slate-800")
                                        ui.label("Hỗ trợ JPG, PNG, PDF, DOCX, ZIP · Dung lượng tối đa 10MB / tệp").classes("text-xs text-slate-500 mb-1")
                                        ui.upload(
                                            on_upload=handle_upload,
                                            auto_upload=True,
                                            max_file_size=10 * 1024 * 1024,
                                        ).classes("w-full max-w-sm").props("flat bordered size=sm max-files=1")

                                    # List of existing attachments
                                    if attachments:
                                        with ui.column().classes("w-full gap-3 pt-2"):
                                            ui.label("Danh sách tệp hiện có:").classes("text-xs font-bold text-slate-500 uppercase tracking-wider")
                                            with ui.element("div").classes("w-full grid grid-cols-1 sm:grid-cols-2 gap-3"):
                                                for att in attachments:
                                                    att_id = att["id"]
                                                    att_name = att["file_name"]
                                                    is_image = att.get("file_type", "").startswith("image/")
                                                    upload_time = format_datetime(att.get("created_at"))

                                                    async def do_download(a_id: int = att_id, a_name: str = att_name) -> None:
                                                        try:
                                                            data = await ticket_service.download_attachment(ticket_id, a_id)
                                                            ui.download(data, a_name)
                                                            toast.success(f"Đã tải xuống '{a_name}'")
                                                        except Exception as exc:
                                                            toast.error(f"Lỗi tải tệp: {exc}")

                                                    with ui.card().classes("p-4 rounded-xl bg-slate-50/90 border border-slate-200 shadow-none hover:border-blue-300 transition-all gap-2.5"):
                                                        with ui.row().classes("w-full justify-between items-start no-wrap gap-2"):
                                                            with ui.row().classes("items-center gap-3 flex-1 min-w-0"):
                                                                with ui.element("div").classes(
                                                                    f"w-10 h-10 rounded-lg flex items-center justify-center shrink-0 { 'bg-blue-100 text-blue-700' if is_image else 'bg-slate-200 text-slate-700' }"
                                                                ):
                                                                    ui.icon("image" if is_image else "insert_drive_file", size="20px")
                                                                with ui.column().classes("gap-0.5 flex-1 min-w-0"):
                                                                    ui.label(att_name).classes("text-sm font-bold text-slate-900 truncate w-full").tooltip(att_name)
                                                                    ui.label(upload_time).classes("text-xs text-slate-400 font-mono")

                                                            ui.button(icon="download", on_click=lambda a_id=att_id, a_name=att_name: do_download(a_id, a_name)).props("flat round dense size=sm color=primary").tooltip("Tải tệp xuống")
                                    else:
                                        with ui.row().classes("w-full py-6 items-center justify-center text-center gap-2 text-slate-400"):
                                            ui.icon("folder_open", size="24px")
                                            ui.label("Chưa có tệp đính kèm nào được tải lên cho sự cố này.").classes("text-xs font-medium")

                        def render_left_content():
                            left_content_pane.clear()
                            t_key = view_state["active_tab"]
                            if t_key == "OVERVIEW":
                                render_overview()
                            elif t_key == "ACTIVITY":
                                render_activity()
                            elif t_key == "ATTACHMENTS":
                                render_attachments()

                        render_left_content()

                    # ---------------------------------------------------------
                    # RIGHT COLUMN (Conversation Panel ~35% / 380-420px)
                    # ---------------------------------------------------------
                    with ui.column().classes("w-full lg:flex-[2] min-w-[320px] max-w-full lg:max-w-[440px] gap-4 sticky top-4"):
                        comments_thread(ticket_id, user, max_height="520px")

                # =============================================================
                # 3. WORKFLOW / STATUS ACTION BAR (Docked at Bottom)
                # =============================================================
                if role in ("ADMIN", "TECHNICIAN") or cur_status == "CLOSED":
                    with ui.card().classes(
                        "w-full p-4 sm:p-5 rounded-2xl bg-slate-900 text-white border border-slate-800 shadow-xl gap-4"
                    ):
                        with ui.row().classes("w-full justify-between items-center flex-wrap gap-4"):
                            with ui.row().classes("items-center gap-3"):
                                ui.icon("alt_route", size="22px").classes("text-blue-400")
                                with ui.column().classes("gap-0.5"):
                                    ui.label("Quy trình xử lý sự cố (Workflow Actions)").classes("text-sm font-bold text-slate-100")
                                    ui.label(f"Trạng thái hiện tại: {get_status_label(cur_status)}").classes("text-xs text-slate-400")

                            # Workflow Actions according to State & Role
                            with ui.row().classes("items-center gap-3 flex-wrap"):
                                async def do_update_status(target_s: str) -> None:
                                    try:
                                        await ticket_service.update_status(ticket_id, target_s)
                                        toast.success(f"Đã chuyển trạng thái: {get_status_label(target_s)}")
                                        await load_detail()
                                    except Exception as exc:
                                        toast.error(f"Lỗi cập nhật trạng thái: {exc}")

                                async def do_claim_ticket() -> None:
                                    try:
                                        await ticket_service.assign_ticket(ticket_id, int(user_id))
                                        toast.success("Đã tiếp nhận xử lý ticket thành công!")
                                        await load_detail()
                                    except Exception as exc:
                                        toast.error(f"Lỗi tiếp nhận ticket: {exc}")

                                async def open_close_modal() -> None:
                                    dialog = ui.dialog()
                                    with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-6 bg-white gap-4"):
                                        with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                                            ui.icon("lock", size="20px").classes("text-slate-800")
                                            ui.label(f"Đóng phiếu sự cố #{ticket_id}").classes("text-base font-bold text-slate-900")
                                        ui.label("Nhập ghi chú kết quả nghiệm thu hoặc phản hồi đóng ticket:").classes("text-xs text-slate-500")
                                        note_input = ui.textarea(placeholder="Nhập ghi chú kết quả xử lý...").props("outlined rows=3").classes("w-full text-sm")

                                        async def do_close() -> None:
                                            try:
                                                await ticket_service.close_ticket(ticket_id, note_input.value or None)
                                                toast.success(f"Đã đóng Ticket #{ticket_id} thành công!")
                                                dialog.close()
                                                await load_detail()
                                            except Exception as exc:
                                                toast.error(f"Lỗi đóng ticket: {exc}")

                                        with ui.row().classes("w-full justify-end gap-2 mt-2 pt-3 border-t border-slate-100"):
                                            ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm")
                                            ui.button("Xác nhận đóng ticket", icon="lock", on_click=do_close).props("color=primary unelevated size=sm").classes("font-bold")
                                    dialog.open()

                                async def open_assign_modal() -> None:
                                    dialog = ui.dialog()
                                    with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-6 bg-white gap-4"):
                                        with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                                            ui.icon("person_add", size="20px").classes("text-blue-600")
                                            ui.label(f"Phân công kỹ thuật viên #{ticket_id}").classes("text-base font-bold text-slate-900")
                                        tech_select = ui.select({}, label="Chọn Kỹ thuật viên phụ trách").props("outlined").classes("w-full text-sm")

                                        try:
                                            techs = await user_service.list_technicians()
                                            tech_select.options = {tech["id"]: f"{tech['ho_ten']} (@{tech['username']})" for tech in techs}
                                            tech_select.update()
                                        except Exception as exc:
                                            toast.error(f"Lỗi tải danh sách KTV: {exc}")

                                        async def do_assign() -> None:
                                            if not tech_select.value:
                                                toast.warning("Vui lòng chọn kỹ thuật viên.")
                                                return
                                            try:
                                                await ticket_service.assign_ticket(ticket_id, int(tech_select.value))
                                                toast.success(f"Phân công Ticket #{ticket_id} thành công!")
                                                dialog.close()
                                                await load_detail()
                                            except Exception as exc:
                                                toast.error(f"Lỗi phân công: {exc}")

                                        with ui.row().classes("w-full justify-end gap-2 mt-2 pt-3 border-t border-slate-100"):
                                            ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm")
                                            ui.button("Xác nhận phân công", icon="save", on_click=do_assign).props("color=primary unelevated size=sm").classes("font-bold")
                                    dialog.open()

                                if cur_status == "OPEN":
                                    if is_technician:
                                        ui.button("Tiếp nhận sự cố (Claim)", icon="bolt", on_click=do_claim_ticket).props("unelevated color=primary size=md").classes("font-bold px-4 py-2 rounded-xl")
                                    if can_assign:
                                        ui.button("Phân công kỹ thuật viên", icon="person_add", on_click=open_assign_modal).props("unelevated color=primary size=md").classes("font-bold px-4 py-2 rounded-xl")
                                elif cur_status == "ASSIGNED":
                                    ui.button("Bắt đầu xử lý (In Progress)", icon="play_arrow", on_click=lambda: do_update_status("IN_PROGRESS")).props("unelevated color=amber-600 size=md").classes("font-bold px-4 py-2 rounded-xl")
                                    if can_assign:
                                        ui.button("Đổi KTV", icon="swap_horiz", on_click=open_assign_modal).props("outline color=slate-300 size=md").classes("font-semibold px-3 py-2 rounded-xl")
                                elif cur_status == "IN_PROGRESS":
                                    ui.button("Đánh dấu đã giải quyết (Resolve)", icon="check_circle", on_click=lambda: do_update_status("RESOLVED")).props("unelevated color=emerald-600 size=md").classes("font-bold px-4 py-2 rounded-xl")
                                elif cur_status == "RESOLVED":
                                    ui.button("Đóng phiếu sự cố (Close)", icon="lock", on_click=open_close_modal).props("unelevated color=slate-700 size=md").classes("font-bold px-4 py-2 rounded-xl")
                                else:
                                    with ui.row().classes("items-center gap-2 text-slate-300 text-sm font-semibold"):
                                        ui.icon("check_circle", size="18px").classes("text-emerald-400")
                                        ui.label("Phiếu sự cố đã được đóng và lưu trữ hoàn tất.")

        ui.timer(0.1, load_detail, once=True)

    app_shell(f"Chi tiết sự cố #{ticket_id}", content)
