from __future__ import annotations

from typing import Any

from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.loading import loading_spinner
from common.formatters import format_datetime
from core.i18n import get_lang
from services.log_analytics_service import log_analytics_service


TEXT = {
    "vi": {
        "forbidden": "Bạn không có quyền xem Log Analytics.",
        "home": "Trang chủ",
        "admin_section": "Quản trị tài nguyên",
        "title": "Phân tích log Perl",
        "subtitle": "Theo dõi kết quả parser/analyzer Perl từ structured log của backend.",
        "refresh": "Tải lại",
        "download_report": "Tải báo cáo",
        "parsed_logs": "Log đã phân tích",
        "parsed_logs_sub": "Dòng log hợp lệ",
        "malformed": "Sai định dạng",
        "malformed_sub": "Dòng sai contract",
        "unknown_event": "Event chưa nhận diện",
        "unknown_event_sub": "Event chưa có trong danh sách",
        "continuation": "Dòng tiếp nối",
        "continuation_sub": "Dòng traceback/stack trace",
        "artifact_ready": "Artifact đã sẵn sàng",
        "artifact_missing": "Chưa có report runtime",
        "source": "Nguồn log mẫu",
        "updated": "Cập nhật",
        "top_events": "Event xuất hiện nhiều nhất",
        "top_events_sub": "Tính từ file CSV log đã parse hoặc file summary.",
        "no_events": "Chưa có event",
        "no_events_sub": "Hãy sinh report Perl để xem phân bố event.",
        "security_alerts": "Cảnh báo bảo mật",
        "security_alerts_sub": "Các cảnh báo brute-force hoặc bất thường từ Perl analyzer.",
        "alerts": "cảnh báo",
        "no_alerts": "Không có cảnh báo",
        "no_alerts_sub": "Analyzer chưa phát hiện brute-force trong artifact hiện tại.",
        "unknown_user": "không rõ user",
        "report_preview": "Xem nhanh báo cáo console",
        "report_preview_sub": "Nội dung rút gọn từ `perl/reports/report.txt`.",
        "no_report": "Chưa có report.txt",
        "no_report_sub": "Chạy generator Perl để sinh báo cáo text.",
        "loading": "Đang tải dữ liệu phân tích log Perl...",
        "load_error": "Lỗi tải Log Analytics",
        "download_ok": "Đã tải artifact Log Analytics.",
        "download_error_title": "Lỗi tải artifact",
        "download_error_msg": "Không thể tải file Log Analytics từ máy chủ.",
    },
    "en": {
        "forbidden": "You are not allowed to view Log Analytics.",
        "home": "Home",
        "admin_section": "Resource Administration",
        "title": "Perl Log Analytics",
        "subtitle": "Inspect Perl parser/analyzer results from backend structured logs.",
        "refresh": "Refresh",
        "download_report": "Download report",
        "parsed_logs": "Parsed logs",
        "parsed_logs_sub": "Valid log lines",
        "malformed": "Malformed",
        "malformed_sub": "Contract violations",
        "unknown_event": "Unknown events",
        "unknown_event_sub": "Events not yet mapped",
        "continuation": "Continuation",
        "continuation_sub": "Traceback/stack-trace lines",
        "artifact_ready": "Artifacts are ready",
        "artifact_missing": "No runtime report yet",
        "source": "Sample log source",
        "updated": "Updated",
        "top_events": "Top events",
        "top_events_sub": "Calculated from parsed logs CSV or summary CSV.",
        "no_events": "No events yet",
        "no_events_sub": "Generate the Perl report to inspect event distribution.",
        "security_alerts": "Security alerts",
        "security_alerts_sub": "Brute-force or anomaly alerts detected by the Perl analyzer.",
        "alerts": "alerts",
        "no_alerts": "No alerts",
        "no_alerts_sub": "The analyzer has not detected brute-force activity in the current artifact.",
        "unknown_user": "unknown user",
        "report_preview": "Console report preview",
        "report_preview_sub": "Short excerpt from `perl/reports/report.txt`.",
        "no_report": "No report.txt yet",
        "no_report_sub": "Run the Perl generator to create a text report.",
        "loading": "Loading Perl log analytics...",
        "load_error": "Failed to load Log Analytics",
        "download_ok": "Log Analytics artifact downloaded.",
        "download_error_title": "Artifact download failed",
        "download_error_msg": "Unable to download the Log Analytics file from the server.",
    },
}

ARTIFACT_LABELS = {
    "vi": {
        "logs_csv": "CSV log đã parse",
        "parser_stats": "JSON thống kê parser",
        "summary_csv": "CSV tổng hợp",
        "security_csv": "CSV cảnh báo bảo mật",
        "report_txt": "Báo cáo text",
    },
    "en": {
        "logs_csv": "Parsed logs CSV",
        "parser_stats": "Parser stats JSON",
        "summary_csv": "Summary CSV",
        "security_csv": "Security events CSV",
        "report_txt": "Text report",
    },
}

EVENT_LABELS = {
    "vi": {
        "LOGIN_FAILED": "Đăng nhập thất bại",
        "LOGIN_SUCCESS": "Đăng nhập thành công",
        "USER_CREATED": "Tạo người dùng",
        "DEVICE_CREATED": "Tạo thiết bị",
        "TICKET_CREATED": "Tạo ticket",
        "TICKET_STATUS_CHANGED": "Đổi trạng thái ticket",
        "UNHANDLED_EXCEPTION": "Lỗi hệ thống chưa xử lý",
        "POSSIBLE_BRUTE_FORCE": "Nghi vấn brute-force",
    },
    "en": {
        "LOGIN_FAILED": "Login failed",
        "LOGIN_SUCCESS": "Login succeeded",
        "USER_CREATED": "User created",
        "DEVICE_CREATED": "Device created",
        "TICKET_CREATED": "Ticket created",
        "TICKET_STATUS_CHANGED": "Ticket status changed",
        "UNHANDLED_EXCEPTION": "Unhandled exception",
        "POSSIBLE_BRUTE_FORCE": "Possible brute-force",
    },
}


def _lang() -> str:
    return "en" if get_lang() == "en" else "vi"


def _txt(key: str) -> str:
    lang = _lang()
    return TEXT[lang].get(key) or TEXT["vi"].get(key) or key


def _artifact_label(key: str | None) -> str:
    lang = _lang()
    if not key:
        return "-"
    return ARTIFACT_LABELS[lang].get(key) or ARTIFACT_LABELS["vi"].get(key) or key


def _event_label(event: str | None) -> str:
    lang = _lang()
    if not event:
        return "-"
    label = EVENT_LABELS[lang].get(event) or EVENT_LABELS["vi"].get(event)
    return f"{label} ({event})" if label else event


def _reason_text(reason: str | None) -> str:
    if not reason:
        return "-"
    if reason.endswith("_or_more_login_failed_within_60_seconds"):
        threshold = reason.split("_", 1)[0]
        if _lang() == "en":
            return f"Detected at least {threshold} failed login attempts within 60 seconds."
        return f"Phát hiện ít nhất {threshold} lần đăng nhập thất bại trong 60 giây."
    return reason.replace("_", " ")


def render_log_analytics_view() -> None:
    def content(user: dict) -> None:
        if user.get("vai_tro") != "ADMIN":
            ui.label(_txt("forbidden")).classes("text-red-600 font-bold p-6")
            return

        state: dict[str, Any] = {"summary": None, "loading": True, "error": None}

        with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200 mb-2.5 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 font-medium"):
                    ui.label(_txt("home"))
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label(_txt("admin_section"))
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Log Analytics").classes("text-slate-900 font-semibold")
                ui.label(_txt("title")).classes("text-xl font-bold text-slate-900 tracking-tight")
                ui.label(_txt("subtitle")).classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                ui.button(_txt("refresh"), icon="refresh", on_click=lambda: refresh()).props(
                    "outline color=slate-700 dense size=sm"
                ).classes("h-9 px-3.5 text-xs font-semibold rounded-lg bg-white border border-slate-300 shadow-2xs hover:bg-slate-50")
                ui.button(_txt("download_report"), icon="article", on_click=lambda: download_artifact("report_txt")).props(
                    "color=primary unelevated dense size=sm"
                ).classes("h-9 px-4 text-xs font-bold rounded-lg shadow-2xs")

        kpi_container = ui.element("div").classes("w-full grid grid-cols-2 lg:grid-cols-4 gap-2.5 mb-3")
        status_container = ui.column().classes("w-full mb-3")
        content_container = ui.column().classes("w-full gap-3")

        def render_kpi(title: str, value: Any, subtitle: str, icon: str, tone: str = "blue") -> None:
            tone_map = {
                "blue": "bg-blue-50 text-blue-700 border-blue-100",
                "emerald": "bg-emerald-50 text-emerald-700 border-emerald-100",
                "amber": "bg-amber-50 text-amber-800 border-amber-100",
                "rose": "bg-rose-50 text-rose-700 border-rose-100",
            }
            with ui.element("div").classes("rounded-lg bg-white border border-slate-200 shadow-2xs p-3 min-h-[88px]"):
                with ui.row().classes("w-full justify-between items-start no-wrap"):
                    with ui.column().classes("gap-1 min-w-0"):
                        ui.label(title).classes("text-[10px] font-bold tracking-wider text-slate-400 uppercase")
                        ui.label(str(value if value is not None else "N/A")).classes("text-2xl font-bold text-slate-900 leading-none")
                        ui.label(subtitle).classes("text-[11px] text-slate-500")
                    with ui.element("div").classes(f"w-9 h-9 rounded-lg border flex items-center justify-center shrink-0 {tone_map.get(tone, tone_map['blue'])}"):
                        ui.icon(icon).classes("text-lg")

        def render_status(summary: dict[str, Any]) -> None:
            status_container.clear()
            artifacts = summary.get("artifacts") or []
            generated = summary.get("generated")
            with status_container:
                with ui.element("div").classes("w-full rounded-lg bg-white border border-slate-200 shadow-2xs p-3"):
                    with ui.row().classes("w-full justify-between items-center gap-3 flex-wrap"):
                        with ui.row().classes("items-center gap-3"):
                            status_icon = "check_circle" if generated else "info"
                            status_class = "text-emerald-600 bg-emerald-50 border-emerald-100" if generated else "text-amber-700 bg-amber-50 border-amber-100"
                            with ui.element("div").classes(f"w-10 h-10 rounded-lg border flex items-center justify-center {status_class}"):
                                ui.icon(status_icon).classes("text-xl")
                            with ui.column().classes("gap-0.5"):
                                ui.label(_txt("artifact_ready") if generated else _txt("artifact_missing")).classes("text-sm font-bold text-slate-900")
                                ui.label(f"{_txt('source')}: {summary.get('source_log') or '-'} · {_txt('updated')}: {format_datetime(summary.get('generated_at'))}").classes("text-xs text-slate-500")
                        with ui.row().classes("items-center gap-2"):
                            for artifact in artifacts:
                                if artifact.get("exists"):
                                    ui.button(
                                        _artifact_label(artifact.get("key")),
                                        icon="download",
                                        on_click=lambda key=artifact.get("key"): download_artifact(key),
                                    ).props("outline dense size=sm color=slate-700").classes("text-xs")

        def render_summary(summary: dict[str, Any]) -> None:
            kpi_container.clear()
            with kpi_container:
                render_kpi(_txt("parsed_logs"), summary.get("total_logs", 0), _txt("parsed_logs_sub"), "segment", "blue")
                render_kpi(_txt("malformed"), summary.get("malformed"), _txt("malformed_sub"), "report_problem", "amber")
                render_kpi(_txt("unknown_event"), summary.get("unknown_event"), _txt("unknown_event_sub"), "help", "rose")
                render_kpi(_txt("continuation"), summary.get("continuation_lines"), _txt("continuation_sub"), "subject", "emerald")

            render_status(summary)
            content_container.clear()
            with content_container:
                with ui.element("div").classes("w-full grid grid-cols-1 xl:grid-cols-2 gap-3"):
                    render_top_events(summary)
                    render_security_events(summary)
                render_report_excerpt(summary)

        def render_top_events(summary: dict[str, Any]) -> None:
            events = summary.get("top_events") or []
            with ui.element("div").classes("rounded-lg bg-white border border-slate-200 shadow-2xs overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center p-3 border-b border-slate-100"):
                    with ui.column().classes("gap-0"):
                        ui.label(_txt("top_events")).classes("text-sm font-bold text-slate-900")
                        ui.label(_txt("top_events_sub")).classes("text-[11px] text-slate-500")
                if not events:
                    empty_state(_txt("no_events"), _txt("no_events_sub"), "analytics")
                else:
                    with ui.column().classes("w-full divide-y divide-slate-100"):
                        max_count = max((item.get("count", 0) for item in events), default=1)
                        for item in events:
                            count = int(item.get("count") or 0)
                            width = max(4, int((count / max_count) * 100))
                            with ui.column().classes("w-full gap-1 p-3"):
                                with ui.row().classes("w-full justify-between items-center"):
                                    ui.label(_event_label(item.get("event"))).classes("text-xs font-bold text-slate-800")
                                    ui.label(str(count)).classes("text-xs font-bold text-slate-500")
                                with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-100 overflow-hidden"):
                                    ui.element("div").classes("h-full rounded-full bg-blue-500").style(f"width: {width}%")

        def render_security_events(summary: dict[str, Any]) -> None:
            events = summary.get("security_events") or []
            with ui.element("div").classes("rounded-lg bg-white border border-slate-200 shadow-2xs overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center p-3 border-b border-slate-100"):
                    with ui.column().classes("gap-0"):
                        ui.label(_txt("security_alerts")).classes("text-sm font-bold text-slate-900")
                        ui.label(_txt("security_alerts_sub")).classes("text-[11px] text-slate-500")
                    ui.label(f"{len(events)} {_txt('alerts')}").classes("text-[11px] font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-100")
                if not events:
                    empty_state(_txt("no_alerts"), _txt("no_alerts_sub"), "verified")
                else:
                    with ui.column().classes("w-full divide-y divide-slate-100 max-h-80 overflow-y-auto"):
                        for event in events:
                            with ui.row().classes("w-full items-start gap-3 p-3 no-wrap"):
                                with ui.element("div").classes("w-9 h-9 rounded-lg bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600 shrink-0"):
                                    ui.icon("shield").classes("text-lg")
                                with ui.column().classes("gap-0.5 min-w-0"):
                                    ui.label(f"{_event_label(event.get('event'))} · {event.get('username') or _txt('unknown_user')}").classes("text-xs font-bold text-slate-800")
                                    ui.label(_reason_text(event.get("reason"))).classes("text-[11px] text-slate-500")
                                    ui.label(event.get("timestamp") or "-").classes("text-[10px] text-slate-400 font-mono")

        def render_report_excerpt(summary: dict[str, Any]) -> None:
            excerpt = summary.get("report_excerpt") or ""
            with ui.element("div").classes("w-full rounded-lg bg-white border border-slate-200 shadow-2xs overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center p-3 border-b border-slate-100"):
                    with ui.column().classes("gap-0"):
                        ui.label(_txt("report_preview")).classes("text-sm font-bold text-slate-900")
                        ui.label(_txt("report_preview_sub")).classes("text-[11px] text-slate-500")
                if not excerpt:
                    empty_state(_txt("no_report"), _txt("no_report_sub"), "article")
                else:
                    ui.markdown(f"```text\n{excerpt}\n```").classes("w-full text-xs p-3 bg-slate-950 text-slate-100 overflow-x-auto")

        async def refresh() -> None:
            state["loading"] = True
            content_container.clear()
            with content_container:
                loading_spinner(_txt("loading"))
            try:
                state["summary"] = await log_analytics_service.get_summary()
                state["error"] = None
                render_summary(state["summary"])
            except Exception as exc:
                state["error"] = str(exc)
                kpi_container.clear()
                status_container.clear()
                content_container.clear()
                with content_container:
                    ui.label(f"{_txt('load_error')}: {exc}").classes("text-sm text-red-600")
            finally:
                state["loading"] = False

        async def download_artifact(key: str | None) -> None:
            if not key:
                return
            try:
                payload = await log_analytics_service.download_artifact(key)
                filename = {
                    "logs_csv": "perl_logs.csv",
                    "parser_stats": "perl_parser_stats.json",
                    "summary_csv": "perl_summary.csv",
                    "security_csv": "perl_security_events.csv",
                    "report_txt": "perl_report.txt",
                }.get(key, f"{key}.txt")
                ui.download(payload, filename)
                toast.success(_txt("download_ok"))
            except Exception as exc:
                toast.show_popup(_txt("download_error_title"), _txt("download_error_msg"), type="error", detail=str(exc))

        ui.timer(0.1, refresh, once=True)

    app_shell("Log Analytics", content)
