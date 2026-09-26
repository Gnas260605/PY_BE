from __future__ import annotations

from typing import Any

from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.loading import loading_spinner
from common.formatters import format_datetime
from services.log_analytics_service import log_analytics_service


ARTIFACT_LABELS = {
    "logs_csv": "Parsed logs CSV",
    "parser_stats": "Parser stats JSON",
    "summary_csv": "Summary CSV",
    "security_csv": "Security events CSV",
    "report_txt": "Text report",
}


def render_log_analytics_view() -> None:
    def content(user: dict) -> None:
        if user.get("vai_tro") != "ADMIN":
            ui.label("Bạn không có quyền xem Log Analytics.").classes("text-red-600 font-bold p-6")
            return

        state: dict[str, Any] = {"summary": None, "loading": True, "error": None}

        with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200 mb-2.5 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 font-medium"):
                    ui.label("Trang chủ")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Quản trị tài nguyên")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Log Analytics").classes("text-slate-900 font-semibold")
                ui.label("Perl Log Analytics").classes("text-xl font-bold text-slate-900 tracking-tight")
                ui.label("Theo dõi kết quả parser/analyzer Perl từ structured log của backend.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                ui.button("Tải lại", icon="refresh", on_click=lambda: refresh()).props(
                    "outline color=slate-700 dense size=sm"
                ).classes("h-9 px-3.5 text-xs font-semibold rounded-lg bg-white border border-slate-300 shadow-2xs hover:bg-slate-50")
                ui.button("Tải report", icon="article", on_click=lambda: download_artifact("report_txt")).props(
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
                                ui.label("Artifact trạng thái sẵn sàng" if generated else "Chưa có report runtime").classes("text-sm font-bold text-slate-900")
                                ui.label(f"Nguồn log mẫu: {summary.get('source_log') or '-'} · Cập nhật: {format_datetime(summary.get('generated_at'))}").classes("text-xs text-slate-500")
                        with ui.row().classes("items-center gap-2"):
                            for artifact in artifacts:
                                if artifact.get("exists"):
                                    ui.button(
                                        artifact.get("label") or ARTIFACT_LABELS.get(artifact.get("key"), artifact.get("key")),
                                        icon="download",
                                        on_click=lambda key=artifact.get("key"): download_artifact(key),
                                    ).props("outline dense size=sm color=slate-700").classes("text-xs")

        def render_summary(summary: dict[str, Any]) -> None:
            kpi_container.clear()
            with kpi_container:
                render_kpi("Parsed logs", summary.get("total_logs", 0), "Dòng log hợp lệ", "segment", "blue")
                render_kpi("Malformed", summary.get("malformed"), "Dòng sai contract", "report_problem", "amber")
                render_kpi("Unknown event", summary.get("unknown_event"), "Event chưa map", "help", "rose")
                render_kpi("Continuation", summary.get("continuation_lines"), "Traceback lines", "subject", "emerald")

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
                        ui.label("Top events").classes("text-sm font-bold text-slate-900")
                        ui.label("Tính từ parsed logs CSV hoặc summary CSV.").classes("text-[11px] text-slate-500")
                if not events:
                    empty_state("Chưa có event", "Hãy sinh report Perl để xem phân bố event.", "analytics")
                else:
                    with ui.column().classes("w-full divide-y divide-slate-100"):
                        max_count = max((item.get("count", 0) for item in events), default=1)
                        for item in events:
                            count = int(item.get("count") or 0)
                            width = max(4, int((count / max_count) * 100))
                            with ui.column().classes("w-full gap-1 p-3"):
                                with ui.row().classes("w-full justify-between items-center"):
                                    ui.label(item.get("event") or "-").classes("text-xs font-bold text-slate-800")
                                    ui.label(str(count)).classes("text-xs font-bold text-slate-500")
                                with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-100 overflow-hidden"):
                                    ui.element("div").classes("h-full rounded-full bg-blue-500").style(f"width: {width}%")

        def render_security_events(summary: dict[str, Any]) -> None:
            events = summary.get("security_events") or []
            with ui.element("div").classes("rounded-lg bg-white border border-slate-200 shadow-2xs overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center p-3 border-b border-slate-100"):
                    with ui.column().classes("gap-0"):
                        ui.label("Security alerts").classes("text-sm font-bold text-slate-900")
                        ui.label("Các cảnh báo brute-force hoặc bất thường từ Perl analyzer.").classes("text-[11px] text-slate-500")
                    ui.label(f"{len(events)} alerts").classes("text-[11px] font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-100")
                if not events:
                    empty_state("Không có cảnh báo", "Analyzer chưa phát hiện brute-force trong artifact hiện tại.", "verified")
                else:
                    with ui.column().classes("w-full divide-y divide-slate-100 max-h-80 overflow-y-auto"):
                        for event in events:
                            with ui.row().classes("w-full items-start gap-3 p-3 no-wrap"):
                                with ui.element("div").classes("w-9 h-9 rounded-lg bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600 shrink-0"):
                                    ui.icon("shield").classes("text-lg")
                                with ui.column().classes("gap-0.5 min-w-0"):
                                    ui.label(f"{event.get('event') or '-'} · {event.get('username') or 'unknown'}").classes("text-xs font-bold text-slate-800")
                                    ui.label(event.get("reason") or "-").classes("text-[11px] text-slate-500")
                                    ui.label(event.get("timestamp") or "-").classes("text-[10px] text-slate-400 font-mono")

        def render_report_excerpt(summary: dict[str, Any]) -> None:
            excerpt = summary.get("report_excerpt") or ""
            with ui.element("div").classes("w-full rounded-lg bg-white border border-slate-200 shadow-2xs overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center p-3 border-b border-slate-100"):
                    with ui.column().classes("gap-0"):
                        ui.label("Console report preview").classes("text-sm font-bold text-slate-900")
                        ui.label("Nội dung rút gọn từ `perl/reports/report.txt`.").classes("text-[11px] text-slate-500")
                if not excerpt:
                    empty_state("Chưa có report.txt", "Chạy generator Perl để sinh báo cáo text.", "article")
                else:
                    ui.markdown(f"```text\n{excerpt}\n```").classes("w-full text-xs p-3 bg-slate-950 text-slate-100 overflow-x-auto")

        async def refresh() -> None:
            state["loading"] = True
            content_container.clear()
            with content_container:
                loading_spinner("Đang tải Perl log analytics...")
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
                    ui.label(f"Lỗi tải Log Analytics: {exc}").classes("text-sm text-red-600")
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
                toast.success("Đã tải artifact Log Analytics.")
            except Exception as exc:
                toast.show_popup("Lỗi tải artifact", "Không thể tải file Log Analytics từ máy chủ.", type="error", detail=str(exc))

        ui.timer(0.1, refresh, once=True)

    app_shell("Log Analytics", content)
