from __future__ import annotations

from nicegui import ui

from common.components.layout import app_shell
from views.user.demo_data import DEMO_TICKETS


def render_ticket_timeline_view(ticket_id: int) -> None:
    def content(user: dict) -> None:
        # Find ticket or fallback to #1048
        ticket = next((t for t in DEMO_TICKETS if t["id"] == ticket_id), DEMO_TICKETS[0])

        # -------------------------------------------------------------
        # 1. BREADCRUMB & HEADER
        # -------------------------------------------------------------
        with ui.column().classes("w-full gap-2 pt-2"):
            # Breadcrumb
            with ui.row().classes("items-center gap-2 text-xs text-slate-400"):
                ui.link("Ticket của tôi", "/user/tickets").classes("text-slate-400 hover:text-blue-600 no-underline")
                ui.label("/")
                ui.label(f"#{ticket['id']}").classes("text-slate-700 font-semibold")

            # Title & Status row
            with ui.row().classes("w-full justify-between items-start flex-wrap gap-4"):
                with ui.column().classes("gap-1.5 flex-1"):
                    ui.label(ticket["title"]).classes(
                        "text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight leading-snug"
                    )
                    with ui.row().classes("items-center gap-3 text-xs text-slate-400 flex-wrap"):
                        ui.label(f"#{ticket['id']}").classes("font-bold text-blue-600 px-1.5 py-0.2 rounded bg-blue-50")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("event").classes("text-sm text-slate-400")
                            ui.label(ticket.get("created_at", "12/09/2026 lúc 09:42")).classes("text-slate-500")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("person").classes("text-sm text-slate-400")
                            ui.label(ticket.get("creator_name", "Trần Thị Mai (Phòng Kế toán)")).classes("text-slate-500")

                with ui.element("span").classes(
                    "px-3 py-1 rounded-full bg-blue-50 text-blue-700 font-bold text-xs border border-blue-200 shrink-0"
                ):
                    ui.label(f"● {ticket['status_label']}")

        # -------------------------------------------------------------
        # 2. INFO CALLOUT BANNER (Image 3)
        # -------------------------------------------------------------
        with ui.card().classes(
            "w-full p-4 rounded-2xl bg-blue-50/70 border border-blue-200/80 shadow-none flex flex-row items-start gap-3 mt-1"
        ):
            ui.icon("info").classes("text-blue-600 text-xl shrink-0 mt-0.5")
            with ui.column().classes("gap-0.5 text-xs text-slate-700"):
                ui.label("Yêu cầu đã được phân công thực tế").classes("font-bold text-blue-900")
                ui.label(
                    "Ticket đã được phân công và đang được kỹ thuật viên xử lý trực tiếp tại hạ tầng nên không thể chỉnh sửa các thông tin ban đầu. Quý khách vui lòng để lại phản hồi ở khung trao đổi bên dưới."
                ).classes("text-slate-600 leading-relaxed")

        # -------------------------------------------------------------
        # 3. TWO COLUMN LAYOUT
        # -------------------------------------------------------------
        with ui.element("div").classes("grid grid-cols-1 lg:grid-cols-12 gap-5 w-full items-start mt-2"):
            # ================= LEFT COLUMN (~65% = 8 of 12) =================
            with ui.column().classes("lg:col-span-8 w-full gap-5"):
                # Card: Mô tả chi tiết từ người dùng
                with ui.card().classes("w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("description").classes("text-blue-600 text-base")
                            ui.label("Mô tả chi tiết từ người dùng").classes("text-sm font-bold text-slate-900")
                        ui.label(f"Bản gốc #{ticket['id']}").classes("text-xs text-slate-400 font-medium")

                    ui.label(ticket["description"]).classes(
                        "text-xs md:text-sm text-slate-700 leading-relaxed mt-2 whitespace-pre-line"
                    )

                    # Tệp đính kèm
                    with ui.column().classes("w-full gap-2 mt-4 pt-3 border-t border-slate-100"):
                        ui.label(f"Tệp đính kèm ({len(ticket.get('attachments', []))})").classes(
                            "text-xs font-bold text-slate-700"
                        )
                        with ui.row().classes("w-full gap-3 flex-wrap sm:flex-nowrap"):
                            for att in ticket.get("attachments", []):
                                with ui.element("div").classes(
                                    "p-3 rounded-xl border border-slate-200 hover:border-blue-300 bg-slate-50/50 flex items-center justify-between gap-3 flex-1 min-w-[200px]"
                                ):
                                    with ui.row().classes("items-center gap-3 min-w-0"):
                                        icon_file = "image" if att["type"] == "image" else "article"
                                        ui.icon(icon_file).classes("text-blue-600 text-xl shrink-0")
                                        with ui.column().classes("gap-0 min-w-0"):
                                            ui.label(att["name"]).classes("text-xs font-bold text-slate-800 truncate")
                                            ui.label(f"{att['size']} · {att['action']}").classes("text-[10px] text-slate-400")
                                    ui.button(
                                        icon="visibility" if att["type"] == "image" else "download",
                                        on_click=lambda a=att: ui.notify(f"Đang mở tệp {a['name']}", type="info"),
                                    ).props("flat round dense color=slate-500").classes("shrink-0")

                # Card: Tiến độ xử lý & Lịch sử hoạt động (Thời gian thực)
                with ui.card().classes("w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("history").classes("text-blue-600 text-base")
                            ui.label("Tiến độ xử lý & Lịch sử hoạt động").classes("text-sm font-bold text-slate-900")
                        with ui.row().classes("items-center gap-1.5"):
                            ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500 animate-pulse")
                            ui.label("Thời gian thực").classes("text-[11px] font-bold text-emerald-700")

                    # Timeline items
                    with ui.column().classes("w-full gap-5 mt-4 relative pl-2"):
                        for item in ticket.get("history", []):
                            with ui.row().classes("w-full items-start gap-3 no-wrap relative"):
                                # Dot
                                is_tech = item.get("is_tech_comment", False)
                                dot_bg = "bg-blue-600 text-white" if is_tech else "bg-slate-100 text-slate-500 border border-slate-200"
                                with ui.element("div").classes(
                                    f"w-7 h-7 rounded-full {dot_bg} flex items-center justify-center shrink-0 text-xs shadow-sm z-10"
                                ):
                                    ui.icon("build" if is_tech else "update").classes("text-sm")

                                with ui.column().classes("gap-1 flex-1"):
                                    # Author / Action row
                                    with ui.row().classes("items-center gap-2 flex-wrap"):
                                        if is_tech:
                                            ui.label(item["author"]).classes("text-xs font-bold text-slate-900")
                                            ui.label(item["author_role"]).classes(
                                                "text-[10px] font-semibold px-2 py-0.2 rounded bg-blue-50 text-blue-700 border border-blue-200"
                                            )
                                        else:
                                            ui.label(item["action"]).classes("text-xs font-bold text-slate-800")
                                        ui.label(item["time"]).classes("text-[11px] text-slate-400 font-medium")

                                    # Content
                                    if is_tech and "quote" in item:
                                        with ui.element("div").classes(
                                            "w-full p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed italic"
                                        ):
                                            ui.label(f'"{item["quote"]}"')
                                        if item.get("tags"):
                                            with ui.row().classes("items-center gap-2 mt-1"):
                                                for tag in item["tags"]:
                                                    ui.label(tag).classes(
                                                        "text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200"
                                                    )
                                    else:
                                        ui.label(item.get("text", "")).classes("text-xs text-slate-600 leading-relaxed")

                # Card: Trao đổi / Phản hồi bổ sung
                with ui.card().classes("w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    with ui.row().classes("items-center gap-2 pb-2"):
                        ui.icon("chat").classes("text-blue-600 text-base")
                        ui.label("Trao đổi / Phản hồi bổ sung").classes("text-sm font-bold text-slate-900")

                    feedback_input = ui.textarea(
                        placeholder="Gửi thêm thông tin hoặc ghi chú cho kỹ thuật viên..."
                    ).props("outlined rows=3").classes("w-full text-xs")

                    with ui.row().classes("w-full justify-between items-center pt-2 flex-wrap gap-2 text-xs"):
                        with ui.row().classes("items-center gap-1.5 text-slate-400"):
                            ui.icon("lock").classes("text-xs text-slate-400")
                            ui.label("Thông tin chỉ hiển thị nội bộ cho đội kỹ thuật IT").classes("text-[11px]")
                        ui.label("0/500 ký tự").classes("text-[11px] text-slate-400")

                    with ui.row().classes("w-full justify-end mt-2"):
                        def send_feedback():
                            if not feedback_input.value:
                                ui.notify("Vui lòng nhập nội dung phản hồi", type="warning")
                                return
                            ui.notify("Đã gửi phản hồi thành công đến kỹ thuật viên!", type="positive")
                            feedback_input.value = ""

                        ui.button("Gửi phản hồi", icon="send", on_click=send_feedback).props(
                            "unelevated no-caps"
                        ).classes("bg-blue-600 hover:bg-blue-700 text-white font-bold px-5 py-2 rounded-xl text-xs")

            # ================= RIGHT COLUMN (~35% = 4 of 12) =================
            with ui.column().classes("lg:col-span-4 w-full gap-5"):
                # 1. Card: THÔNG TIN PHÂN LOẠI
                with ui.card().classes("w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    ui.label("THÔNG TIN PHÂN LOẠI").classes(
                        "text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-3"
                    )

                    with ui.column().classes("w-full gap-3 text-xs"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Trạng thái").classes("text-slate-500 font-medium")
                            ui.label(f"● {ticket['status_label']}").classes(
                                "font-bold text-blue-700 px-2 py-0.5 rounded bg-blue-50"
                            )

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Mức độ ưu tiên").classes("text-slate-500 font-medium")
                            ui.label(f"⚠️ {ticket['priority_label']}").classes(
                                "font-bold text-red-700 px-2 py-0.5 rounded bg-red-50 border border-red-200"
                            )

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Phân loại").classes("text-slate-500 font-medium")
                            ui.label(f"{ticket['category_label']} (Incident)").classes("font-semibold text-slate-800")

                        with ui.column().classes("w-full gap-1 pt-2 border-t border-slate-100"):
                            ui.label("Thiết bị liên quan").classes("text-slate-500 font-medium")
                            with ui.row().classes("items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-200"):
                                ui.icon("print").classes("text-slate-500 text-sm")
                                with ui.column().classes("gap-0"):
                                    ui.label(ticket["device_code"]).classes("font-mono font-bold text-slate-900 text-[11px]")
                                    ui.label(ticket.get("device_name", "")).classes("text-[10px] text-slate-500")

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Vị trí thiết bị").classes("text-slate-500 font-medium")
                            ui.label(ticket.get("device_location", "Tầng 4 - Tòa nhà A")).classes(
                                "font-semibold text-slate-800"
                            )

                        with ui.column().classes("w-full gap-0.5 pt-2 border-t border-slate-100"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("SLA phản hồi").classes("text-slate-500 font-medium")
                                with ui.row().classes("items-center gap-1 text-emerald-600 font-bold"):
                                    ui.icon("check_circle").classes("text-xs")
                                    ui.label(ticket.get("sla_status", "Đạt cam kết"))
                            ui.label(ticket.get("sla_detail", "Cam kết < 30 phút · Đã phản hồi sau 8 phút")).classes(
                                "text-[10px] text-slate-400"
                            )

                        with ui.row().classes("w-full justify-between items-center pt-2 border-t border-slate-100"):
                            ui.label("Lần cập nhật cuối").classes("text-slate-500 font-medium")
                            ui.label(ticket.get("updated_time", "12 phút trước")).classes("font-semibold text-slate-800")

                # 2. Card: KỸ THUẬT VIÊN PHỤ TRÁCH
                with ui.card().classes("w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    ui.label("KỸ THUẬT VIÊN PHỤ TRÁCH").classes(
                        "text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-3"
                    )

                    with ui.row().classes("items-center gap-3"):
                        with ui.element("div").classes(
                            "w-11 h-11 rounded-full bg-slate-200 text-slate-800 font-bold flex items-center justify-center text-sm shrink-0 ring-2 ring-blue-100"
                        ):
                            ui.label((ticket.get("tech_initial") or "NA")[:2])

                        with ui.column().classes("gap-0"):
                            ui.label(ticket["tech_name"]).classes("text-sm font-bold text-slate-900")
                            ui.label(ticket.get("tech_spec", "Chuyên viên IT L2")).classes("text-[11px] text-slate-500")
                            with ui.row().classes("items-center gap-1.5 mt-0.5"):
                                ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500")
                                ui.label(ticket.get("tech_status", "Đang trực tuyến")).classes(
                                    "text-[10px] font-bold text-emerald-700"
                                )

                    with ui.column().classes("w-full gap-2 mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("mail").classes("text-slate-400 text-sm")
                            ui.label(ticket.get("tech_email", "an.nguyen@helpdeskpro.enterprise")).classes(
                                "text-[11px] font-mono text-slate-700 truncate"
                            )
                        with ui.row().classes("items-center justify-between"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("call").classes("text-slate-400 text-sm")
                                ui.label("Máy lẻ nội bộ:").classes("text-slate-500")
                            ui.label(ticket.get("tech_ext", "Ext 114")).classes("font-mono font-bold text-blue-700")

                # 3. Card: Hướng dẫn dành cho bạn
                with ui.card().classes("w-full p-4 rounded-2xl bg-blue-50/50 border border-blue-100 shadow-none"):
                    with ui.row().classes("items-start gap-2.5"):
                        with ui.element("div").classes(
                            "w-8 h-8 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center shrink-0"
                        ):
                            ui.icon("mark_email_read").classes("text-base")
                        with ui.column().classes("gap-1 text-xs text-slate-600"):
                            ui.label("Hướng dẫn dành cho bạn").classes("font-bold text-slate-900")
                            ui.label(
                                "Bạn sẽ nhận thông báo qua email ngay khi sự cố được giải quyết hoặc kỹ thuật viên cần thêm thông tin xác nhận. Vui lòng giữ máy tính kết nối mạng để IT hỗ trợ từ xa khi cần."
                            ).classes("text-[11px] leading-relaxed text-slate-500")

    app_shell(f"Chi tiết Ticket #{ticket_id}", content)
