from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.formatters import format_datetime, format_relative_time
from core.i18n import get_role_label, t
from services.ticket_service import ticket_service


ROLE_CONFIG = {
    "ADMIN": {
        "badge": "bg-purple-50 text-purple-700 border-purple-200",
        "avatar_bg": "bg-purple-600 text-white",
        "initial": "QT",
    },
    "TECHNICIAN": {
        "badge": "bg-blue-50 text-blue-700 border-blue-200",
        "avatar_bg": "bg-blue-600 text-white",
        "initial": "KT",
    },
    "USER": {
        "badge": "bg-slate-100 text-slate-700 border-slate-200",
        "avatar_bg": "bg-slate-700 text-white",
        "initial": "ND",
    },
}

QUICK_REPLIES = [
    ("Tiếp nhận", "Đang tiếp nhận và kiểm tra thiết bị."),
    ("Xác minh", "Đã liên hệ người yêu cầu để xác minh thông tin sự cố."),
    ("Đang xử lý", "Đang tiến hành cài đặt / thay thế linh kiện."),
    ("Đã xử lý", "Đã xử lý xong sự cố, vui lòng kiểm tra lại thiết bị."),
    ("Chờ phản hồi", "Đang chờ người dùng phản hồi kết quả sau khi xử lý."),
]


def comments_thread(
    ticket_id: int,
    current_user: dict[str, Any],
    *,
    max_height: str = "450px",
) -> None:
    current_user_id = current_user.get("id")
    current_role = current_user.get("vai_tro", "USER")

    with ui.card().classes("w-full p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm bg-white gap-3 flex flex-col"):
        # Header with Live Counter & Refresh
        with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
            with ui.row().classes("items-center gap-2.5"):
                ui.icon("chat_bubble_outline", size="20px").classes("text-blue-600")
                ui.label("Trao đổi & Phản hồi").classes("text-base font-bold text-slate-900")
                count_badge = ui.label("0").classes(
                    "text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200"
                )

            async def handle_refresh() -> None:
                await reload_comments()
                toast.info("Đã làm mới danh sách trao đổi")

            ui.button("Làm mới", icon="refresh", on_click=handle_refresh).props("flat dense size=sm color=slate-600").classes("text-xs font-semibold hover:bg-slate-50")

        # Scroll area for conversation feed
        scroll_container = ui.scroll_area().classes(f"w-full h-[{max_height}] p-3 sm:p-4 bg-slate-50/70 rounded-xl border border-slate-100")
        with scroll_container:
            messages_container = ui.column().classes("w-full gap-4")

        # Sticky Message Composer at bottom
        with ui.column().classes("w-full gap-2 pt-2 border-t border-slate-100"):
            # Quick Canned Replies Menu (For Admin & Technician)
            if current_role in ("ADMIN", "TECHNICIAN"):
                with ui.row().classes("w-full justify-between items-center"):
                    with ui.row().classes("items-center gap-1.5"):
                        ui.icon("bolt", size="16px").classes("text-amber-500")
                        ui.label("Câu trả lời mẫu:").classes("text-xs font-bold text-slate-600")

                    # Menu of Quick replies
                    with ui.button("Chọn mẫu phản hồi ▾").props("flat dense size=sm color=primary").classes("text-xs font-bold px-2 py-0.5 bg-blue-50 rounded-lg"):
                        with ui.menu().classes("p-1.5 rounded-xl border border-slate-200 shadow-lg min-w-[260px]"):
                            for label_short, full_text in QUICK_REPLIES:
                                def make_insert(txt=full_text):
                                    return lambda: insert_reply(txt)

                                with ui.menu_item(on_click=make_insert()).classes("rounded-lg hover:bg-blue-50 p-2 cursor-pointer"):
                                    with ui.column().classes("gap-0.5"):
                                        ui.label(label_short).classes("text-xs font-bold text-blue-800")
                                        ui.label(full_text).classes("text-[11px] text-slate-500 leading-tight")

            def insert_reply(text_to_insert: str) -> None:
                current_val = text_input.value or ""
                if current_val.strip():
                    text_input.set_value(f"{current_val.strip()}\n{text_to_insert}")
                else:
                    text_input.set_value(text_to_insert)
                text_input.run_method("focus")

            # Multiline Composer
            with ui.row().classes("w-full gap-2.5 items-end no-wrap"):
                text_input = (
                    ui.textarea(
                        placeholder="Nhập nội dung trao đổi với người dùng hoặc ghi chú kỹ thuật... (Enter để gửi, Shift+Enter xuống dòng)",
                    )
                    .props("outlined autogrow rows=2")
                    .classes("flex-1 text-sm bg-white rounded-xl")
                )

                async def send_comment() -> None:
                    content = (text_input.value or "").strip()
                    if not content:
                        toast.warning("Vui lòng nhập nội dung trao đổi trước khi gửi.")
                        return
                    try:
                        send_btn.props("loading")
                        await ticket_service.create_comment(ticket_id, content)
                        text_input.set_value("")
                        toast.success("Đã gửi phản hồi thành công!")
                        await reload_comments()
                    except Exception as exc:
                        toast.show_popup(
                            title="Lỗi gửi phản hồi",
                            message="Không thể gửi tin nhắn trao đổi lên hệ thống.",
                            type="error",
                            detail=str(exc),
                        )
                    finally:
                        send_btn.props(remove="loading")

                send_btn = (
                    ui.button("Gửi", icon="send", on_click=send_comment)
                    .props("color=primary unelevated size=md")
                    .classes("px-5 py-3 h-12 shrink-0 font-bold rounded-xl shadow-sm text-sm")
                )

        async def reload_comments() -> None:
            try:
                comments = await ticket_service.list_comments(ticket_id)
                count_badge.text = str(len(comments))

                messages_container.clear()
                with messages_container:
                    if not comments:
                        with ui.column().classes("w-full py-12 items-center justify-center text-center gap-2"):
                            ui.icon("chat", size="36px").classes("text-slate-300")
                            ui.label("Chưa có tin nhắn trao đổi").classes("text-sm font-bold text-slate-800")
                            ui.label("Nhập phản hồi bên dưới để bắt đầu trao đổi với người yêu cầu hoặc kỹ thuật viên.").classes("text-xs text-slate-500 max-w-sm leading-relaxed")
                    else:
                        for item in comments:
                            author_id = item.get("user_id")
                            is_me = author_id == current_user_id
                            author_name = item.get("user_name") or t("user_label", id=author_id)
                            role = item.get("user_role") or "USER"
                            created_time = format_datetime(item.get("created_at"))
                            relative_time = format_relative_time(item.get("created_at"))
                            content_txt = item.get("content") or item.get("noi_dung") or ""

                            cfg = ROLE_CONFIG.get(role, ROLE_CONFIG["USER"])
                            role_label = get_role_label(role)
                            initial = author_name[:2].upper() if author_name else cfg["initial"]

                            if is_me:
                                # Outgoing Message (Me) - Right aligned
                                with ui.row().classes("w-full justify-end items-start gap-2.5 no-wrap"):
                                    with ui.column().classes("items-end max-w-[85%] gap-1"):
                                        with ui.row().classes("items-center gap-2 px-1"):
                                            ui.label(relative_time).classes("text-xs text-slate-400 font-medium")
                                            ui.label(f"• {created_time}").classes("text-xs text-slate-400 font-mono hidden sm:inline")
                                            ui.label("Bạn").classes("text-xs font-bold text-blue-900")
                                            ui.label(role_label).classes(
                                                f"text-[10px] font-bold px-2 py-0.5 rounded border {cfg['badge']}"
                                            )

                                        with ui.element("div").classes(
                                            "p-3.5 text-sm leading-relaxed bg-blue-600 text-white rounded-2xl rounded-tr-xs shadow-sm whitespace-pre-wrap break-words font-normal"
                                        ):
                                            ui.label(content_txt)

                                    with ui.element("div").classes(
                                        f"w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shrink-0 shadow-2xs border border-blue-700 {cfg['avatar_bg']}"
                                    ):
                                        ui.label(initial)

                            else:
                                # Incoming Message (Other) - Left aligned
                                with ui.row().classes("w-full justify-start items-start gap-2.5 no-wrap"):
                                    with ui.element("div").classes(
                                        f"w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shrink-0 shadow-2xs border border-slate-300 {cfg['avatar_bg']}"
                                    ):
                                        ui.label(initial)

                                    with ui.column().classes("items-start max-w-[85%] gap-1"):
                                        with ui.row().classes("items-center gap-2 px-1"):
                                            ui.label(author_name).classes("text-xs font-bold text-slate-900")
                                            ui.label(role_label).classes(
                                                f"text-[10px] font-bold px-2 py-0.5 rounded border {cfg['badge']}"
                                            )
                                            ui.label(relative_time).classes("text-xs text-slate-400 font-medium")
                                            ui.label(f"• {created_time}").classes("text-xs text-slate-400 font-mono hidden sm:inline")

                                        with ui.element("div").classes(
                                            "p-3.5 text-sm leading-relaxed bg-white text-slate-800 border border-slate-200 rounded-2xl rounded-tl-xs shadow-2xs whitespace-pre-wrap break-words font-normal"
                                        ):
                                            ui.label(content_txt)

            except Exception as exc:
                messages_container.clear()
                with messages_container:
                    ui.label(f"Lỗi tải tin nhắn: {exc}").classes("text-xs text-red-600")

        ui.timer(0.1, reload_comments, once=True)
