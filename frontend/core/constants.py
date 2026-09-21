from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"
    USER = "USER"

class TicketStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class TicketCategory(str, Enum):
    INCIDENT = "INCIDENT"
    SERVICE_REQUEST = "SERVICE_REQUEST"
    MAINTENANCE = "MAINTENANCE"

class DeviceType(str, Enum):
    COMPUTER = "COMPUTER"
    PRINTER = "PRINTER"
    ROUTER = "ROUTER"
    OTHER = "OTHER"

class DeviceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    BROKEN = "BROKEN"
    INACTIVE = "INACTIVE"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

# Friendly Error Messages Mapping
ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Tên đăng nhập hoặc mật khẩu không chính xác.",
    "ACCOUNT_INACTIVE": "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Quản trị viên.",
    "USER_INACTIVE": "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Quản trị viên.",
    "INVALID_TOKEN": "Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
    "TOKEN_EXPIRED": "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
    "FORBIDDEN": "Bạn không có quyền thực hiện thao tác này.",
    "USERNAME_EXISTS": "Tên đăng nhập đã tồn tại trong hệ thống.",
    "DUPLICATE_USERNAME": "Tên đăng nhập đã tồn tại trong hệ thống.",
    "DUPLICATE_EMAIL": "Email đã tồn tại trong hệ thống.",
    "DEVICE_CODE_EXISTS": "Mã thiết bị (Device Code) đã tồn tại.",
    "DUPLICATE_DEVICE_CODE": "Mã thiết bị (Device Code) đã tồn tại.",
    "DEVICE_NOT_FOUND": "Không tìm thấy thiết bị yêu cầu.",
    "USER_NOT_FOUND": "Không tìm thấy người dùng.",
    "TICKET_NOT_FOUND": "Không tìm thấy yêu cầu hỗ trợ (Ticket).",
    "INVALID_STATUS_TRANSITION": "Không thể chuyển trạng thái theo yêu cầu.",
    "INVALID_INPUT": "Dữ liệu nhập chưa hợp lệ. Vui lòng kiểm tra lại.",
    "DEVICE_IN_USE": "Không thể xóa thiết bị đang được liên kết với Ticket đang mở.",
    "FILE_TOO_LARGE": "Dung lượng tệp vượt quá giới hạn cho phép (tối đa 10MB).",
    "INVALID_FILE_TYPE": "Định dạng tệp không được hỗ trợ. Vui lòng chọn tệp ảnh hoặc tài liệu thông dụng.",
    "RATE_LIMIT_EXCEEDED": "Bạn đã gửi yêu cầu quá nhanh hoặc thử đăng nhập sai quá số lần cho phép. Vui lòng thử lại sau 1 phút.",
    "ATTACHMENT_NOT_FOUND": "Không tìm thấy tệp đính kèm.",
    "FILE_NOT_FOUND": "Tệp tin không tồn tại trên hệ thống lưu trữ.",
    "SERVER_ERROR": "Lỗi máy chủ nội bộ. Vui lòng thử lại sau.",
    "CONNECTION_ERROR": "Không thể kết nối đến Backend Server (8000). Vui lòng kiểm tra lại dịch vụ Backend!"
}

ROLE_LABELS = {
    Role.ADMIN.value: "Quản trị viên",
    Role.TECHNICIAN.value: "Kỹ thuật viên",
    Role.USER.value: "Người dùng",
}

STATUS_LABELS = {
    TicketStatus.OPEN.value: "Chờ tiếp nhận",
    TicketStatus.ASSIGNED.value: "Đã phân công",
    TicketStatus.IN_PROGRESS.value: "Đang xử lý",
    TicketStatus.RESOLVED.value: "Đã giải quyết",
    TicketStatus.CLOSED.value: "Đã đóng hoàn tất",
    DeviceStatus.ACTIVE.value: "Hoạt động",
    DeviceStatus.MAINTENANCE.value: "Bảo trì",
    DeviceStatus.BROKEN.value: "Bị hỏng",
    DeviceStatus.INACTIVE.value: "Ngừng dùng",
    UserStatus.ACTIVE.value: "Đang hoạt động",
    UserStatus.INACTIVE.value: "Đã khóa",
}

ACTION_LABELS = {
    "CREATED": "Tạo mới sự cố",
    "ASSIGNED": "Phân công xử lý",
    "STATUS_CHANGED": "Cập nhật trạng thái",
    "RESOLVED": "Khắc phục sự cố",
    "CLOSED": "Đóng sự cố",
    "COMMENTED": "Thêm trao đổi",
    "UPDATED": "Cập nhật thông tin",
    "REOPENED": "Mở lại sự cố",
}

PRIORITY_LABELS = {
    TicketPriority.LOW.value: "Thấp",
    TicketPriority.MEDIUM.value: "Trung bình",
    TicketPriority.HIGH.value: "Cao",
    TicketPriority.URGENT.value: "Khẩn cấp",
}

CATEGORY_LABELS = {
    TicketCategory.INCIDENT.value: "Sự cố kỹ thuật",
    TicketCategory.SERVICE_REQUEST.value: "Yêu cầu dịch vụ",
    TicketCategory.MAINTENANCE.value: "Bảo trì định kỳ",
}

