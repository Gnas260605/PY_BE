from typing import Any
from nicegui import ui

from common.components import toast
from common.formatters import format_datetime
from services.ticket_service import ticket_service


def comments_thread(ticket_id: int, current_user: dict) -> None:
    current_user_id = current_user.get("id")

    with ui.card().classes("w-full p-5 rounded-xl border border-slate-200 shadow-sm bg-white mt-2"):
        with ui.row().classes("w-full justify-between items-center mb-3 pb-2 border-b border-slate-100"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("forum", color="primary").classes("text-base")
                ui.label("Trao đổi & Bình luận").classes("text-sm font-bold text-slate-900")
            ui.label("Phản hồi trực tiếp giữa người dùng và KTV").classes("text-xs text-slate-400")

        # Scroll area for messages
        with ui.scroll_area().classes("w-full h-64 p-3 bg-slate-50/70 rounded-xl border border-slate-100 mb-3"):
            messages_container = ui.column().classes("w-full gap-2.5")

        # Comment input form
        with ui.row().classes("w-full gap-2 items-end no-wrap"):
            text_input = ui.textarea(placeholder="Nhập nội dung phản hồi... (Enter hoặc bấm Gửi)").props("outlined autogrow dense rows=1").classes("flex-1")

            async def send_comment() -> None:
                content = (text_input.value or "").strip()
                if not content:
                    toast.warning("Vui lòng nhập nội dung bình luận.")
                    return
                try:
                    await ticket_service.create_comment(ticket_id, content)
                    text_input.set_value("")
                    toast.success("Đã gửi phản hồi thành công! 💬")
                    await reload_comments()
                except Exception as exc:
                    toast.show_popup(
                        title="Không thể gửi phản hồi",
                        message="Đã có lỗi xảy ra khi gửi tin nhắn trao đổi.",
                        type="error",
                        detail=str(exc),
                    )

            ui.button("Gửi", icon="send", on_click=send_comment).props("color=primary unelevated size=sm").classes("px-4 py-2.5 shrink-0")

        async def reload_comments() -> None:
            try:
                comments = await ticket_service.list_comments(ticket_id)
                messages_container.clear()
                with messages_container:
                    if not comments:
                        with ui.column().classes("w-full py-12 items-center text-center gap-1"):
                            ui.icon("chat_bubble_outline").classes("text-3xl text-slate-300")
                            ui.label("Chưa có trao đổi nào").classes("text-xs font-semibold text-slate-700")
                            ui.label("Nhập tin nhắn bên dưới để gửi phản hồi.").classes("text-[11px] text-slate-400")
                    else:
                        for item in comments:
                            author_id = item.get("user_id")
                            is_me = author_id == current_user_id
                            author_name = item.get("user_name") or f"User #{author_id}"
                            role = item.get("user_role") or "USER"
                            created_time = format_datetime(item.get("created_at"))
                            content = item.get("content") or item.get("noi_dung") or ""

                            align_class = "self-end items-end" if is_me else "self-start items-start"
                            bubble_style = (
                                "bg-blue-600 text-white rounded-2xl rounded-tr-xs"
                                if is_me
                                else "bg-white text-slate-900 border border-slate-200 rounded-2xl rounded-tl-xs shadow-xs"
                            )

                            with ui.column().classes(f"max-w-[85%] {align_class} gap-1"):
                                with ui.row().classes("items-center gap-1.5 px-1"):
                                    ui.label(author_name if not is_me else "Bạn").classes("text-[11px] font-bold text-slate-700")
                                    if role in ("ADMIN", "TECHNICIAN") and not is_me:
                                        ui.label("KTV / ADMIN").classes("text-[9px] font-bold px-1.5 py-0.2 bg-blue-50 text-blue-700 rounded border border-blue-200")
                                    ui.label(created_time).classes("text-[10px] text-slate-400")

                                with ui.element("div").classes(f"p-2.5 text-xs leading-relaxed {bubble_style}"):
                                    ui.label(content).classes("whitespace-pre-wrap")
            except Exception as exc:
                messages_container.clear()
                with messages_container:
                    ui.label(f"Lỗi tải bình luận: {exc}").classes("text-xs text-red-600")

        ui.timer(0.1, reload_comments, once=True)
