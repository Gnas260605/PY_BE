from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.formatters import format_datetime, format_relative_time
from services.ticket_service import ticket_service


ROLE_CONFIG = {
    "ADMIN": {
        "label": "Quản trị viên",
        "badge": "bg-purple-50 text-purple-700 border-purple-200",
        "avatar_bg": "bg-purple-600 text-white",
        "icon": "admin_panel_settings",
    },
    "TECHNICIAN": {
        "label": "Kỹ thuật viên",
        "badge": "bg-blue-50 text-blue-700 border-blue-200",
        "avatar_bg": "bg-blue-600 text-white",
        "icon": "build",
    },
    "USER": {
        "label": "Người yêu cầu",
        "badge": "bg-slate-100 text-slate-700 border-slate-200",
        "avatar_bg": "bg-slate-600 text-white",
        "icon": "person",
    },
}

QUICK_REPLIES = [
    "⚡ Đang tiếp nhận và kiểm tra thiết bị.",
    "📞 Đã liên hệ người yêu cầu để xác minh lỗi.",
    "🔧 Đang tiến hành cài đặt / thay thế linh kiện.",
    "✅ Đã xử lý xong sự cố, vui lòng kiểm tra lại.",
    "⏳ Đang chờ người dùng phản hồi kết quả.",
]


def comments_thread(
    ticket_id: int,
    current_user: dict[str, Any],
    *,
    compact: bool = False,
    max_height: str = "320px",
) -> None:
    current_user_id = current_user.get("id")
    current_role = current_user.get("vai_tro", "USER")

    card_padding = "p-3.5" if compact else "p-5"

    with ui.card().classes(f"w-full {card_padding} rounded-xl border border-slate-200 shadow-2xs bg-white mt-1 gap-2.5"):
        # Header with Live Counter & Refresh
        with ui.row().classes("w-full justify-between items-center pb-2.5 border-b border-slate-100"):
            with ui.row().classes("items-center gap-2"):
                with ui.element("div").classes("w-7 h-7 rounded-lg bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center"):
                    ui.icon("forum", size="16px")
                with ui.column().classes("gap-0"):
                    with ui.row().classes("items-center gap-2"):
                        ui.label("Trao đổi & Ghi chú Kỹ thuật").classes("text-sm font-bold text-slate-900")
                        count_badge = ui.label("0 tin nhắn").classes(
                            "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200"
                        )
                    ui.label("Phản hồi trực tiếp giữa Người dùng, Kỹ thuật viên & Quản trị").classes("text-[11px] text-slate-400")

            async def handle_refresh() -> None:
                await reload_comments()
                toast.info("Đã làm mới luồng trao đổi.")

            ui.button(icon="refresh", on_click=handle_refresh).props("flat dense round size=sm color=slate-400").tooltip("Làm mới tin nhắn")

        # Scroll area for conversation feed
        scroll_container = ui.scroll_area().classes(f"w-full h-[{max_height}] p-3 bg-slate-50/70 rounded-xl border border-slate-100/90")
        with scroll_container:
            messages_container = ui.column().classes("w-full gap-3")

        # Quick Canned Replies for Technicians & Admins
        if current_role in ("ADMIN", "TECHNICIAN"):
            with ui.column().classes("w-full gap-1 pt-1"):
                ui.label("Gợi ý phản hồi nhanh:").classes("text-[10px] font-semibold text-slate-400 uppercase tracking-wider")
                with ui.row().classes("w-full gap-1.5 flex-wrap"):
                    for reply in QUICK_REPLIES:
                        def insert_text(t: str = reply) -> None:
                            text_input.set_value(t)
                            text_input.run_method("focus")

                        ui.button(reply, on_click=insert_text).props("flat dense size=xs color=slate-700").classes(
                            "text-[10px] px-2 py-0.5 rounded-full bg-slate-100/90 hover:bg-blue-50 hover:text-blue-700 border border-slate-200/80 transition-colors font-medium"
                        )

        # Message Input Composer
        with ui.row().classes("w-full gap-2 items-end no-wrap pt-1"):
            text_input = (
                ui.textarea(
                    placeholder="Nhập nội dung phản hồi hoặc ghi chú kỹ thuật... (Enter để gửi)",
                )
                .props("outlined autogrow dense rows=1")
                .classes("flex-1 text-xs bg-white rounded-lg")
            )

            async def send_comment() -> None:
                content = (text_input.value or "").strip()
                if not content:
                    toast.warning("Vui lòng nhập nội dung trao đổi.")
                    return
                try:
                    send_btn.props("loading")
                    await ticket_service.create_comment(ticket_id, content)
                    text_input.set_value("")
                    toast.success("Đã gửi tin nhắn thành công!")
                    await reload_comments()
                except Exception as exc:
                    toast.show_popup(
                        title="Không thể gửi tin nhắn",
                        message="Đã có lỗi xảy ra khi lưu nội dung phản hồi.",
                        type="error",
                        detail=str(exc),
                    )
                finally:
                    send_btn.props(remove="loading")

            send_btn = (
                ui.button("Gửi", icon="send", on_click=send_comment)
                .props("color=primary unelevated size=sm")
                .classes("px-4 py-2.5 h-10 shrink-0 font-bold rounded-lg shadow-2xs")
            )

        async def reload_comments() -> None:
            try:
                comments = await ticket_service.list_comments(ticket_id)
                count_badge.text = f"{len(comments)} tin nhắn"

                messages_container.clear()
                with messages_container:
                    if not comments:
                        with ui.column().classes("w-full py-10 items-center justify-center text-center gap-1.5"):
                            with ui.element("div").classes("w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-400"):
                                ui.icon("chat_bubble_outline", size="20px")
                            ui.label("Chưa có trao đổi nào").classes("text-xs font-bold text-slate-700")
                            ui.label("Hãy để lại phản hồi đầu tiên để bắt đầu quá trình hỗ trợ xử lý.").classes("text-[11px] text-slate-400 max-w-xs")
                    else:
                        for item in comments:
                            author_id = item.get("user_id")
                            is_me = author_id == current_user_id
                            author_name = item.get("user_name") or f"User #{author_id}"
                            role = item.get("user_role") or "USER"
                            created_time = format_datetime(item.get("created_at"))
                            relative_time = format_relative_time(item.get("created_at"))
                            content = item.get("content") or item.get("noi_dung") or ""

                            cfg = ROLE_CONFIG.get(role, ROLE_CONFIG["USER"])

                            if is_me:
                                # Outgoing Message (Me) - Right aligned
                                with ui.row().classes("w-full justify-end items-start gap-2 no-wrap"):
                                    with ui.column().classes("items-end max-w-[82%] gap-1"):
                                        with ui.row().classes("items-center gap-1.5 px-1"):
                                            ui.label(relative_time).classes("text-[10px] text-slate-400")
                                            ui.label(f"• {created_time}").classes("text-[9px] text-slate-400 hidden sm:inline")
                                            ui.label("Bạn").classes("text-[11px] font-bold text-blue-900")
                                            ui.label(cfg["label"]).classes(
                                                f"text-[9px] font-bold px-1.5 py-0.2 rounded border {cfg['badge']}"
                                            )

                                        with ui.element("div").classes(
                                            "p-3 text-xs leading-relaxed bg-blue-600 text-white rounded-2xl rounded-tr-xs shadow-xs whitespace-pre-wrap break-words"
                                        ):
                                            ui.label(content)

                                    with ui.element("div").classes(
                                        f"w-8 h-8 rounded-full flex items-center justify-center font-bold text-[11px] shrink-0 shadow-2xs {cfg['avatar_bg']}"
                                    ):
                                        ui.icon(cfg["icon"], size="16px")

                            else:
                                # Incoming Message (Other) - Left aligned
                                with ui.row().classes("w-full justify-start items-start gap-2 no-wrap"):
                                    with ui.element("div").classes(
                                        f"w-8 h-8 rounded-full flex items-center justify-center font-bold text-[11px] shrink-0 shadow-2xs {cfg['avatar_bg']}"
                                    ):
                                        ui.icon(cfg["icon"], size="16px")

                                    with ui.column().classes("items-start max-w-[82%] gap-1"):
                                        with ui.row().classes("items-center gap-1.5 px-1"):
                                            ui.label(author_name).classes("text-[11px] font-bold text-slate-900")
                                            ui.label(cfg["label"]).classes(
                                                f"text-[9px] font-bold px-1.5 py-0.2 rounded border {cfg['badge']}"
                                            )
                                            ui.label(relative_time).classes("text-[10px] text-slate-400")
                                            ui.label(f"• {created_time}").classes("text-[9px] text-slate-400 hidden sm:inline")

                                        with ui.element("div").classes(
                                            "p-3 text-xs leading-relaxed bg-white text-slate-800 border border-slate-200/90 rounded-2xl rounded-tl-xs shadow-2xs whitespace-pre-wrap break-words"
                                        ):
                                            ui.label(content)

            except Exception as exc:
                messages_container.clear()
                with messages_container:
                    ui.label(f"Lỗi tải bình luận: {exc}").classes("text-xs text-red-600")

        ui.timer(0.1, reload_comments, once=True)
