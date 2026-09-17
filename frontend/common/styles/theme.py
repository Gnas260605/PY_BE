from nicegui import ui

PRIMARY = "#2563eb"
SURFACE = "#ffffff"
BACKGROUND = "#f8fafc"
TEXT = "#0f172a"


def apply_theme() -> None:
    ui.colors(
        primary=PRIMARY,
        secondary="#64748b",
        accent="#0ea5e9",
        positive="#10b981",
        negative="#ef4444",
        info="#6366f1",
        warning="#f59e0b",
    )
    ui.add_head_html(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
        <style>
          body, input, button, textarea, select, .q-btn, .q-field, .q-table, .q-item, div, span, p, h1, h2, h3, h4, h5, h6 {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          }
          .material-icons, .material-icons-outlined, .material-symbols-outlined, .q-icon {
            font-family: 'Material Icons' !important;
            font-weight: normal;
            font-style: normal;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-smoothing: antialiased;
          }
          body {
            background-color: #f8fafc;
            color: #0f172a;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
          /* Custom sleek scrollbar */
          ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
          }
          ::-webkit-scrollbar-track {
            background: #f1f5f9;
          }
          ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 9999px;
          }
          ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
          }
          /* Card Hover */
          .card-hover {
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          }
          .card-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.06);
            border-color: #cbd5e1 !important;
          }
          /* Quasar component refinements */
          .q-field--outlined .q-field__control {
            border-radius: 10px !important;
            background: #ffffff;
            border-color: #e2e8f0 !important;
            transition: all 0.15s ease;
          }
          .q-field--outlined.q-field--focused .q-field__control {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
          }
          .q-btn {
            border-radius: 8px !important;
            font-weight: 600 !important;
            text-transform: none !important;
            letter-spacing: 0.01em !important;
            transition: all 0.15s ease;
          }
          .q-table__card {
            border-radius: 12px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03) !important;
            background-color: #ffffff !important;
          }
          .q-table th {
            font-weight: 700 !important;
            color: #475569 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            background-color: #f8fafc !important;
            padding: 12px 16px !important;
            border-bottom: 1px solid #e2e8f0 !important;
          }
          .q-table td {
            font-size: 0.875rem !important;
            padding: 14px 16px !important;
            color: #1e293b !important;
            border-bottom: 1px solid #f1f5f9 !important;
          }
          .q-table tbody tr:hover {
            background-color: #f8fafc !important;
          }
          .line-clamp-1 {
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .line-clamp-2 {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .desktop-table-view {
            display: block !important;
            width: 100%;
          }
          .mobile-card-view {
            display: none !important;
            width: 100%;
          }
          @media (max-width: 768px) {
            .desktop-table-view {
              display: none !important;
            }
            .mobile-card-view {
              display: flex !important;
            }
          }
        </style>
        """
    )
