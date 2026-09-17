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
        "btn_continue_work": "Tiếp tục xử lý",
        "btn_view_now": "Xem và xử lý ngay",
        "btn_open_queue": "Mở hàng đợi sự cố",
        "btn_open_workspace": "Mở bàn làm việc",
        "btn_device_lookup": "Tra cứu thiết bị",
        "btn_open_workspace_arrow": "Mở Bàn làm việc KTV →",
        "btn_device_lookup_arrow": "Tra cứu thiết bị & Vị trí →",
        
        # Dashboard & Workspace
        "tech_dash_title": "Xin chào, {name}",
        "tech_dash_sub": "Đây là các công việc cần bạn xử lý hôm nay.",
        "admin_dash_title": "Trung tâm Điều hành & Giám sát Hệ thống",
        "admin_dash_sub": "Tổng quan vận hành, hiệu suất xử lý sự cố và tình trạng thiết bị toàn hệ thống.",
        "kpi_my_active": "VIỆC CẦN XỬ LÝ",
        "kpi_my_active_sub": "Sự cố đang chờ xử lý",
        "kpi_my_in_progress": "ĐANG XỬ LÝ",
        "kpi_my_in_progress_sub": "Đang trong tiến trình",
        "kpi_urgent": "CẦN ƯU TIÊN",
        "kpi_urgent_sub": "Mức High & Urgent chưa giải quyết",
        "kpi_resolved": "ĐÃ GIẢI QUYẾT",
        "kpi_resolved_sub": "Sự cố đã khắc phục",
        "sec_work_queue": "Công việc cần xử lý",
        "sec_work_queue_sub": "Các ticket đang được giao cho bạn, ưu tiên theo mức độ và thời gian cập nhật.",
        "sec_urgent_attention": "CẦN CHÚ Ý",
        "sec_progress": "TIẾN ĐỘ CÔNG VIỆC",
        "sec_quick_actions": "THAO TÁC NHANH",
        "sec_recent_updates": "Cập nhật gần đây",
        "sec_recent_updates_sub": "Lịch sử thay đổi và cập nhật trạng thái mới nhất trên các ticket.",
        "no_urgent_tickets": "Không có sự cố khẩn cấp tồn đọng.",
        "all_work_done": "Tuyệt vời! Bạn không còn sự cố nào tồn đọng.",
        "all_work_done_sub": "Hãy kiểm tra hàng đợi chung để tiếp nhận công việc mới nếu có.",
        "progress_done_text": "{resolved} / {total} công việc đã giải quyết",
        "progress_working": "Đang làm: {count}",
        "progress_waiting": "Chờ bắt đầu: {count}",
        "user_label": "Người dùng #{id}",
        "updated_time": "Cập nhật: {time}",
        "item_count_tickets": "{count} sự cố",
        "view_link": "Xem →",

        # Task Board View (Workbench)
        "tb_title": "Bàn làm việc Kỹ thuật viên",
        "tb_sub": "Tiếp nhận, xử lý sự cố và trao đổi trực tiếp với người yêu cầu.",
        "tab_my_tasks": "Việc của tôi",
        "tab_unassigned": "Chờ tiếp nhận",
        "tab_urgent": "Khẩn cấp",
        "tab_in_progress": "Đang xử lý",
        "tab_resolved": "Đã giải quyết",
        "tab_all": "Tất cả sự cố",
        "tb_total_tickets": "Tổng: {count} sự cố",
        "tb_search_placeholder": "Tìm kiếm theo mã, tiêu đề, thiết bị...",
        "tb_no_tickets_selected": "Chọn một sự cố bên trái để xem chi tiết",
        "tb_tech_actions": "Thao tác kỹ thuật:",
        "tb_tech_resolved_badge": "Đã hoàn tất khắc phục kỹ thuật",
        "tb_tech_closed_badge": "Sự cố đã được đóng hoàn tất.",
        "tb_description_title": "MÔ TẢ SỰ CỐ",
        "tb_info_title": "THÔNG TIN LIÊN QUAN",
        "tb_requester": "Người yêu cầu",
        "tb_device": "Thiết bị",
        "tb_device_location": "Vị trí thiết bị",
        "tb_created_at": "Thời gian tạo",
        "tb_category": "Phân loại",
        "tb_history_title": "LỊCH SỬ TIẾN TRÌNH",
        "tb_unlinked": "Không liên kết",
        "tb_no_location": "Chưa có thông tin",

        # Comments & Chat
        "chat_title": "Trao đổi & Phản hồi sự cố",
        "chat_placeholder": "Nhập nội dung phản hồi hoặc ghi chú kỹ thuật...",
        "chat_canned_title": "Câu trả lời nhanh:",
        "chat_send_btn": "Gửi tin nhắn",
        "chat_empty_title": "Chưa có trao đổi nào",
        "chat_empty_sub": "Nhập phản hồi bên dưới để bắt đầu trao đổi với người dùng.",
        "chat_author_me": "Bạn",
        "chat_badge_admin": "Admin",
        "chat_badge_tech": "KTV",
        "chat_badge_user": "User",

        # Ticket Detail View
        "detail_title": "Chi tiết sự cố #{id}",
        "detail_back": "Quay lại",
        "detail_tech_assigned": "Kỹ thuật viên phụ trách:",
        "detail_device_linked": "Thiết bị liên quan:",
        "detail_no_device": "Không gán thiết bị cụ thể",
        "detail_timeline_title": "Tiến trình & Lịch sử xử lý",
        "detail_events_count": "{count} mốc sự kiện",
        "detail_actions_title": "Tác vụ xử lý",
        "detail_btn_claim": "Nhận xử lý sự cố này",
        "detail_btn_assign": "Phân công Kỹ thuật viên",
        "detail_btn_change_tech": "Đổi Kỹ thuật viên",
        "detail_btn_start": "Bắt đầu xử lý",
        "detail_btn_resolve": "Đã khắc phục xong",
        "detail_btn_close": "Đóng sự cố",
        "detail_closed_text": "Ticket đã được đóng hoàn tất.",
        "detail_feedback_card_title": "Trao đổi & Phản hồi",
        "detail_feedback_card_sub": "Bạn có thể để lại bình luận hoặc phản hồi trực tiếp với Kỹ thuật viên ở khung trao đổi bên cạnh.",
        "detail_info_card_title": "Thông tin liên quan",
        "detail_creator": "Người tạo:",
        "detail_created_at": "Ngày tạo: {time}",
        "detail_updated_at": "Cập nhật: {time}",
        "detail_unassigned_tech": "Chưa phân công",
        "detail_unknown_location": "Chưa xác định",

        # User Settings View
        "settings_title": "Cài đặt & Tùy chọn hệ thống",
        "settings_sub": "Tùy chỉnh ngôn ngữ hiển thị, giao diện làm việc và thông tin tài khoản cá nhân.",
        "settings_breadcrumb_home": "Trang chủ",
        "settings_breadcrumb_current": "Cài đặt cá nhân",
        "settings_card_lang_title": "Ngôn ngữ & Vùng hiển thị",
        "settings_card_lang_sub": "Lựa chọn ngôn ngữ sử dụng trên toàn bộ giao diện hệ thống.",
        "settings_lang_label": "Ngôn ngữ giao diện (System Language)",
        "settings_theme_label": "Chế độ giao diện (Appearance)",
        "settings_density_label": "Mật độ hiển thị danh sách (Table Density)",
        "settings_theme_light": "☀️ Chế độ sáng (Light Mode)",
        "settings_theme_auto": "💻 Theo cài đặt thiết bị (System Default)",
        "settings_density_compact": "Gọn gàng (Compact - Khuyên dùng cho IT Operations)",
        "settings_density_comfortable": "Rộng rãi (Comfortable)",
        "settings_btn_save_pref": "Lưu tùy chọn",
        "settings_card_notify_title": "Tùy chọn thông báo",
        "settings_card_notify_sub": "Cấu hình cách hệ thống gửi cảnh báo và thông điệp.",
        "settings_notify_toast": "Hiển thị Popup Toast khi có tin nhắn phản hồi mới",
        "settings_notify_urgent": "Cảnh báo âm thanh khi phát hiện sự cố khẩn cấp (Urgent SLA)",
        "settings_notify_email": "Nhận email tóm tắt khi sự cố được giải quyết",
        "settings_btn_update_notify": "Cập nhật thông báo",
        "settings_card_profile_title": "Hồ sơ tài khoản",
        "settings_card_profile_sub": "Thông tin định danh của bạn trên hệ thống.",
        "settings_field_fullname": "Họ và tên",
        "settings_field_email": "Địa chỉ Email",
        "settings_field_phone": "Số điện thoại liên hệ",
        "settings_btn_update_profile": "Cập nhật thông tin",
        "settings_card_security_title": "Bảo mật & Mật khẩu",
        "settings_card_security_sub": "Đổi mật khẩu đăng nhập tài khoản.",
        "settings_field_old_pwd": "Mật khẩu hiện tại",
        "settings_field_new_pwd": "Mật khẩu mới (tối thiểu 8 ký tự)",
        "settings_field_confirm_pwd": "Xác nhận mật khẩu mới",
        "settings_btn_change_pwd": "Đổi mật khẩu",

        # Device Lookup View
        "lookup_title": "Tra cứu thiết bị & Lịch sử sửa chữa",
        "lookup_sub": "Tìm kiếm thiết bị và theo dõi các sự cố đã từng xảy ra trên thiết bị đó.",
        "lookup_select_device": "Chọn thiết bị cần tra cứu",
        "lookup_specs_title": "THÔNG SỐ & VỊ TRÍ THIẾT BỊ",
        "lookup_history_title": "LỊCH SỬ SỰ CỐ & SỬA CHỮA",
        "lookup_code": "Mã thiết bị",
        "lookup_name": "Tên thiết bị",
        "lookup_location": "Vị trí đặt",
        "lookup_status": "Tình trạng",
        "lookup_no_tickets": "Chưa ghi nhận sự cố nào trên thiết bị này.",

        # My Tickets & Create Ticket Views
        "mytickets_title": "Yêu cầu hỗ trợ của tôi",
        "mytickets_sub": "Theo dõi tiến trình giải quyết các sự cố và dịch vụ IT bạn đã gửi.",
        "mytickets_btn_new": "Tạo yêu cầu mới",
        "create_ticket_title": "Tạo yêu cầu hỗ trợ IT",
        "create_ticket_sub": "Điền thông tin sự cố để đội ngũ Kỹ thuật viên tiếp nhận và xử lý nhanh chóng.",
        "create_sec_info": "1. THÔNG TIN SỰ CỐ",
        "create_sec_device": "2. THIẾT BỊ LIÊN QUAN",
        "create_sec_desc": "3. MÔ TẢ CHI TIẾT",
        "create_field_title": "Tiêu đề yêu cầu tóm tắt",
        "create_field_category": "Phân loại sự cố / dịch vụ",
        "create_field_priority": "Mức độ ưu tiên / Ảnh hưởng",
        "create_field_device": "Thiết bị gặp sự cố (Tùy chọn)",
        "create_field_desc": "Mô tả chi tiết hiện tượng lỗi, phần mềm bị ảnh hưởng...",
        "create_btn_submit": "Gửi yêu cầu hỗ trợ",
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
        "btn_continue_work": "Continue Work",
        "btn_view_now": "Inspect & Work Now",
        "btn_open_queue": "Open Ticket Queue",
        "btn_open_workspace": "Open Tech Workspace",
        "btn_device_lookup": "Device Lookup",
        "btn_open_workspace_arrow": "Open Tech Workspace →",
        "btn_device_lookup_arrow": "Lookup Devices & Location →",

        # Dashboard & Workspace
        "tech_dash_title": "Welcome, {name}",
        "tech_dash_sub": "Here is your operational workload for today.",
        "admin_dash_title": "IT Operations & Monitoring Center",
        "admin_dash_sub": "System overview, ticket performance metrics, and enterprise device health.",
        "kpi_my_active": "PENDING WORK",
        "kpi_my_active_sub": "Tickets awaiting action",
        "kpi_my_in_progress": "IN PROGRESS",
        "kpi_my_in_progress_sub": "Active investigations",
        "kpi_urgent": "URGENT ATTENTION",
        "kpi_urgent_sub": "High & Urgent SLA incidents",
        "kpi_resolved": "RESOLVED",
        "kpi_resolved_sub": "Completed resolutions",
        "sec_work_queue": "Work Queue",
        "sec_work_queue_sub": "Tickets assigned to you, prioritized by severity and recent activity.",
        "sec_urgent_attention": "URGENT ATTENTION",
        "sec_progress": "WORK PROGRESS",
        "sec_quick_actions": "QUICK ACTIONS",
        "sec_recent_updates": "Recent Activity",
        "sec_recent_updates_sub": "Real-time state transitions and status updates on all tickets.",
        "no_urgent_tickets": "No pending urgent incidents.",
        "all_work_done": "Great job! You have no pending tickets.",
        "all_work_done_sub": "Check the unassigned ticket queue to claim new incoming tasks.",
        "progress_done_text": "{resolved} / {total} tasks resolved",
        "progress_working": "Working: {count}",
        "progress_waiting": "Queued: {count}",
        "user_label": "User #{id}",
        "updated_time": "Updated: {time}",
        "item_count_tickets": "{count} tickets",
        "view_link": "View →",

        # Task Board View (Workbench)
        "tb_title": "Technician Workspace",
        "tb_sub": "Accept, resolve incidents and collaborate directly with requesters.",
        "tab_my_tasks": "My Tasks",
        "tab_unassigned": "Unassigned",
        "tab_urgent": "Urgent",
        "tab_in_progress": "In Progress",
        "tab_resolved": "Resolved",
        "tab_all": "All Tickets",
        "tb_total_tickets": "Total: {count} tickets",
        "tb_search_placeholder": "Search by ID, title, device...",
        "tb_no_tickets_selected": "Select a ticket from the left queue to inspect details",
        "tb_tech_actions": "Technical Actions:",
        "tb_tech_resolved_badge": "Technical resolution completed",
        "tb_tech_closed_badge": "Incident has been closed.",
        "tb_description_title": "INCIDENT DESCRIPTION",
        "tb_info_title": "ASSOCIATED INFORMATION",
        "tb_requester": "Requester",
        "tb_device": "Device",
        "tb_device_location": "Device Location",
        "tb_created_at": "Created At",
        "tb_category": "Category",
        "tb_history_title": "AUDIT TIMELINE",
        "tb_unlinked": "Unlinked",
        "tb_no_location": "No location configured",

        # Comments & Chat
        "chat_title": "Collaboration & Incident Feed",
        "chat_placeholder": "Type your response or technical note...",
        "chat_canned_title": "Canned Responses:",
        "chat_send_btn": "Send Message",
        "chat_empty_title": "No messages yet",
        "chat_empty_sub": "Enter a message below to start collaborating with the requester.",
        "chat_author_me": "You",
        "chat_badge_admin": "Admin",
        "chat_badge_tech": "Tech",
        "chat_badge_user": "User",

        # Ticket Detail View
        "detail_title": "Ticket Details #{id}",
        "detail_back": "Back",
        "detail_tech_assigned": "Assigned Technician:",
        "detail_device_linked": "Associated Device:",
        "detail_no_device": "No specific device linked",
        "detail_timeline_title": "Resolution Progress & History",
        "detail_events_count": "{count} events",
        "detail_actions_title": "Operational Actions",
        "detail_btn_claim": "Claim this Ticket",
        "detail_btn_assign": "Assign Technician",
        "detail_btn_change_tech": "Reassign Technician",
        "detail_btn_start": "Start Work",
        "detail_btn_resolve": "Mark as Resolved",
        "detail_btn_close": "Close Ticket",
        "detail_closed_text": "Ticket has been closed completely.",
        "detail_feedback_card_title": "Collaboration & Feedback",
        "detail_feedback_card_sub": "You can leave comments or communicate directly with the technician in the discussion panel.",
        "detail_info_card_title": "Associated Information",
        "detail_creator": "Creator:",
        "detail_created_at": "Created: {time}",
        "detail_updated_at": "Updated: {time}",
        "detail_unassigned_tech": "Unassigned",
        "detail_unknown_location": "Unknown Location",

        # User Settings View
        "settings_title": "System Settings & Preferences",
        "settings_sub": "Customize display language, workspace interface and personal account info.",
        "settings_breadcrumb_home": "Home",
        "settings_breadcrumb_current": "User Settings",
        "settings_card_lang_title": "Language & Region",
        "settings_card_lang_sub": "Choose the primary language used across the entire system interface.",
        "settings_lang_label": "System Language",
        "settings_theme_label": "Appearance Theme",
        "settings_density_label": "Table Density",
        "settings_theme_light": "☀️ Light Mode",
        "settings_theme_auto": "💻 System Default",
        "settings_density_compact": "Compact (Recommended for IT Operations)",
        "settings_density_comfortable": "Comfortable",
        "settings_btn_save_pref": "Save Preferences",
        "settings_card_notify_title": "Notification Preferences",
        "settings_card_notify_sub": "Configure how the system delivers alerts and incident messages.",
        "settings_notify_toast": "Show Toast popups when new comments/replies arrive",
        "settings_notify_urgent": "Play audio alert when urgent SLA incidents are detected",
        "settings_notify_email": "Receive email summaries when tickets are resolved",
        "settings_btn_update_notify": "Update Notifications",
        "settings_card_profile_title": "Account Profile",
        "settings_card_profile_sub": "Your identification details on the system.",
        "settings_field_fullname": "Full Name",
        "settings_field_email": "Email Address",
        "settings_field_phone": "Phone Number",
        "settings_btn_update_profile": "Update Profile",
        "settings_card_security_title": "Security & Password",
        "settings_card_security_sub": "Change your account login password.",
        "settings_field_old_pwd": "Current Password",
        "settings_field_new_pwd": "New Password (min 8 characters)",
        "settings_field_confirm_pwd": "Confirm New Password",
        "settings_btn_change_pwd": "Change Password",

        # Device Lookup View
        "lookup_title": "Device Lookup & Maintenance History",
        "lookup_sub": "Search device specs and inspect historic incidents recorded for this device.",
        "lookup_select_device": "Select device to inspect",
        "lookup_specs_title": "DEVICE SPECIFICATIONS & LOCATION",
        "lookup_history_title": "INCIDENT & REPAIR HISTORY",
        "lookup_code": "Device Tag",
        "lookup_name": "Device Name",
        "lookup_location": "Assigned Location",
        "lookup_status": "Status",
        "lookup_no_tickets": "No incidents reported for this device.",

        # My Tickets & Create Ticket Views
        "mytickets_title": "My Support Tickets",
        "mytickets_sub": "Track real-time progress on IT incidents and service requests you submitted.",
        "mytickets_btn_new": "Create New Ticket",
        "create_ticket_title": "Submit IT Support Request",
        "create_ticket_sub": "Fill in the issue details for prompt review and resolution by the IT Helpdesk team.",
        "create_sec_info": "1. INCIDENT INFORMATION",
        "create_sec_device": "2. ASSOCIATED DEVICE",
        "create_sec_desc": "3. DETAILED DESCRIPTION",
        "create_field_title": "Summary Title",
        "create_field_category": "Incident / Request Category",
        "create_field_priority": "Severity / Impact Level",
        "create_field_device": "Faulty Device (Optional)",
        "create_field_desc": "Detailed error symptom, software impacted...",
        "create_btn_submit": "Submit Request",
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


TICKET_TITLE_TRANSLATIONS: dict[str, str] = {
    "Máy Tính Phòng 202 bị hư": "Room 202 Computer is broken",
    "Bảo trì định kỳ máy chủ cơ sở dữ liệu": "Routine Database Server Maintenance",
    "Mất kết nối mạng toàn bộ phòng Nhân sự": "Network down for entire HR Department",
    "Máy in không in được từ máy tính kế toán": "Printer cannot print from accounting computer",
    "Màn hình PC-001 không lên nguồn": "PC-001 monitor does not turn on",
    "Cài đặt phần mềm kế toán MISA mới": "Install new MISA accounting software",
    "Thay hộp mực máy in màu phòng Thiết kế": "Replace toner for Design room color printer",
    "Cấp quyền truy cập thư mục chung phòng Kế toán": "Grant shared folder access for Accounting room",
    "Bảo trì nâng cấp Firmware Router Tầng 2": "Firmware upgrade for 2nd Floor Router",
}

TICKET_DESC_TRANSLATIONS: dict[str, str] = {
    "Thực hiện hút bụi, kiểm tra dung lượng ổ cứng và sao lưu database tháng 8.": "Perform dusting, check disk space, and back up August database.",
    "Toàn bộ máy tính tầng 3 không thể truy cập internet và mạng nội bộ.": "All computers on 3rd floor cannot access internet and local network.",
    "Người dùng gửi lệnh in từ PC-001 nhưng máy in Canon không phản hồi, đèn báo nháy đỏ.": "User sent print job from PC-001 but Canon printer does not respond, red light blinking.",
    "Màn hình bật không lên tín hiệu, quạt máy tính vẫn quay. Đã thử đổi ổ cắm.": "Monitor turns on with no signal, computer fan still spinning. Tried changing power outlet.",
    "Cần cài đặt bản quyền phần mềm MISA 2026 cho máy tính kế toán viên mới.": "Need to install genuine MISA 2026 license for new accountant's computer.",
    "Máy in màu Epson L8056 báo cạn mực vàng và xanh, bản in bị sọc.": "Epson L8056 color printer reports low yellow and cyan ink, prints are streaked.",
    "Nhân viên mới cần quyền truy cập thư mục Z:\\Accounting trên File Server.": "New employee needs access to Z:\\Accounting folder on File Server.",
    "Cập nhật bản vá bảo mật CVE-2026 cho Router Cisco phòng Server.": "Apply CVE-2026 security patch to Cisco Router in Server Room.",
}


def get_ticket_title(title: str | None) -> str:
    if not title:
        return "-"
    if get_lang() == "en":
        return TICKET_TITLE_TRANSLATIONS.get(title.strip(), title)
    return title


def get_ticket_desc(desc: str | None) -> str:
    if not desc:
        return "-"
    if get_lang() == "en":
        return TICKET_DESC_TRANSLATIONS.get(desc.strip(), desc)
    return desc

