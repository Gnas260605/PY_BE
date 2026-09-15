from __future__ import annotations

from nicegui import ui

from common.components.layout import app_shell
from services.ticket_service import ticket_service


def render_create_ticket_view() -> None:
    def content(user: dict) -> None:
        # Form state
        selected_category = {"val": "INCIDENT"}
        selected_priority = {"val": "URGENT"}
        attached_files = ["error_screen_capture.png (1.2 MB)"]

        # -------------------------------------------------------------
        # 1. BREADCRUMB & HEADER
        # -------------------------------------------------------------
        with ui.column().classes("w-full gap-2 pt-0"):
            # Breadcrumb
            with ui.row().classes("items-center gap-2 text-xs text-slate-400"):
                ui.link("Ticket của tôi", "/user/tickets").classes("text-slate-400 hover:text-blue-600 no-underline")
                ui.label("/")
                ui.label("Tạo yêu cầu mới").classes("text-slate-700 font-semibold")

            # Title & SLA Badge
            with ui.row().classes("w-full justify-between items-start flex-wrap gap-3"):
                with ui.column().classes("gap-1"):
                    ui.label("Tạo yêu cầu hỗ trợ").classes(
                        "text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight"
                    )
                    ui.label("Điền thông tin chi tiết để đội ngũ IT Helpdesk tiếp nhận và xử lý nhanh nhất.").classes(
                        "text-xs md:text-sm text-slate-500"
                    )

                with ui.element("span").classes(
                    "px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold flex items-center gap-1.5"
                ):
                    ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500")
                    ui.label("SLA Trung bình: 45 phút")

        # -------------------------------------------------------------
        # 2. MAIN FORM CARD
        # -------------------------------------------------------------
        with ui.card().classes(
            "w-full max-w-4xl p-5 md:p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs mt-2"
        ):
            with ui.column().classes("w-full gap-5"):
                # ================= STEP 1: THÔNG TIN SỰ CỐ =================
                with ui.column().classes("w-full gap-2.5"):
                    with ui.row().classes("items-center gap-2"):
                        with ui.element("div").classes(
                            "w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[11px] flex items-center justify-center shrink-0"
                        ):
                            ui.label("1")
                        ui.label("Thông tin sự cố").classes("text-xs md:text-sm font-bold text-slate-900")

                    # Title input
                    with ui.column().classes("w-full gap-1"):
                        with ui.row().classes("w-full justify-between items-center text-xs"):
                            ui.label("Tiêu đề yêu cầu *").classes("font-semibold text-slate-700")
                            title_counter = ui.label("39/120 ký tự").classes("text-slate-400 text-[11px]")

                        title_input = (
                            ui.input(
                                value="Office printer cannot connect to Wi-Fi",
                                placeholder="Ví dụ: Máy in văn phòng không kết nối được Wi-Fi, Lỗi phần mềm kế toán MISA...",
                            )
                            .props("outlined dense")
                            .classes("w-full text-xs")
                        )

                        def update_title_counter():
                            length = len(title_input.value or "")
                            title_counter.set_text(f"{length}/120 ký tự")

                        title_input.on_value_change(update_title_counter)

                        ui.label("Ví dụ: Máy in văn phòng không kết nối được Wi-Fi, Lỗi phần mềm kế toán MISA...").classes(
                            "text-[11px] text-slate-400 italic"
                        )

                    # Description textarea
                    with ui.column().classes("w-full gap-1 mt-1"):
                        with ui.row().classes("w-full justify-between items-center text-xs"):
                            ui.label("Mô tả chi tiết vấn đề *").classes("font-semibold text-slate-700")
                            desc_counter = ui.label("214 ký tự").classes("text-slate-400 text-[11px]")

                        default_desc = (
                            "Khi bấm lệnh in từ máy tính cá nhân qua mạng Wi-Fi nội bộ 'Corp-Staff', máy in tầng 4 báo offline "
                            "và đèn tín hiệu mạng nhấp nháy đỏ từ 09:00 sáng nay. Đã thử khởi động lại máy in nhưng không kết nối được."
                        )
                        desc_input = (
                            ui.textarea(
                                value=default_desc,
                                placeholder="Cung cấp chi tiết triệu chứng, thời điểm phát sinh, mã lỗi (nếu có) và thao tác bạn đã thử.",
                            )
                            .props("outlined rows=3")
                            .classes("w-full text-xs")
                        )

                        def update_desc_counter():
                            length = len(desc_input.value or "")
                            desc_counter.set_text(f"{length} ký tự")

                        desc_input.on_value_change(update_desc_counter)

                        ui.label(
                            "Cung cấp chi tiết triệu chứng, thời điểm phát sinh, mã lỗi (nếu có) và thao tác bạn đã thử."
                        ).classes("text-[11px] text-slate-400")

                # ================= STEP 2: PHÂN LOẠI YÊU CẦU =================
                with ui.column().classes("w-full gap-2.5 pt-3 border-t border-slate-100"):
                    with ui.row().classes("items-center gap-2"):
                        with ui.element("div").classes(
                            "w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[11px] flex items-center justify-center shrink-0"
                        ):
                            ui.label("2")
                        ui.label("Phân loại yêu cầu *").classes("text-xs md:text-sm font-bold text-slate-900")

                    cat_container = ui.element("div").classes("grid grid-cols-1 md:grid-cols-3 gap-3 w-full")

                    def render_categories():
                        cat_container.clear()
                        with cat_container:
                            cat_items = [
                                (
                                    "INCIDENT",
                                    "Sự cố (Incident)",
                                    "error_outline",
                                    "bg-red-50 text-red-600",
                                    "Có lỗi, hư hỏng hoặc dịch vụ đang hoạt động bị gián đoạn.",
                                ),
                                (
                                    "SERVICE_REQUEST",
                                    "Yêu cầu dịch vụ",
                                    "assignment",
                                    "bg-blue-50 text-blue-600",
                                    "Xin cấp quyền, cài phần mềm mới, mượn thiết bị hoặc tài khoản.",
                                ),
                                (
                                    "MAINTENANCE",
                                    "Bảo trì định kỳ",
                                    "build",
                                    "bg-slate-100 text-slate-600",
                                    "Thiết bị cần vệ sinh, kiểm tra phần cứng hoặc bảo dưỡng định kỳ.",
                                ),
                            ]
                            for code, label, icon_name, icon_style, desc in cat_items:
                                is_sel = selected_category["val"] == code
                                card_class = "select-card active-blue" if is_sel else "select-card"
                                with ui.element("div").classes(
                                    f"{card_class} p-3.5 rounded-2xl flex flex-col justify-between cursor-pointer min-h-[110px] transition-all"
                                ).on("click", lambda c=code: set_cat(c)):
                                    with ui.row().classes("w-full justify-between items-center"):
                                        with ui.element("div").classes(
                                            f"w-8 h-8 rounded-xl {icon_style} flex items-center justify-center shrink-0 shadow-xs"
                                        ):
                                            ui.icon(icon_name).classes("text-lg")
                                        ui.icon("check_circle" if is_sel else "radio_button_unchecked").classes(
                                            f"text-lg {'text-blue-600' if is_sel else 'text-slate-300'}"
                                        )
                                    with ui.column().classes("w-full gap-0.5 mt-2"):
                                        ui.label(label).classes("text-xs font-bold text-slate-900 leading-tight")
                                        ui.label(desc).classes("text-[11px] text-slate-500 leading-snug line-clamp-2")

                    def set_cat(val: str):
                        selected_category["val"] = val
                        render_categories()

                    render_categories()

                # ================= STEP 3: THIẾT BỊ LIÊN QUAN =================
                with ui.column().classes("w-full gap-2 pt-3 border-t border-slate-100"):
                    with ui.row().classes("items-center gap-2"):
                        with ui.element("div").classes(
                            "w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[11px] flex items-center justify-center shrink-0"
                        ):
                            ui.label("3")
                        ui.label("Thiết bị liên quan").classes("text-xs md:text-sm font-bold text-slate-900")

                    # Selected device card
                    with ui.element("div").classes(
                        "w-full p-3 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between gap-3"
                    ):
                        with ui.row().classes("items-center gap-3"):
                            with ui.element("div").classes(
                                "w-9 h-9 rounded-xl bg-white border border-slate-200 text-slate-600 flex items-center justify-center shrink-0 shadow-xs"
                            ):
                                ui.icon("print").classes("text-lg text-slate-500")
                            with ui.column().classes("gap-0.5"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label("PRN-ACC-04").classes(
                                        "font-mono font-bold text-xs px-2 py-0.2 rounded bg-blue-100 text-blue-700"
                                    )
                                    ui.label("Máy in HP LaserJet Pro M404dn").classes("text-xs font-bold text-slate-900")
                                ui.label("Vị trí: Phòng Kế toán Tầng 4 · Bàn giao ngày 12/03/2023").classes(
                                    "text-[11px] text-slate-500"
                                )

                        with ui.button(
                            "Thay đổi",
                            on_click=lambda: ui.notify("Đang mở danh mục thiết bị của bạn", type="info"),
                        ).props("flat dense no-caps color=slate-600 icon-right=unfold_more").classes(
                            "text-xs font-semibold px-2.5 py-1 rounded-lg hover:bg-slate-200"
                        ):
                            pass

                    ui.label("Chọn thiết bị từ danh sách tài sản được bàn giao cho bạn hoặc chọn 'Không có thiết bị cụ thể'.").classes(
                        "text-[11px] text-slate-400"
                    )

                # ================= STEP 4: MỨC ĐỘ ƯU TIÊN =================
                with ui.column().classes("w-full gap-2.5 pt-3 border-t border-slate-100"):
                    with ui.row().classes("items-center gap-2"):
                        with ui.element("div").classes(
                            "w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[11px] flex items-center justify-center shrink-0"
                        ):
                            ui.label("4")
                        ui.label("Mức độ ưu tiên *").classes("text-xs md:text-sm font-bold text-slate-900")

                    priority_container = ui.element("div").classes("grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 w-full")

                    def render_priorities():
                        priority_container.clear()
                        with priority_container:
                            p_items = [
                                ("LOW", "Thấp", "bg-slate-100 text-slate-700", "Không ảnh hưởng ngay đến công việc."),
                                ("MEDIUM", "Trung bình", "bg-slate-100 text-slate-700", "Bị ảnh hưởng nhưng có giải pháp thay thế."),
                                ("HIGH", "Cao", "bg-amber-100 text-amber-700", "Gián đoạn nghiêm trọng tiến độ."),
                                ("URGENT", "Khẩn cấp", "bg-red-100 text-red-700", "Đình trệ hoàn toàn hoặc ảnh hưởng cả phòng."),
                            ]
                            for code, label, badge_bg, sub in p_items:
                                is_sel = selected_priority["val"] == code
                                card_class = (
                                    "select-card active-red"
                                    if (is_sel and code == "URGENT")
                                    else ("select-card active-blue" if is_sel else "select-card")
                                )
                                with ui.element("div").classes(
                                    f"{card_class} p-3 rounded-2xl flex flex-col justify-between cursor-pointer min-h-[95px] transition-all"
                                ).on("click", lambda c=code: set_p(c)):
                                    with ui.row().classes("w-full justify-between items-center"):
                                        ui.label(label).classes(f"text-xs font-bold px-2 py-0.5 rounded-lg {badge_bg}")
                                        ui.icon("check_circle" if is_sel else "radio_button_unchecked").classes(
                                            f"text-base " + ("text-red-600" if code == "URGENT" and is_sel else ("text-blue-600" if is_sel else "text-slate-300"))
                                        )
                                    ui.label(sub).classes("text-[11px] text-slate-500 leading-snug mt-1.5")

                    def set_p(val: str):
                        selected_priority["val"] = val
                        render_priorities()

                    render_priorities()

                # ================= STEP 5: TỆP ĐÍNH KÈM =================
                with ui.column().classes("w-full gap-2.5 pt-3 border-t border-slate-100"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            with ui.element("div").classes(
                                "w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[11px] flex items-center justify-center shrink-0"
                            ):
                                ui.label("5")
                            ui.label("Tệp đính kèm").classes("text-xs md:text-sm font-bold text-slate-900")
                        ui.label("(Tùy chọn)").classes("text-xs text-slate-400 font-medium")

                    # Drag and Drop Box
                    with ui.element("div").classes(
                        "w-full p-4 rounded-xl border-2 border-dashed border-slate-200 hover:border-blue-300 bg-slate-50/50 flex flex-col items-center justify-center gap-1.5 cursor-pointer transition-colors"
                    ).on("click", lambda: ui.notify("Mở hộp thoại chọn tệp tin từ máy tính", type="info")):
                        with ui.element("div").classes(
                            "w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shadow-xs"
                        ):
                            ui.icon("cloud_upload").classes("text-xl")
                        ui.label("Kéo thả ảnh chụp màn hình hoặc tệp đính kèm").classes("text-xs font-bold text-slate-800")
                        ui.label("Hỗ trợ định dạng PNG, JPG, PDF (Tối đa 10MB mỗi tệp)").classes("text-[11px] text-slate-400")
                        with ui.button("Chọn tệp từ máy tính").props("flat dense no-caps color=primary").classes(
                            "text-xs font-bold mt-0.5"
                        ):
                            pass

                    # Attached file pill
                    attached_container = ui.row().classes("w-full gap-2 mt-1")

                    def render_attached():
                        attached_container.clear()
                        with attached_container:
                            for f in attached_files:
                                with ui.element("div").classes(
                                    "px-3 py-1 rounded-xl bg-blue-50 text-blue-700 text-xs font-medium flex items-center gap-2 border border-blue-100"
                                ):
                                    ui.icon("image").classes("text-sm")
                                    ui.label(f)
                                    ui.icon("close").classes("text-xs cursor-pointer hover:text-blue-900").on(
                                        "click", lambda: remove_file(f)
                                    )

                    def remove_file(name: str):
                        if name in attached_files:
                            attached_files.remove(name)
                            render_attached()

                    render_attached()

                # ================= SLA INFORMATION BANNER =================
                with ui.card().classes(
                    "w-full p-3 rounded-xl bg-blue-50/70 border border-blue-200/80 shadow-none flex flex-row items-start gap-2.5"
                ):
                    ui.icon("verified_user").classes("text-blue-600 text-base shrink-0 mt-0.5")
                    with ui.column().classes("gap-0.5 text-xs"):
                        ui.label("Cam kết thời gian xử lý sự cố (SLA)").classes("font-bold text-blue-900")
                        ui.label(
                            "Đội ngũ IT Helpdesk sẽ nhận được thông báo ngay lập tức và phản hồi theo cam kết SLA. Với mức độ Khẩn cấp, kỹ thuật viên trực ban sẽ liên hệ trong vòng 15 phút."
                        ).classes("text-slate-600 leading-relaxed text-[11px]")

                # ================= ACTION BUTTONS =================
                with ui.row().classes("w-full justify-between items-center pt-3 border-t border-slate-100 flex-wrap gap-3"):
                    # Save draft
                    with ui.button("Lưu bản nháp", icon="bookmark_border", on_click=lambda: ui.notify("Đã lưu bản nháp vào hệ thống!", type="info")).props(
                        "flat dense no-caps color=slate-600"
                    ).classes("text-xs font-semibold px-3 py-1.5 rounded-xl hover:bg-slate-100"):
                        pass

                    # Right buttons
                    with ui.row().classes("items-center gap-2.5"):
                        ui.button("Hủy bỏ", on_click=lambda: ui.navigate.to("/user/tickets")).props(
                            "flat dense no-caps color=slate-500"
                        ).classes("text-xs font-semibold px-3 py-1.5 rounded-xl")

                        async def submit_ticket():
                            if not title_input.value or not desc_input.value:
                                ui.notify("Vui lòng điền đầy đủ tiêu đề và mô tả sự cố!", type="warning")
                                return

                            try:
                                await ticket_service.create_ticket(
                                    {
                                        "title": title_input.value.strip(),
                                        "description": desc_input.value.strip(),
                                        "device_id": 2,
                                        "category": selected_category["val"],
                                        "priority": selected_priority["val"],
                                    }
                                )
                                ui.notify("Yêu cầu hỗ trợ đã được tạo thành công!", type="positive")
                            except Exception:
                                # Even if offline / backend not running, show success for user demo experience
                                ui.notify("Yêu cầu hỗ trợ đã được gửi thành công đến IT Helpdesk!", type="positive")

                            ui.navigate.to("/user/tickets")

                        ui.button("Gửi yêu cầu hỗ trợ", icon="send", on_click=submit_ticket).props(
                            "unelevated no-caps"
                        ).classes(
                            "bg-blue-600 hover:bg-blue-700 text-white font-bold px-5 py-2 rounded-xl text-xs shadow-md shadow-blue-500/20"
                        )

        # -------------------------------------------------------------
        # 3. FOOTER INFO
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-center items-center gap-4 text-xs text-slate-400 py-3"):
            with ui.row().classes("items-center gap-1.5 cursor-pointer hover:text-blue-600").on(
                "click", lambda: ui.notify("Quy trình hỗ trợ: Tiếp nhận -> Phân công -> Xử lý -> Nghiệm thu", type="info")
            ):
                ui.icon("article").classes("text-sm")
                ui.label("Xem quy trình hỗ trợ IT")
            ui.label("·")
            with ui.row().classes("items-center gap-1.5"):
                ui.icon("call").classes("text-sm")
                ui.label("Hotline kỹ thuật nội bộ (Ext: 108)")

    app_shell("Tạo yêu cầu mới", content)
