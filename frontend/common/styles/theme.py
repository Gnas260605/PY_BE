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
        info="#3b82f6",
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
          /* Compact top layout overrides */
          .nicegui-content {
            padding: 0 !important;
          }
          .q-header {
            min-height: 48px !important;
            height: 48px !important;
            display: flex !important;
            align-items: center !important;
          }
          .q-page-container {
            padding-top: 48px !important;
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
          /* Card hover */
          .card-hover {
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          }
          .card-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px -6px rgba(15, 23, 42, 0.07);
          }
          /* Quasar component refinements */
          .q-field--outlined .q-field__control {
            border-radius: 10px !important;
            background: #ffffff;
            transition: border-color 0.2s ease;
          }
          .q-field--outlined.q-field--focused .q-field__control {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
          }
          .q-field--dense .q-field__control, .q-field--dense .q-field__marginal {
            height: 38px !important;
          }
          .q-btn {
            border-radius: 10px !important;
            font-weight: 600 !important;
            text-transform: none !important;
            letter-spacing: 0.01em !important;
          }
          /* Sleek Quasar table styling */
          .q-table__container {
            background-color: #ffffff !important;
            border-radius: 14px !important;
            box-shadow: none !important;
          }
          .q-table th {
            font-size: 11px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
            color: #64748b !important;
            background-color: #f8fafc !important;
            padding: 8px 14px !important;
            border-bottom: 1px solid #e2e8f0 !important;
            height: 38px !important;
          }
          .q-table td {
            font-size: 12px !important;
            color: #1e293b !important;
            padding: 8px 14px !important;
            border-bottom: 1px solid #f1f5f9 !important;
            height: 42px !important;
          }
          .q-table tbody tr:hover {
            background-color: #f8fafc !important;
          }
          .q-table__bottom {
            font-size: 12px !important;
            color: #64748b !important;
            padding: 6px 14px !important;
            border-top: 1px solid #e2e8f0 !important;
          }
          /* Interactive selection cards */
          .select-card {
            border: 1.5px solid #e2e8f0;
            border-radius: 14px;
            padding: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            background-color: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            width: 100%;
          }
          .select-card:hover {
            border-color: #93c5fd;
            background-color: #f8fafc;
          }
          .select-card.active-blue {
            border-color: #2563eb !important;
            background-color: #eff6ff !important;
            box-shadow: 0 0 0 1px #2563eb !important;
          }
          .select-card.active-red {
            border-color: #ef4444 !important;
            background-color: #fef2f2 !important;
            box-shadow: 0 0 0 1px #ef4444 !important;
          }
          .select-card.active-amber {
            border-color: #f59e0b !important;
            background-color: #fffbeb !important;
            box-shadow: 0 0 0 1px #f59e0b !important;
          }
          /* Step circle */
          .step-circle {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background-color: #2563eb;
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 8px;
          }
          /* Dynamic animated login backdrop */
          .login-bg {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at 15% 15%, rgba(37, 99, 235, 0.28) 0%, transparent 42%),
                        radial-gradient(circle at 85% 85%, rgba(99, 102, 241, 0.25) 0%, transparent 45%),
                        radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.15) 0%, transparent 55%),
                        linear-gradient(135deg, #090e1a 0%, #0f172a 45%, #1e1b4b 100%);
            overflow: hidden;
            z-index: 10;
          }
          .login-grid-pattern {
            position: absolute;
            inset: 0;
            background-image: radial-gradient(rgba(255, 255, 255, 0.12) 1.2px, transparent 1.2px);
            background-size: 32px 32px;
            pointer-events: none;
          }
          .login-card-glass {
            background: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.6);
            box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.3);
          }
          @keyframes floatSlow {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-12px) rotate(2deg); }
          }
          .floating-chip {
            animation: floatSlow 6s ease-in-out infinite;
          }
          .floating-chip-delayed {
            animation: floatSlow 8s ease-in-out infinite 2s;
          }
        </style>
        """
    )
