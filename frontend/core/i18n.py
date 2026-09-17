from __future__ import annotations

from typing import Any
from nicegui import app

DICTIONARY: dict[str, dict[str, str]] = {
    "vi": {
        # Navigation & Shell
        "nav_dashboard": "Dashboard",
        "nav_tech_workspace": "Bàn làm việc KTV",
        "nav_dispatch": "Giám sát sự cố",
        "nav_devices": "Danh mục thiết bị",
        "nav_users": "Quản lý người dùng",
        "nav_my_tickets": "Yêu cầu của tôi",
        "nav_create_ticket": "Tạo yêu cầu hỗ trợ",
        "nav_device_lookup": "Tra cứu thiết bị",
        "nav_settings": "Cài đặt cá nhân",
        "nav_logout": "Đăng xuất",
        "sec_overview": "TỔNG QUAN",
        "sec_admin": "QUẢN TRỊ TÀI NGUYÊN",
        "sec_tech": "BÀN LÀM VIỆC",
        "sec_tools": "CÔNG CỤ & CÀI ĐẶT",
        "sec_user_service": "HỖ TRỢ DỊCH VỤ",
        "sec_quick_tools": "TIỆN ÍCH & CÀI ĐẶT",

        # Statuses
        "status_OPEN": "Chờ tiếp nhận",
        "status_ASSIGNED": "Đã phân công",
        "status_IN_PROGRESS": "Đang xử lý",
        "status_RESOLVED": "Đã giải quyết",
        "status_CLOSED": "Đã đóng hoàn tất",
        "status_ACTIVE": "Hoạt động",
        "status_MAINTENANCE": "Bảo trì",
        "status_BROKEN": "Bị hỏng",
        "status_INACTIVE": "Ngừng dùng",

        # Priorities
        "priority_LOW": "Thấp",
        "priority_MEDIUM": "Trung bình",
        "priority_HIGH": "Cao",
        "priority_URGENT": "Khẩn cấp",

        # Categories
        "category_INCIDENT": "Sự cố kỹ thuật",
        "category_SERVICE_REQUEST": "Yêu cầu dịch vụ",
        "category_MAINTENANCE": "Bảo trì định kỳ",

        # Roles
        "role_ADMIN": "Quản trị viên",
        "role_TECHNICIAN": "Kỹ thuật viên",
        "role_USER": "Người dùng",

        # Actions
        "action_CREATED": "Tạo mới sự cố",
        "action_ASSIGNED": "Phân công xử lý",
        "action_STATUS_CHANGED": "Cập nhật trạng thái",
        "action_RESOLVED": "Khắc phục sự cố",
        "action_CLOSED": "Đóng sự cố",
        "action_COMMENTED": "Thêm trao đổi",
        "action_UPDATED": "Cập nhật thông tin",
        "action_REOPENED": "Mở lại sự cố",

        # Common UI Terms
        "btn_refresh": "Tải lại",
        "btn_save": "Lưu",
        "btn_cancel": "Hủy",
        "btn_confirm": "Xác nhận",
        "btn_search": "Tìm kiếm",
        "btn_claim": "Tiếp nhận sự cố",
        "btn_start_work": "Bắt đầu xử lý",
        "btn_mark_resolved": "Đánh dấu đã xử lý",
        "btn_close_ticket": "Đóng sự cố",
        "btn_send_comment": "Gửi tin nhắn",
        "btn_create_ticket": "Gửi yêu cầu hỗ trợ",
        "btn_all_tickets": "Xem tất cả",
        
        # Dashboard & Workspace
        "tech_dash_title": "Xin chào, {name}",
        "tech_dash_sub": "Đây là các công việc cần bạn xử lý hôm nay.",
        "kpi_my_active": "VIỆC CẦN XỬ LÝ",
        "kpi_my_in_progress": "ĐANG XỬ LÝ",
        "kpi_urgent": "CẦN ƯU TIÊN",
        "kpi_resolved": "ĐÃ GIẢI QUYẾT",
        "sec_work_queue": "Công việc cần xử lý",
        "sec_urgent_attention": "CẦN CHÚ Ý",
        "sec_progress": "TIẾN ĐỘ CÔNG VIỆC",
        "sec_quick_actions": "THAO TÁC NHANH",
        "sec_recent_updates": "Cập nhật gần đây",
        "no_urgent_tickets": "Không có sự cố khẩn cấp tồn đọng.",
        "all_work_done": "Tuyệt vời! Bạn không còn sự cố nào tồn đọng.",
    },
    "en": {
        # Navigation & Shell
        "nav_dashboard": "Dashboard",
        "nav_tech_workspace": "Tech Workspace",
        "nav_dispatch": "Ticket Monitoring",
        "nav_devices": "Device Inventory",
        "nav_users": "User Management",
        "nav_my_tickets": "My Tickets",
        "nav_create_ticket": "Create Ticket",
        "nav_device_lookup": "Device Lookup",
        "nav_settings": "User Settings",
        "nav_logout": "Logout",
        "sec_overview": "OVERVIEW",
        "sec_admin": "ADMINISTRATION",
        "sec_tech": "WORKSPACE",
        "sec_tools": "TOOLS & SETTINGS",
        "sec_user_service": "SERVICE DESK",
        "sec_quick_tools": "QUICK UTILITIES",

        # Statuses
        "status_OPEN": "Open",
        "status_ASSIGNED": "Assigned",
        "status_IN_PROGRESS": "In Progress",
        "status_RESOLVED": "Resolved",
        "status_CLOSED": "Closed",
        "status_ACTIVE": "Active",
        "status_MAINTENANCE": "Maintenance",
        "status_BROKEN": "Broken",
        "status_INACTIVE": "Inactive",

        # Priorities
        "priority_LOW": "Low",
        "priority_MEDIUM": "Medium",
        "priority_HIGH": "High",
        "priority_URGENT": "Urgent",

        # Categories
        "category_INCIDENT": "Technical Incident",
        "category_SERVICE_REQUEST": "Service Request",
        "category_MAINTENANCE": "Routine Maintenance",

        # Roles
        "role_ADMIN": "Administrator",
        "role_TECHNICIAN": "Technician",
        "role_USER": "User",

        # Actions
        "action_CREATED": "Ticket Created",
        "action_ASSIGNED": "Technician Assigned",
        "action_STATUS_CHANGED": "Status Changed",
        "action_RESOLVED": "Incident Resolved",
        "action_CLOSED": "Ticket Closed",
        "action_COMMENTED": "Comment Added",
        "action_UPDATED": "Ticket Updated",
        "action_REOPENED": "Ticket Reopened",

        # Common UI Terms
        "btn_refresh": "Refresh",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "btn_confirm": "Confirm",
        "btn_search": "Search",
        "btn_claim": "Claim Ticket",
        "btn_start_work": "Start Work",
        "btn_mark_resolved": "Mark as Resolved",
        "btn_close_ticket": "Close Ticket",
        "btn_send_comment": "Send Message",
        "btn_create_ticket": "Submit Support Request",
        "btn_all_tickets": "View All",

        # Dashboard & Workspace
        "tech_dash_title": "Welcome, {name}",
        "tech_dash_sub": "Here is your workload for today.",
        "kpi_my_active": "PENDING WORK",
        "kpi_my_in_progress": "IN PROGRESS",
        "kpi_urgent": "URGENT ATTENTION",
        "kpi_resolved": "RESOLVED",
        "sec_work_queue": "Work Queue",
        "sec_urgent_attention": "URGENT ATTENTION",
        "sec_progress": "WORK PROGRESS",
        "sec_quick_actions": "QUICK ACTIONS",
        "sec_recent_updates": "Recent Activity",
        "no_urgent_tickets": "No pending urgent incidents.",
        "all_work_done": "Great job! You have no pending tickets.",
    },
}


def get_lang() -> str:
    try:
        return app.storage.user.get("language", "vi")
    except Exception:
        return "vi"


def set_lang(lang: str) -> None:
    try:
        app.storage.user["language"] = lang
    except Exception:
        pass


def t(key: str, default: str | None = None, **kwargs: Any) -> str:
    lang = get_lang()
    raw = DICTIONARY.get(lang, {}).get(key) or DICTIONARY.get("vi", {}).get(key) or default or key
    if kwargs:
        try:
            return raw.format(**kwargs)
        except Exception:
            return raw
    return raw


def get_status_label(status: str | None) -> str:
    if not status:
        return "-"
    return t(f"status_{status}", default=status)


def get_priority_label(priority: str | None) -> str:
    if not priority:
        return "-"
    return t(f"priority_{priority}", default=priority)


def get_category_label(category: str | None) -> str:
    if not category:
        return "-"
    return t(f"category_{category}", default=category)


def get_role_label(role: str | None) -> str:
    if not role:
        return "-"
    return t(f"role_{role}", default=role)


def get_action_label(action: str | None) -> str:
    if not action:
        return "-"
    return t(f"action_{action}", default=action)
