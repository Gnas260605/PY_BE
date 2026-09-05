# Bàn giao Frontend Python - CS466 Helpdesk

Ngày bàn giao: 05/09/2026  
Phạm vi: `frontend/`  
Người tiếp nhận: Dev Frontend

## 1. Tổng quan

Frontend đã được tái cấu trúc theo hướng Python-first trong `FRONTEND_PYTHON_DEVELOPMENT_GUIDE.md`, sử dụng **NiceGUI + httpx** để kết nối backend FastAPI.

Nguồn sự thật kỹ thuật cần bám:

1. `docs/api-contract.md`
2. `database/schema.sql`
3. Code backend hiện tại đã merge
4. `frontend/FRONTEND_PYTHON_DEVELOPMENT_GUIDE.md`

Lưu ý quan trọng: guide frontend có nhắc `PATCH /tickets/{id}/resolve`, nhưng contract/backend hiện tại dùng `PATCH /tickets/{id}/status` để chuyển `RESOLVED`. Frontend Python mới đã bám theo contract/backend hiện tại.

## 2. Stack hiện tại

- Python 3.12
- NiceGUI `2.24.2`
- httpx `>=0.28.0`
- pydantic `>=2.0.0`
- python-dotenv `>=1.0.0`

NiceGUI được pin `2.24.2` để tương thích với backend đang pin `fastapi==0.116.1` và `starlette==0.47.3`. Không nên đổi thành `nicegui>=2.0.0` vì bản mới có thể kéo FastAPI/Starlette lên version không tương thích backend.

## 3. Cách chạy

Chạy backend trước tại `http://127.0.0.1:8000/api`, sau đó chạy frontend:

```powershell
cd D:\Individua_Project\Python_Project\frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Mặc định frontend chạy tại:

```text
http://127.0.0.1:8500
```

Biến môi trường hỗ trợ:

- `API_BASE_URL`: mặc định `http://127.0.0.1:8000/api`
- `FRONTEND_HOST`: mặc định `127.0.0.1`
- `FRONTEND_PORT`: mặc định `8500`
- `FRONTEND_CACHE_TTL_SECONDS`: mặc định `60`
- `FRONTEND_STORAGE_SECRET`: secret cho NiceGUI user storage

## 4. Cấu trúc thư mục mới

```text
frontend/
├── app.py
├── requirements.txt
├── core/
│   ├── auth_context.py
│   ├── cache.py
│   ├── config.py
│   ├── constants.py
│   └── http_client.py
├── common/
│   ├── formatters.py
│   ├── validators.py
│   ├── components/
│   │   ├── bottom_nav.py
│   │   ├── data_table.py
│   │   ├── layout.py
│   │   ├── modal.py
│   │   ├── navbar.py
│   │   ├── responsive_card.py
│   │   ├── sidebar.py
│   │   ├── stat_card.py
│   │   ├── status_badge.py
│   │   └── toast.py
│   └── styles/
│       ├── breakpoints.py
│       └── theme.py
├── services/
│   ├── auth_service.py
│   ├── device_service.py
│   ├── ticket_service.py
│   └── user_service.py
└── views/
    ├── auth/
    ├── admin/
    ├── technician/
    ├── user/
    ├── dashboard_view.py
    └── ticket_board.py
```

Các file HTML/JS cũ vẫn được giữ lại:

- `index.html`
- `pages/dashboard.html`
- `js/*.js`
- `assets/css/style.css`

Chúng là UI legacy, chưa bị xóa để tránh mất phần đang làm dở. Frontend Python mới chạy qua `app.py`.

## 5. Route frontend Python

| Route | Màn hình | Role mục tiêu |
|:---|:---|:---|
| `/` | Login | Public |
| `/login` | Login | Public |
| `/dashboard` | Dashboard tổng quan | USER, TECHNICIAN, ADMIN |
| `/admin/users` | Quản lý users | ADMIN |
| `/admin/devices` | Quản lý devices | ADMIN |
| `/admin/tickets` | Phân công/giám sát tickets | ADMIN |
| `/technician/tasks` | Ticket cần xử lý | TECHNICIAN |
| `/technician/devices` | Tra cứu/cập nhật devices | TECHNICIAN |
| `/user/tickets` | Ticket của tôi | USER |
| `/user/tickets/new` | Tạo ticket | USER, ADMIN |
| `/tickets/{ticket_id}/history` | Timeline ticket | USER, TECHNICIAN, ADMIN |

## 6. Service layer đã có

### AuthService

File: `services/auth_service.py`

- `health()`: gọi `GET /health`
- `login(username, password)`: gọi `POST /login`, lưu `access_token` và `current_user`
- `logout()`: xóa session và clear cache
- `current_user()`
- `is_authenticated()`

### UserService

File: `services/user_service.py`

- `list_users(role=None, status=None, keyword=None, refresh=False)`
- `list_technicians(refresh=False)`
- `create_user(payload)`
- `get_user(user_id)`
- `update_user(user_id, payload)`
- `update_user_status(user_id, status)`

Chỉ ADMIN dùng được theo backend RBAC.

### DeviceService

File: `services/device_service.py`

- `list_devices(status=None, type=None, keyword=None, refresh=False)`
- `create_device(payload)`
- `get_device(device_id)`
- `update_device(device_id, payload)`

Theo contract hiện tại: USER không được gọi `GET /devices`; chỉ ADMIN và TECHNICIAN.

### TicketService

File: `services/ticket_service.py`

- `list_tickets(...)`
- `create_ticket(payload)`
- `get_ticket(ticket_id)`
- `update_ticket(ticket_id, payload)`
- `assign_ticket(ticket_id, technician_id)`
- `update_status(ticket_id, status)`
- `close_ticket(ticket_id, note=None)`
- `get_history(ticket_id)`
- `next_statuses(current_status)`

Lifecycle đang bám backend:

```text
OPEN -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED
```

## 7. Component/UI đã có

- `common/components/layout.py`: app shell chung, login guard, navbar, sidebar, bottom nav.
- `common/components/navbar.py`: header responsive, user avatar, logout.
- `common/components/sidebar.py`: menu theo role.
- `common/components/bottom_nav.py`: navigation mobile.
- `common/components/stat_card.py`: KPI cards.
- `common/components/data_table.py`: bảng desktop + card list mobile cho ticket.
- `common/components/responsive_card.py`: ticket card touch-friendly.
- `common/components/status_badge.py`: badge màu cho status/priority.
- `common/components/toast.py`: notify success/error/warning.
- `common/styles/theme.py`: theme NiceGUI/Tailwind cơ bản.
- `common/styles/breakpoints.py`: class responsive dùng chung.

## 8. Quy ước dữ liệu cần nhớ

### User

- Role hợp lệ: `USER`, `TECHNICIAN`, `ADMIN`
- Status hợp lệ: `ACTIVE`, `INACTIVE`
- Field backend dùng tiếng Việt: `ho_ten`, `vai_tro`, `trang_thai`

### Device

- Status hợp lệ: `ACTIVE`, `MAINTENANCE`, `BROKEN`, `INACTIVE`
- Field backend: `ma_thiet_bi`, `ten_thiet_bi`, `loai_thiet_bi`, `vi_tri`, `trang_thai`, `mo_ta`

### Ticket

- Category hợp lệ: `INCIDENT`, `SERVICE_REQUEST`, `MAINTENANCE`
- Priority hợp lệ: `LOW`, `MEDIUM`, `HIGH`, `URGENT`
- Status hợp lệ: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`
- Field API đã được backend expose dạng tiếng Anh: `title`, `description`, `category`, `priority`, `status`

## 9. Việc đã verify

Đã chạy:

```powershell
python -m compileall .\frontend
```

Kết quả: pass.

Đã smoke test frontend:

```powershell
python app.py
Invoke-WebRequest http://127.0.0.1:8500/login
```

Kết quả:

```text
HTTP_STATUS=200
BODY_HAS_NICEGUI=True
```

## 10. Việc còn nên làm tiếp

Ưu tiên tiếp theo cho dev frontend:

1. Hoàn thiện CRUD edit/update cho User và Device trong modal thay vì mới có create/list cơ bản.
2. Bổ sung action buttons trong bảng desktop giống mobile card actions.
3. Làm form assign/status trực quan hơn cho ADMIN và TECHNICIAN.
4. Thêm page chi tiết ticket đầy đủ gồm creator/device/technician.
5. Thêm empty state/loading state thống nhất cho mọi bảng.
6. Bổ sung kiểm tra role ở UI trước khi gọi API, nhưng vẫn để backend RBAC là lớp bảo vệ chính.
7. Kiểm thử thủ công 3 tài khoản seed: `admin`, `tech01`, `user01`.
8. Nếu cần production hóa, tách frontend vào `.venv` riêng để không ảnh hưởng dependency backend.

## 11. Tài khoản demo

Mật khẩu seed mặc định:

```text
CS466@123
```

Tài khoản thường dùng:

- `admin`: ADMIN
- `tech01`: TECHNICIAN
- `user01`: USER

## 12. Lưu ý bàn giao

- Không tự sửa `database/schema.sql` từ frontend.
- Không đổi API endpoint nếu chưa cập nhật `docs/api-contract.md`.
- Nếu backend trả lỗi dạng `{ "detail": "ERROR_CODE" }`, `core/http_client.py` đã map một số mã lỗi sang tiếng Việt.
- Nếu chạy frontend trong môi trường global Python, dependency có thể ảnh hưởng backend; nên dùng `.venv` trong `frontend/`.
- UI HTML/JS legacy vẫn còn để tham khảo hoặc migrate dần, nhưng hướng chính hiện tại là Python NiceGUI.
