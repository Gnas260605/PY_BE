from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.comments_thread import comments_thread
from common.components.layout import app_shell
from common.components.status_badge import priority_badge, status_badge
from common.components.timeline import audit_timeline
from common.formatters import format_datetime
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


def render_ticket_detail_view(ticket_id: int) -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")
        role = user.get("vai_tro", "USER")
        can_assign = role == "ADMIN"
        is_technician = role == "TECHNICIAN"

        # Container
        main_container = ui.column().classes("w-full gap-4")

        async def load_detail() -> None:
            try:
                ticket = await ticket_service.get_ticket(ticket_id)
                history = await ticket_service.get_history(ticket_id)
            except Exception as exc:
                main_container.clear()
                with main_container:
                    ui.label(f"Ticket #{ticket_id}: {exc}").classes("text-sm text-red-600")
                return

            cur_status = ticket.get("status")
            assigned_tech_id = ticket.get("technician_id")
            category_label = get_category_label(ticket.get("category"))
            ticket_title = get_ticket_title(ticket.get("title"))
            ticket_desc = get_ticket_desc(ticket.get("description"))

            main_container.clear()
            with main_container:
                # Top Navigation Breadcrumb & Actions
                with ui.row().classes("w-full justify-between items-center py-1 border-b border-slate-200 mb-2"):
                    with ui.row().classes("items-center gap-2.5"):
                        ui.button(icon="arrow_back", on_click=lambda: ui.navigate.back()).props("flat round dense size=sm color=slate-700")
                        ui.label(f"Ticket #{ticket.get('id')}").classes("text-lg font-bold text-slate-900")
                        status_badge(cur_status)
                        priority_badge(ticket.get("priority"))

                    with ui.row().classes("items-center gap-2"):
                        ui.button(t("btn_refresh"), icon="refresh", on_click=load_detail).props("outline dense size=sm color=slate-700").classes("px-2.5")

                # Main 2-Column Grid
                with ui.row().classes("w-full gap-5 items-start"):
                    # Left Column (70%) - Content, Timeline, Comments
                    with ui.column().classes("flex-[3] min-w-[340px] gap-4"):
                        # Description Card
                        with ui.card().classes("w-full p-5 rounded-xl bg-white border border-slate-200 shadow-sm"):
                            with ui.row().classes("items-center gap-2 mb-2"):
                                ui.label(category_label).classes("text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 uppercase")
                                ui.label(t("detail_created_at", time=format_datetime(ticket.get('created_at')))).classes("text-xs text-slate-400")

                            ui.label(ticket_title).classes("text-base font-bold text-slate-900 mb-2 leading-snug")
                            ui.label(t("tb_description_title")).classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1")
                            ui.label(ticket_desc).classes("text-xs text-slate-700 whitespace-pre-wrap leading-relaxed bg-slate-50/70 p-3 rounded-lg border border-slate-100")

                        # Timeline Stepper Card
                        with ui.card().classes("w-full p-5 rounded-xl bg-white border border-slate-200 shadow-sm"):
                            with ui.row().classes("w-full justify-between items-center mb-3 pb-2 border-b border-slate-100"):
                                ui.label(t("detail_timeline_title")).classes("text-sm font-bold text-slate-900")
                                ui.label(t("detail_events_count", count=len(history))).classes("text-xs text-slate-400")
                            audit_timeline(history)

                        # Comments Thread
                        comments_thread(ticket_id, user)

                    # Right Column (30%) - Metadata & Quick Actions
                    with ui.column().classes("flex-1 min-w-[280px] gap-4"):
                        # Quick Action Card (Only for ADMIN & TECHNICIAN)
                        if role in ("ADMIN", "TECHNICIAN"):
                            with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-sm"):
                                ui.label(t("detail_actions_title")).classes("text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 pb-1 border-b border-slate-100")

                                async def do_update_status(target_s: str) -> None:
                                    try:
                                        await ticket_service.update_status(ticket_id, target_s)
                                        toast.success(f"{get_status_label(target_s)}")
                                        await load_detail()
                                    except Exception as exc:
                                        toast.error(str(exc))

                                async def do_claim_ticket() -> None:
                                    try:
                                        await ticket_service.assign_ticket(ticket_id, int(user_id))
                                        toast.success("Success!")
                                        await load_detail()
                                    except Exception as exc:
                                        toast.error(f"Error: {exc}")

                                async def open_close_modal() -> None:
                                    dialog = ui.dialog()
                                    with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-6 bg-white gap-3"):
                                        ui.label(f"{t('btn_close_ticket')} #{ticket_id}").classes("text-base font-bold text-slate-900")
                                        ui.label(t("detail_closed_text")).classes("text-xs text-slate-500 mb-1")
                                        note_input = ui.textarea(placeholder="...").props("outlined rows=3").classes("w-full")

                                        async def do_close() -> None:
                                            try:
                                                await ticket_service.close_ticket(ticket_id, note_input.value or None)
                                                toast.success("Closed successfully.")
                                                dialog.close()
                                                await load_detail()
                                            except Exception as exc:
                                                toast.error(str(exc))

                                        with ui.row().classes("w-full justify-end gap-2 mt-4 pt-3 border-t border-slate-100"):
                                            ui.button(t("btn_cancel"), on_click=dialog.close).props("flat color=slate-600")
                                            ui.button(t("btn_confirm"), icon="lock", on_click=do_close).props("color=primary unelevated")
                                    dialog.open()

                                async def open_assign_modal() -> None:
                                    dialog = ui.dialog()
                                    with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-6 bg-white gap-3"):
                                        ui.label(f"{t('detail_btn_assign')} #{ticket_id}").classes("text-base font-bold text-slate-900")
                                        tech_select = ui.select({}, label="Technician").props("outlined").classes("w-full")

                                        try:
                                            techs = await user_service.list_technicians()
                                            tech_select.options = {tech["id"]: f"{tech['ho_ten']} (@{tech['username']})" for tech in techs}
                                            tech_select.update()
                                        except Exception as exc:
                                            toast.error(str(exc))

                                        async def do_assign() -> None:
                                            if not tech_select.value:
                                                toast.warning("Select a technician.")
                                                return
                                            try:
                                                await ticket_service.assign_ticket(ticket_id, int(tech_select.value))
                                                toast.success("Assigned successfully.")
                                                dialog.close()
                                                await load_detail()
                                            except Exception as exc:
                                                toast.error(str(exc))

                                        with ui.row().classes("w-full justify-end gap-2 mt-4 pt-3 border-t border-slate-100"):
                                            ui.button(t("btn_cancel"), on_click=dialog.close).props("flat color=slate-600")
                                            ui.button(t("btn_save"), on_click=do_assign).props("color=primary unelevated")
                                    dialog.open()

                                # Workflow Actions according to State & Role
                                if cur_status == "OPEN":
                                    if is_technician:
                                        ui.button(t("detail_btn_claim"), icon="bolt", on_click=do_claim_ticket).props("unelevated color=primary").classes("w-full justify-start py-2 text-xs font-bold")
                                    if can_assign:
                                        ui.button(t("detail_btn_assign"), icon="person_add", on_click=open_assign_modal).props("unelevated color=primary").classes("w-full justify-start py-2 text-xs font-bold")
                                elif cur_status == "ASSIGNED":
                                    ui.button(t("detail_btn_start"), icon="play_arrow", on_click=lambda: do_update_status("IN_PROGRESS")).props("unelevated color=amber-700").classes("w-full justify-start py-2 text-xs font-bold")
                                    if can_assign:
                                        ui.button(t("detail_btn_change_tech"), icon="swap_horiz", on_click=open_assign_modal).props("outline color=slate-700").classes("w-full justify-start py-1.5 text-xs font-semibold mt-2")
                                elif cur_status == "IN_PROGRESS":
                                    ui.button(t("detail_btn_resolve"), icon="check_circle", on_click=lambda: do_update_status("RESOLVED")).props("unelevated color=emerald-700").classes("w-full justify-start py-2 text-xs font-bold")
                                elif cur_status == "RESOLVED":
                                    ui.button(t("detail_btn_close"), icon="lock", on_click=open_close_modal).props("unelevated color=slate-800").classes("w-full justify-start py-2 text-xs font-bold")
                                else:
                                    with ui.row().classes("items-center gap-1.5 text-slate-500 text-xs py-2"):
                                        ui.icon("lock").classes("text-sm")
                                        ui.label(t("detail_closed_text"))
                        else:
                            # Informative card for USER
                            with ui.card().classes("w-full p-4 rounded-xl bg-blue-50/60 border border-blue-100 shadow-sm gap-2"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("forum").classes("text-blue-600 text-lg")
                                    ui.label(t("detail_feedback_card_title")).classes("text-xs font-bold text-blue-900 uppercase tracking-wider")
                                ui.label(t("detail_feedback_card_sub")).classes("text-xs text-blue-700 leading-relaxed")

                        # Meta Details Card
                        with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-sm"):
                            ui.label(t("detail_info_card_title")).classes("text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 pb-1 border-b border-slate-100")

                            # Creator info
                            user_info = ticket.get("user") or {}
                            ui.label(t("detail_creator")).classes("text-[10px] font-bold text-slate-400 uppercase")
                            ui.label(user_info.get("ho_ten") or t("user_label", id=ticket.get('user_id'))).classes("text-sm font-bold text-slate-800 mb-2")

                            # Technician info
                            tech_info = ticket.get("technician") or {}
                            ui.label(t("detail_tech_assigned")).classes("text-[10px] font-bold text-slate-400 uppercase")
                            tech_name = tech_info.get("ho_ten") or (f"Tech #{assigned_tech_id}" if assigned_tech_id else t("detail_unassigned_tech"))
                            ui.label(tech_name).classes(f"text-sm font-bold {'text-blue-700' if assigned_tech_id else 'text-amber-700'} mb-2")

                            # Device info
                            device_info = ticket.get("device") or {}
                            ui.label(t("detail_device_linked")).classes("text-[10px] font-bold text-slate-400 uppercase")
                            if device_info.get("ten_thiet_bi") or device_info.get("ma_thiet_bi"):
                                with ui.card().classes("w-full p-2.5 rounded-lg bg-slate-50 border border-slate-100 shadow-none mb-2"):
                                    ui.label(f"{device_info.get('ma_thiet_bi', '')} · {device_info.get('ten_thiet_bi', '')}").classes("text-xs font-bold text-blue-700")
                                    ui.label(f"{t('tb_device_location')}: {device_info.get('vi_tri') or t('detail_unknown_location')}").classes("text-[11px] text-slate-500")
                            else:
                                ui.label(t("detail_no_device")).classes("text-xs text-slate-500 mb-2")

                            ui.separator().classes("my-2")
                            ui.label(t("detail_created_at", time=format_datetime(ticket.get('created_at')))).classes("text-[11px] text-slate-400")
                            ui.label(t("detail_updated_at", time=format_datetime(ticket.get('updated_at')))).classes("text-[11px] text-slate-400")

        ui.timer(0.1, load_detail, once=True)

    app_shell(t("detail_title", id=ticket_id), content)
