from nicegui import ui


PRIMARY = "#2563eb"
SURFACE = "#ffffff"
BACKGROUND = "#f8fafc"
TEXT = "#0f172a"


def apply_theme() -> None:
    ui.colors(primary=PRIMARY, secondary="#475569", accent="#0ea5e9")
    ui.add_head_html(
        """
        <style>
          body { background: #f8fafc; color: #0f172a; }
          .glass-card { background: rgba(255,255,255,.92); backdrop-filter: blur(12px); }
          .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        </style>
        """
    )
