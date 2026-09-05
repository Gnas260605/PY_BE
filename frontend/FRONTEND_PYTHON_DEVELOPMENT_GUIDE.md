# 📘 TÀI LIỆU KIẾN TRÚC & HƯỚNG DẪN PHÁT TRIỂN FRONTEND BẰNG PYTHON
> **Dự án:** CS466 Helpdesk Management System  
> **Backend API:** FastAPI (`http://127.0.0.1:8000/api`) — 19 Endpoints  
> **Ngôn ngữ Frontend:** Python 3.12  

---

## 🎯 1. TỔNG QUAN VÀ ĐỊNH HƯỚNG CÔNG NGHỆ

Hệ thống CS466 Helpdesk phân chia rõ 3 vai trò người dùng (**ADMIN**, **TECHNICIAN**, **USER**) cùng 19 REST API. Để chuyển đổi hoàn toàn Frontend sang Python mà vẫn đảm bảo **giao diện hiện đại**, **tối ưu thuật toán xử lý**, và **co giãn linh hoạt (Responsive) trên cả PC & Mobile**, ta lựa chọn các công nghệ hàng đầu:

### 🏆 Đề xuất Framework: **NiceGUI** (hoặc **Streamlit** / **Flet**)
* **NiceGUI (Khuyên dùng số 1):** Dựa trên nền tảng FastAPI + Vue/Quasar Tailwind. Viết 100% Python, hỗ trợ Flexbox/Grid chuẩn CSS để scale Mobile & PC cực kỳ mượt mà, hỗ trợ Async/Await native, WebSockets cập nhật trạng thái thời gian thực.
* **Flet (Flutter for Python):** Viết Python nhưng render bằng Flutter Engine. Co giãn đa nền tảng (Web, Mobile App Android/iOS, Desktop Windows) chuẩn từng pixel.
* **Streamlit:** Phát triển siêu tốc, phù hợp làm Dashboard báo cáo nhanh.

---

## 📂 2. CẤU TRÚC THƯ MỤC CHUẨN (ROLE-BASED & COMPONENT-DRIVEN)

Cấu trúc thư mục được thiết kế theo nguyên lý **Separation of Concerns (SoC)**: Tách biệt rõ các thành phần dùng chung (Common/Core) và các trang nghiệp vụ riêng biệt cho từng Role.

```text
frontend_python/
│
├── core/                               # [DÙNG CHUNG] Cấu hình nền tảng & Hạ tầng
│   ├── __init__.py
│   ├── config.py                       # URL Backend, App settings, Timeout
│   ├── http_client.py                  # HTTP Client wrapper (httpx async/sync, retry, error handling)
│   ├── auth_context.py                 # Quản lý Token JWT, Session, User state, Role Permission Guard
│   └── constants.py                    # Enum trạng thái (OPEN, IN_PROGRESS,...), Roles, Priority
│
├── common/                             # [DÙNG CHUNG] Thành phần giao diện tái sử dụng
│   ├── __init__.py
│   ├── styles/                         # Theme, Colors, Dark/Light Mode, Responsive Breakpoints
│   │   ├── theme.py
│   │   └── breakpoints.py              # Xử lý co giãn màn hình Mobile (<768px), Tablet, Desktop
│   ├── components/                     # UI Components dùng chung
│   │   ├── navbar.py                   # Header / Top Navigation bar
│   │   ├── sidebar.py                  # Sidebar điều hướng (PC: Sidebar, Mobile: Drawer menu)
│   │   ├── bottom_nav.py               # Thanh điều hướng dưới đáy (dành riêng cho Mobile)
│   │   ├── stat_card.py                # Thẻ thống kê KPI/Số liệu
│   │   ├── data_table.py               # Bảng dữ liệu thông minh (Sort, Filter, Pagination, Responsive)
│   │   ├── responsive_card.py          # Card hiển thị thay cho Table khi xem trên Mobile
│   │   ├── status_badge.py             # Badge hiển thị màu sắc theo trạng thái (OPEN, RESOLVED,...)
│   │   ├── modal.py                    # Popup Dialog / Modal xác nhận
│   │   └── toast.py                    # Thông báo Toast (Success, Error, Warning)
│   ├── formatters.py                   # Định dạng datetime (dd/MM/yyyy HH:mm), format text, truncate
│   └── validators.py                   # Kiểm tra dữ liệu Form (Email, Password, Required fields)
│
├── services/                           # [DÙNG CHUNG] Service Layer kết nối 19 API Backend
│   ├── __init__.py
│   ├── auth_service.py                 # POST /login, Logout
│   ├── user_service.py                 # GET/POST/PATCH /users, Status toggle (Admin)
│   ├── device_service.py               # GET/POST/PATCH/DELETE /devices
│   └── ticket_service.py               # GET/POST/PATCH /tickets, Assign, Resolve, Close, History
│
├── views/                              # Giao diện người dùng theo từng Module & Role
│   ├── __init__.py
│   ├── auth/                           # Màn hình Xác thực
│   │   └── login_view.py               # Form đăng nhập Responsive
│   │
│   ├── admin/                          # [VAI TRÒ: ADMIN]
│   │   ├── dashboard_view.py           # Tổng quan hệ thống, biểu đồ phân bổ ticket, thiết bị
│   │   ├── user_mgmt_view.py           # Quản lý tài khoản (CRUD user, Khóa/Mở khóa)
│   │   ├── device_mgmt_view.py         # Quản lý kho thiết bị (CRUD device)
│   │   └── ticket_dispatch_view.py     # Phân công Kỹ thuật viên (Assign Tech), giám sát toàn bộ ticket
│   │
│   ├── technician/                     # [VAI TRÒ: TECHNICIAN]
│   │   ├── task_board_view.py          # Danh sách ticket được giao, cập nhật IN_PROGRESS -> RESOLVED
│   │   ├── device_lookup_view.py       # Tra cứu thông số, lịch sử bảo trì thiết bị
│   │   └── resolution_modal.py         # Form nhập ghi chú khắc phục sự cố (resolution_note)
│   │
│   └── user/                           # [VAI TRÒ: USER - Người dùng cuối]
│       ├── my_tickets_view.py          # Danh sách ticket của tôi (Filter theo trạng thái)
│       ├── create_ticket_view.py       # Form tạo yêu cầu hỗ trợ mới (Chọn thiết bị, mức ưu tiên)
│       └── ticket_timeline_view.py     # Xem tiến độ xử lý & Lịch sử thao tác (Ticket History Timeline)
│
├── assets/                             # Hình ảnh, Icons, Logo
│   ├── logo.svg
│   └── favicon.ico
│
├── app.py                              # Entry Point chính của ứng dụng Frontend Python
└── requirements.txt                    # Danh sách thư viện Python Frontend
```

---

## 🔌 3. ÁNH XẠ 19 API BACKEND VÀO PYTHON SERVICE LAYER

Hệ thống API Contract hiện tại gồm 19 endpoint được nhóm thành 4 Service chính:

| Service | Endpoint Backend | Quyền hạn (Role) | Chức năng trên UI Python |
|:---|:---|:---:|:---|
| **`AuthService`** | `POST /login`<br>`GET /health` | Tất cả | Đăng nhập lưu JWT token, kiểm tra trạng thái Backend |
| **`UserService`** | `GET /users`<br>`POST /users`<br>`GET /users/{id}`<br>`PATCH /users/{id}`<br>`PATCH /users/{id}/status` | `ADMIN` | Quản lý thành viên, tìm kiếm theo tên/email/role, bật/tắt kích hoạt tài khoản |
| **`DeviceService`** | `GET /devices`<br>`POST /devices`<br>`GET /devices/{id}`<br>`PATCH /devices/{id}`<br>`DELETE /devices/{id}` | `ADMIN`, `TECHNICIAN`, `USER` | Danh mục thiết bị, kiểm tra tình trạng máy, thêm/sửa/xóa tài sản CNTT |
| **`TicketService`** | `GET /tickets`<br>`POST /tickets`<br>`GET /tickets/{id}`<br>`PATCH /tickets/{id}`<br>`PATCH /tickets/{id}/assign`<br>`PATCH /tickets/{id}/resolve`<br>`PATCH /tickets/{id}/close`<br>`GET /tickets/{id}/history` | Tùy Role | Tạo ticket, phân quyền nhận việc, cập nhật tiến độ, xem timeline chi tiết |

---

## ⚡ 4. TỐI ƯU HÓA THUẬT TOÁN & HIỆU NĂNG XỬ LÝ GIAO DIỆN (PERFORMANCE & ALGORITHMS)

Để giao diện chạy siêu mượt, không bị đơ giật (lag) kể cả khi có hàng nghìn bản ghi Ticket/User:

### 4.1. Thuật toán Client-side Cache với cơ chế TTL (Time-To-Live)
* **Vấn đề:** Các dữ liệu ít thay đổi (như danh sách thiết bị `DEVICES`, danh sách Kỹ thuật viên) nếu gọi API liên tục mỗi lần chuyển trang sẽ làm chậm UI và quá tải DB.
* **Giải pháp:** Áp dụng thuật toán **LRU Cache có hạn giờ (TTL)** trên bộ nhớ Frontend.
```python
import time
from functools import wraps

class TTLCache:
    def __init__(self, ttl_seconds=60):
        self.ttl = ttl_seconds
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            val, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return val
            del self.cache[key]
        return None

    def set(self, key, val):
        self.cache[key] = (val, time.time())
```

### 4.2. Thuật toán Debounce cho ô Tìm kiếm (Search Bar)
* **Vấn đề:** Người dùng gõ từng ký tự vào ô tìm kiếm nếu gọi API ngay lập tức sẽ sinh ra hàng chục request dư thừa (gây giật lag).
* **Giải pháp:** Sử dụng thuật toán **Debounce** với độ trễ 300ms. Chỉ gửi request API khi người dùng ngừng gõ quá 300ms.

### 4.3. Client-side Fast Indexing & Filtering
* Đối với danh sách Tickets (100 - 500 records), áp dụng thuật toán tìm kiếm đa tiêu chí bằng Python List Comprehension kết hợp Set Intersection để lọc tức thì theo: `Keyword + Status + Priority + AssignedTech` với độ phức tạp **O(N)** cực kỳ nhanh (< 2ms).

### 4.4. Cơ chế Cập nhật Lạc quan (Optimistic UI Update)
* Khi Kỹ thuật viên nhấn *"Bắt đầu xử lý"* hoặc *"Đổi trạng thái"*, giao diện Python đổi ngay trạng thái badge trên màn hình trước, đồng thời chạy ngầm gọi API `PATCH /tickets/{id}/resolve`. Nếu API trả về lỗi thì mới rollback lại trạng thái cũ và bắn thông báo Toast lỗi.

---

## 📱💻 5. THIẾT KẾ CO GIÃN RESPONSIVE (SCALE MOBILE & PC)

Để giao diện tự động thích ứng hoàn hảo giữa màn hình máy tính lớn (PC/Laptop) và điện thoại di động (Mobile):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PC / LAPTOP (≥ 1024px)                           │
│ ┌──────────────┬──────────────────────────────────────────────────────────┐ │
│ │              │  [Header]: User Info, Role Badge, Dark/Light, Logout     │ │
│ │   SIDEBAR    ├──────────────────────────────────────────────────────────┤ │
│ │  NAVIGATION  │  [KPI Stat Cards Grid: 4 Cột]                            │ │
│ │  (Cố định    ├──────────────────────────────────────────────────────────┤ │
│ │   bên trái)  │  [Data Table]: Bảng đầy đủ các cột, Sort, Actions        │ │
│ └──────────────┴──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────┐
│           MOBILE (< 768px)            │
│ ┌───────────────────────────────────┐ │
│ │ [≡] Helpdesk App        [Avatar]  │ │ <- Header rút gọn + Hamburger Button
│ ├───────────────────────────────────┤ │
│ │ [KPI Cards Slider / 2 Cột]        │ │
│ ├───────────────────────────────────┤ │
│ │ [Search & Filter Dropdown]        │ │
│ ├───────────────────────────────────┤ │
│ │ [Card 1]: Ticket #12 (Badge)      │ │ <- Tự động chuyển Table thành Card
│ │  Thiết bị: Laptop Dell - Sang HT  │ │    để dễ chạm vuốt trên màn hình nhỏ
│ │  [Chi tiết] [Cập nhật tiến độ]    │ │
│ ├───────────────────────────────────┤ │
│ │ [Card 2]: Ticket #11 (Badge)      │ │
│ ├───────────────────────────────────┤ │
│ │ [Trang chủ] [Tickets] [Tạo mới]   │ │ <- Bottom Navigation Bar dưới đáy
│ └───────────────────────────────────┘ │
└───────────────────────────────────────┘
```

### Các quy tắc Responsive chính:
1. **Layout Wrapper:**
   * **Trên PC (`width >= 1024px`):** Hiển thị Sidebar dọc bên trái, nội dung chính chiếm không gian rộng (Grid 3 - 4 cột).
   * **Trên Mobile (`width < 768px`):** Thu gọn Sidebar thành **Drawer Popup (Menu 3 gạch)** hoặc chuyển các nút chính xuống **Bottom Navigation Bar** ở đáy màn hình.
2. **Chuyển đổi Bảng Dữ liệu (Adaptive Data View):**
   * PC: Hiển thị dạng bảng truyền thống `<table>` với đầy đủ 8 cột (ID, Tiêu đề, Thiết bị, Người tạo, KTV phụ trách, Mức ưu tiên, Trạng thái, Thao tác).
   * Mobile: Tự động chuyển đổi thành dạng danh sách **Thẻ (Vertical Card List)**, hiển thị thông tin cốt lõi kèm nút bấm to dễ chạm (Touch-friendly).
3. **Form nhập liệu & Modal:**
   * PC: Modal pop-up ở giữa màn hình (kích thước 600px).
   * Mobile: Modal mở rộng toàn màn hình (Full-width Bottom Sheet) để bàn phím ảo không che mất nút Submit.

---

## 🛠️ 6. CODE MẪU THIẾT KẾ CƠ BẢN (REFERENCE IMPLEMENTATION)

Dưới đây là khung code mẫu Python (viết bằng **NiceGUI** + **httpx**) thể hiện rõ cách kết nối API, phân quyền Role và tự động Responsive:

### 6.1. Module gọi API Backend (`core/http_client.py`)
```python
import httpx
from core.auth_context import auth_context

BASE_URL = "http://127.0.0.1:8000/api"

class ApiClient:
    @staticmethod
    async def request(method: str, endpoint: str, data: dict = None, params: dict = None):
        headers = {"Content-Type": "application/json"}
        if auth_context.token:
            headers["Authorization"] = f"Bearer {auth_context.token}"

        async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    json=data,
                    params=params,
                    headers=headers
                )
                if response.status_code == 401:
                    auth_context.logout()
                    raise Exception("Phiên đăng nhập đã hết hạn!")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                err_detail = response.json().get("detail", str(e))
                raise Exception(f"Lỗi API: {err_detail}")
```

### 6.2. Kiểm soát Phân quyền (`core/auth_context.py`)
```python
class AuthContext:
    def __init__(self):
        self.token = None
        self.current_user = None

    def set_session(self, token: str, user: dict):
        self.token = token
        self.current_user = user

    def logout(self):
        self.token = None
        self.current_user = None

    def is_admin(self) -> bool:
        return self.current_user and self.current_user.get("vai_tro") == "ADMIN"

    def is_technician(self) -> bool:
        return self.current_user and self.current_user.get("vai_tro") == "TECHNICIAN"

    def is_user(self) -> bool:
        return self.current_user and self.current_user.get("vai_tro") == "USER"

auth_context = AuthContext()
```

### 6.3. Giao diện Đa nền tảng Responsive (`common/components/ticket_card.py`)
```python
from nicegui import ui

def render_ticket_card(ticket: dict, on_update_status=None):
    """Render thẻ Ticket tối ưu cả PC và Mobile"""
    status_colors = {
        "OPEN": "bg-blue-100 text-blue-800 border-blue-300",
        "IN_PROGRESS": "bg-amber-100 text-amber-800 border-amber-300",
        "RESOLVED": "bg-emerald-100 text-emerald-800 border-emerald-300",
        "CLOSED": "bg-gray-100 text-gray-800 border-gray-300",
    }
    
    color_class = status_colors.get(ticket.get("trang_thai"), "bg-gray-100 text-gray-800")

    with ui.card().classes('w-full p-4 mb-3 shadow-md rounded-xl hover:shadow-lg transition-all border'):
        with ui.row().classes('w-full justify-between items-center'):
            ui.label(f"#{ticket['id']} - {ticket['tieu_de']}").classes('text-lg font-bold text-gray-800')
            ui.label(ticket['trang_thai']).classes(f'px-3 py-1 text-xs font-semibold rounded-full border {color_class}')
        
        ui.label(ticket.get('mo_ta', '')).classes('text-sm text-gray-600 my-2 line-clamp-2')
        
        with ui.row().classes('w-full justify-between items-center text-xs text-gray-500 mt-2 border-t pt-2'):
            ui.label(f"👤 Người tạo: {ticket.get('nguoi_tao_ten', 'N/A')}")
            ui.label(f"💻 Thiết bị: {ticket.get('ma_thiet_bi', 'Chưa gắn')}")
            
        if on_update_status:
            with ui.row().classes('w-full justify-end mt-3 gap-2'):
                ui.button('Cập nhật tiến độ', on_click=lambda: on_update_status(ticket)).props('sm color=primary')
```

---

## 🚀 7. KẾ HOẠCH TRIỂN KHAI THEO TỪNG BƯỚC

1. **Giai đoạn 1 (Core & Auth):**
   * Xây dựng `core/http_client.py` và `core/auth_context.py`.
   * Tạo màn hình `views/auth/login_view.py` kết nối API `POST /login`.
2. **Giai đoạn 2 (Role USER):**
   * Tạo màn hình gửi Ticket hỗ trợ (`POST /tickets`) và tra cứu tiến độ (`GET /tickets`).
   * Xem dòng thời gian lịch sử (`GET /tickets/{id}/history`).
3. **Giai đoạn 3 (Role TECHNICIAN):**
   * Màn hình danh sách ticket cần xử lý.
   * Modal cập nhật trạng thái `IN_PROGRESS` $\to$ `RESOLVED` (`PATCH /tickets/{id}/resolve`).
4. **Giai đoạn 4 (Role ADMIN):**
   * Bảng quản lý Users (`GET/POST/PATCH /users`, Khóa/Mở tài khoản).
   * Bảng quản lý Thiết bị (`GET/POST/PATCH/DELETE /devices`).
   * Phân công Ticket cho Kỹ thuật viên (`PATCH /tickets/{id}/assign`).
5. **Giai đoạn 5 (Tối ưu hóa UI/UX & Responsive):**
   * Tinh chỉnh CSS Tailwind/Quasar để hiển thị hoàn hảo trên kích thước Mobile 375px đến Màn hình 4K.
   * Áp dụng TTL Cache và Debounce Search.
