# KẾT QUẢ KIỂM THỬ API CHI TIẾT — VAI TRÒ: ADMIN
> **Commit SHA:** `bf51d53f57ba2e0ac537dd1b349122e3400f28c4`  
> **Thời gian chạy:** 2026-09-21 20:24:51  
> **Môi trường:** Local FastAPI (Python 3.12 + MySQL 8.0)  
> **Tổng số test cases:** 19 | **Thành công:** 19 | **Thất bại:** 0  
> **Đánh giá tổng thể:** **`PASSED`**

---

## 1. Bảng tóm tắt kết quả (Summary Table)

| ID | Tên kịch bản | Method | Endpoint | Expected | Actual | Thời gian | Trạng thái |
|:---|:---|:---:|:---|:---:|:---:|:---:|:---:|
| `ADM-01` | Kiểm tra Healthcheck hệ thống | `GET` | `/api/health` | `200` | `200` | 16.64ms | ✅ PASS |
| `ADM-02` | Đăng nhập ADMIN thành công | `POST` | `/api/login` | `200` | `200` | 383.38ms | ✅ PASS |
| `ADM-03` | Đăng nhập sai mật khẩu | `POST` | `/api/login` | `401` | `401` | 369.25ms | ✅ PASS |
| `ADM-04` | Lấy danh sách Users (Hỗ trợ lọc & tìm kiếm) | `GET` | `/api/users?role=USER&status=ACTIVE` | `200` | `200` | 24.94ms | ✅ PASS |
| `ADM-05` | Tạo User mới (user_adm_test) | `POST` | `/api/users` | `201` | `201` | 380.1ms | ✅ PASS |
| `ADM-06` | Tạo User trùng Username (Expect 409) | `POST` | `/api/users` | `409` | `409` | 26.54ms | ✅ PASS |
| `ADM-07` | Xem chi tiết User vừa tạo | `GET` | `/api/users/8` | `200` | `200` | 25.34ms | ✅ PASS |
| `ADM-08` | Cập nhật thông tin User | `PATCH` | `/api/users/8` | `200` | `200` | 33.92ms | ✅ PASS |
| `ADM-09` | Vô hiệu hóa User (INACTIVE) | `PATCH` | `/api/users/8/status` | `200` | `200` | 30.9ms | ✅ PASS |
| `ADM-10` | Đăng nhập bằng tài khoản INACTIVE (Expect 401) | `POST` | `/api/login` | `401` | `401` | 14.91ms | ✅ PASS |
| `ADM-11` | Kích hoạt lại User (ACTIVE) | `PATCH` | `/api/users/8/status` | `200` | `200` | 29.88ms | ✅ PASS |
| `ADM-12` | Thêm thiết bị mới (PC-999) | `POST` | `/api/devices` | `201` | `201` | 32.33ms | ✅ PASS |
| `ADM-13` | Thêm thiết bị trùng Mã (Expect 409) | `POST` | `/api/devices` | `409` | `409` | 21.55ms | ✅ PASS |
| `ADM-14` | Lấy danh sách thiết bị | `GET` | `/api/devices?status=ACTIVE&keyword=PC` | `200` | `200` | 23.43ms | ✅ PASS |
| `ADM-15` | Xem chi tiết thiết bị | `GET` | `/api/devices/8` | `200` | `200` | 28.83ms | ✅ PASS |
| `ADM-16` | Cập nhật thông tin & trạng thái thiết bị | `PATCH` | `/api/devices/8` | `200` | `200` | 40.01ms | ✅ PASS |
| `ADM-17` | Admin xem toàn bộ Ticket trong hệ thống | `GET` | `/api/tickets` | `200` | `200` | 34.09ms | ✅ PASS |
| `ADM-18` | Admin gán Kỹ thuật viên cho Ticket | `PATCH` | `/api/tickets/2/assign` | `200` | `200` | 42.78ms | ✅ PASS |
| `ADM-19` | Gán User không phải Kỹ thuật viên (Expect 400) | `PATCH` | `/api/tickets/2/assign` | `400` | `400` | 29.06ms | ✅ PASS |

---

## 2. Chi tiết từng kịch bản kiểm thử (Request & Response Details)

### `ADM-01` - Kiểm tra Healthcheck hệ thống
- **Mô tả:** Xác nhận server và kết nối MySQL hoạt động bình thường
- **Request:** `GET /api/health`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `16.64 ms`
```json
// Response Body:
{
  "status": "ok"
}
```

### `ADM-02` - Đăng nhập ADMIN thành công
- **Mô tả:** Đăng nhập tài khoản admin lấy Bearer token
- **Request:** `POST /api/login`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `383.38 ms`
```json
// Request Body:
{
  "username": "admin",
  "password": "CS466@123"
}
```
```json
// Response Body:
{
  "access_token": "<redacted>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "ho_ten": "Quản trị hệ thống",
    "email": "admin@cs466.local",
    "vai_tro": "ADMIN",
    "trang_thai": "ACTIVE"
  }
}
```

### `ADM-03` - Đăng nhập sai mật khẩu
- **Mô tả:** Kỳ vọng 401 Unauthorized khi nhập sai mật khẩu
- **Request:** `POST /api/login`
- **HTTP Status:** Kỳ vọng `401` | Thực tế `401` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `369.25 ms`
```json
// Request Body:
{
  "username": "admin",
  "password": "WrongPassword"
}
```
```json
// Response Body:
{
  "detail": "AUTH_FAILED",
  "path": "/api/login"
}
```

### `ADM-04` - Lấy danh sách Users (Hỗ trợ lọc & tìm kiếm)
- **Mô tả:** Admin lấy danh sách user lọc theo role=USER và status=ACTIVE
- **Request:** `GET /api/users?role=USER&status=ACTIVE`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `24.94 ms`
```json
// Response Body:
[
  {
    "id": 3,
    "username": "user01",
    "ho_ten": "Người dùng 01",
    "email": "user01@cs466.local",
    "vai_tro": "USER",
    "trang_thai": "ACTIVE",
    "receive_email_on_resolve": false,
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  },
  {
    "id": 4,
    "username": "user02",
    "ho_ten": "Nguyễn Văn B (Kế toán)",
    "email": "ketoan_b@cs466.local",
    "vai_tro": "USER",
    "trang_thai": "ACTIVE",
    "receive_email_on_resolve": false,
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  },
  {
    "id": 6,
    "username": "user03",
    "ho_ten": "Trần Thị C (Nhân sự)",
    "email": "nhansu_c@cs466.local",
    "vai_tro": "USER",
    "trang_thai": "ACTIVE",
    "receive_email_on_resolve": false,
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  }
]
```

### `ADM-05` - Tạo User mới (user_adm_test)
- **Mô tả:** Tạo người dùng mới với mật khẩu bcrypt, không trả về password_hash
- **Request:** `POST /api/users`
- **HTTP Status:** Kỳ vọng `201` | Thực tế `201` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `380.1 ms`
```json
// Request Body:
{
  "username": "user_adm_test",
  "password": "CS466@123",
  "ho_ten": "Nguyễn Văn B",
  "email": "user_adm_test@cs466.local",
  "vai_tro": "USER"
}
```
```json
// Response Body:
{
  "id": 8,
  "username": "user_adm_test",
  "ho_ten": "Nguyễn Văn B",
  "email": "user_adm_test@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "receive_email_on_resolve": false,
  "created_at": "2026-09-21T13:24:52",
  "updated_at": "2026-09-21T13:24:52"
}
```

### `ADM-06` - Tạo User trùng Username (Expect 409)
- **Mô tả:** Kỳ vọng 409 Conflict khi username đã tồn tại
- **Request:** `POST /api/users`
- **HTTP Status:** Kỳ vọng `409` | Thực tế `409` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `26.54 ms`
```json
// Request Body:
{
  "username": "user_adm_test",
  "password": "CS466@123",
  "ho_ten": "Nguyen Van B Trùng",
  "email": "diff_email@cs466.local",
  "vai_tro": "USER"
}
```
```json
// Response Body:
{
  "detail": "DUPLICATE_USER",
  "path": "/api/users"
}
```

### `ADM-07` - Xem chi tiết User vừa tạo
- **Mô tả:** Lấy chi tiết user theo ID
- **Request:** `GET /api/users/8`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `25.34 ms`
```json
// Response Body:
{
  "id": 8,
  "username": "user_adm_test",
  "ho_ten": "Nguyễn Văn B",
  "email": "user_adm_test@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "receive_email_on_resolve": false,
  "created_at": "2026-09-21T13:24:52",
  "updated_at": "2026-09-21T13:24:52"
}
```

### `ADM-08` - Cập nhật thông tin User
- **Mô tả:** Cập nhật họ tên và email của user
- **Request:** `PATCH /api/users/8`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `33.92 ms`
```json
// Request Body:
{
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "user_adm_updated@cs466.local",
  "vai_tro": "USER"
}
```
```json
// Response Body:
{
  "id": 8,
  "username": "user_adm_test",
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "user_adm_updated@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "receive_email_on_resolve": false,
  "created_at": "2026-09-21T13:24:52",
  "updated_at": "2026-09-21T13:24:52"
}
```

### `ADM-09` - Vô hiệu hóa User (INACTIVE)
- **Mô tả:** Khóa tài khoản user sang trạng thái INACTIVE
- **Request:** `PATCH /api/users/8/status`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `30.9 ms`
```json
// Request Body:
{
  "status": "INACTIVE"
}
```
```json
// Response Body:
{
  "id": 8,
  "username": "user_adm_test",
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "user_adm_updated@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "INACTIVE",
  "receive_email_on_resolve": false,
  "created_at": "2026-09-21T13:24:52",
  "updated_at": "2026-09-21T13:24:52"
}
```

### `ADM-10` - Đăng nhập bằng tài khoản INACTIVE (Expect 401)
- **Mô tả:** Tài khoản INACTIVE không được phép đăng nhập
- **Request:** `POST /api/login`
- **HTTP Status:** Kỳ vọng `401` | Thực tế `401` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `14.91 ms`
```json
// Request Body:
{
  "username": "user_adm_test",
  "password": "CS466@123"
}
```
```json
// Response Body:
{
  "detail": "AUTH_FAILED",
  "path": "/api/login"
}
```

### `ADM-11` - Kích hoạt lại User (ACTIVE)
- **Mô tả:** Kích hoạt lại tài khoản sang trạng thái ACTIVE
- **Request:** `PATCH /api/users/8/status`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `29.88 ms`
```json
// Request Body:
{
  "status": "ACTIVE"
}
```
```json
// Response Body:
{
  "id": 8,
  "username": "user_adm_test",
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "user_adm_updated@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "receive_email_on_resolve": false,
  "created_at": "2026-09-21T13:24:52",
  "updated_at": "2026-09-21T13:24:52"
}
```

### `ADM-12` - Thêm thiết bị mới (PC-999)
- **Mô tả:** Admin thêm thiết bị mới vào hệ thống
- **Request:** `POST /api/devices`
- **HTTP Status:** Kỳ vọng `201` | Thực tế `201` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `32.33 ms`
```json
// Request Body:
{
  "ma_thiet_bi": "PC-999",
  "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế Toán - Tầng 2",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Optiplex i7 16GB"
}
```
```json
// Response Body:
{
  "id": 8,
  "ma_thiet_bi": "PC-999",
  "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế Toán - Tầng 2",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Optiplex i7 16GB",
  "created_at": "2026-09-21T13:24:52",
  "updated_at": "2026-09-21T13:24:52"
}
```

### `ADM-13` - Thêm thiết bị trùng Mã (Expect 409)
- **Mô tả:** Kỳ vọng 409 Conflict khi mã thiết bị đã tồn tại
- **Request:** `POST /api/devices`
- **HTTP Status:** Kỳ vọng `409` | Thực tế `409` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `21.55 ms`
```json
// Request Body:
{
  "ma_thiet_bi": "PC-999",
  "ten_thiet_bi": "Máy tính phòng Marketing",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Marketing"
}
```
```json
// Response Body:
{
  "detail": "DUPLICATE_DEVICE_CODE",
  "path": "/api/devices"
}
```

### `ADM-14` - Lấy danh sách thiết bị
- **Mô tả:** Lấy danh sách thiết bị có lọc theo trạng thái và từ khóa
- **Request:** `GET /api/devices?status=ACTIVE&keyword=PC`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `23.43 ms`
```json
// Response Body:
[
  {
    "id": 1,
    "ma_thiet_bi": "PC-001",
    "ten_thiet_bi": "Máy tính phòng Kế toán 01",
    "loai_thiet_bi": "COMPUTER",
    "vi_tri": "Phòng Kế toán - Tầng 2",
    "trang_thai": "ACTIVE",
    "mo_ta": "Dell Optiplex 7090 i7 16GB",
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  },
  {
    "id": 4,
    "ma_thiet_bi": "PC-002",
    "ten_thiet_bi": "Máy tính phòng Nhân sự",
    "loai_thiet_bi": "COMPUTER",
    "vi_tri": "Phòng Nhân sự - Tầng 3",
    "trang_thai": "ACTIVE",
    "mo_ta": "HP EliteDesk 800 G6",
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  },
  {
    "id": 8,
    "ma_thiet_bi": "PC-999",
    "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
    "loai_thiet_bi": "COMPUTER",
    "vi_tri": "Phòng Kế Toán - Tầng 2",
    "trang_thai": "ACTIVE",
    "mo_ta": "Dell Optiplex i7 16GB",
    "created_at": "2026-09-21T13:24:52",
    "updated_at": "2026-09-21T13:24:52"
  }
]
```

### `ADM-15` - Xem chi tiết thiết bị
- **Mô tả:** Lấy thông tin chi tiết thiết bị
- **Request:** `GET /api/devices/8`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `28.83 ms`
```json
// Response Body:
{
  "id": 8,
  "ma_thiet_bi": "PC-999",
  "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế Toán - Tầng 2",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Optiplex i7 16GB",
  "created_at": "2026-09-21T13:24:52",
  "updated_at": "2026-09-21T13:24:52"
}
```

### `ADM-16` - Cập nhật thông tin & trạng thái thiết bị
- **Mô tả:** Đổi trạng thái thiết bị sang MAINTENANCE
- **Request:** `PATCH /api/devices/8`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `40.01 ms`
```json
// Request Body:
{
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Đang gửi bảo hành ổ cứng"
}
```
```json
// Response Body:
{
  "id": 8,
  "ma_thiet_bi": "PC-999",
  "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế Toán - Tầng 2",
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Đang gửi bảo hành ổ cứng",
  "created_at": "2026-09-21T13:24:52",
  "updated_at": "2026-09-21T13:24:52"
}
```

### `ADM-17` - Admin xem toàn bộ Ticket trong hệ thống
- **Mô tả:** Admin có quyền xem mọi ticket của toàn bộ người dùng
- **Request:** `GET /api/tickets`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `34.09 ms`
```json
// Response Body:
[
  {
    "id": 8,
    "title": "Bảo trì nâng cấp Firmware Router Tầng 2",
    "description": "Cập nhật bản vá bảo mật CVE-2026 cho Router Cisco phòng Server.",
    "category": "MAINTENANCE",
    "priority": "HIGH",
    "status": "IN_PROGRESS",
    "user_id": 3,
    "device_id": 3,
    "technician_id": 5,
    "created_at": "2026-08-24T15:00:00",
    "updated_at": "2026-09-21T13:24:51",
    "resolved_at": null,
    "closed_at": null
  },
  {
    "id": 7,
    "title": "Cấp quyền truy cập thư mục chung phòng Kế toán",
    "description": "Nhân viên mới cần quyền truy cập thư mục Z:\\Accounting trên File Server.",
    "category": "SERVICE_REQUEST",
    "priority": "MEDIUM",
    "status": "RESOLVED",
    "user_id": 4,
    "device_id": 5,
    "technician_id": 5,
    "created_at": "2026-08-24T14:30:00",
    "updated_at": "2026-09-21T13:24:51",
    "resolved_at": "2026-08-24T15:45:00",
    "closed_at": null
  },
  {
    "id": 6,
    "title": "Thay hộp mực máy in màu phòng Thiết kế",
    "description": "Máy in màu Epson L8056 báo cạn mực vàng và xanh, bản in bị sọc.",
    "category": "SERVICE_REQUEST",
    "priority": "LOW",
    "status": "OPEN",
    "user_id": 3,
    "device_id": 6,
    "technician_id": null,
    "created_at": "2026-08-24T14:00:00",
    "updated_at": "2026-09-21T13:24:51",
    "resolved_at": null,
    "closed_at": null
  },
  {
    "id": 5,
    "title": "Bảo trì định kỳ máy chủ cơ sở dữ liệu",
    "description": "Thực hiện hút bụi, kiểm tra dung lượng ổ cứng và sao lưu database tháng 8.",
    "category": "MAINTENANCE",
    "priority": "MEDIUM",
    "status": "RESOLVED",
    "user_id": 3,
    "device_id": 5,
    "technician_id": 2,
    "created_at": "2026-08-24T11:30:00",
    "updated_at": "2026-09-21T13:24:51",
    "resolved_at": "2026-08-24T16:00:00",
    "closed_at": null
  },
  {
    "id": 4,
    "title": "Cài đặt phần mềm kế toán MISA mới",
    "description": "Cần cài đặt bản quyền phần mềm MISA 2026 cho máy tính kế toán viên mới.",
    "category": "SERVICE_REQUEST",
    "priority": "HIGH",
    "status": "ASSIGNED",
    "user_id": 4,
    "device_id": 1,
    "technician_id": 5,
    "created_at": "2026-08-24T10:45:00",
    "updated_at": "2026-09-21T13:24:51",
    "resolved_at": null,
    "closed_at": null
  },
  {
    "id": 3,
    "title": "Mất kết nối mạng toàn bộ phòng Nhân sự",
    "description": "Toàn bộ máy tính tầng 3 không thể truy cập internet và mạng nội bộ.",
    "category": "INCIDENT",
    "priority": "URGENT",
    "status": "IN_PROGRESS",
    "user_id": 6,
    "device_id": 7,
    "technician_id": 2,
    "created_at": "2026-08-24T10:00:00",
    "updated_at": "2026-09-21T13:24:51",
    "resolved_at": null,
    "closed_at": null
  },
  {
    "id": 2,
    "title": "Màn hình PC-001 không lên nguồn",
    "description": "Màn hình bật không lên tín hiệu, quạt máy tính vẫn quay. Đã thử đổi ổ cắm.",
    "category": "INCIDENT",
    "priority": "URGENT",
    "status": "OPEN",
    "user_id": 4,
    "device_id": 1,
    "technician_id": null,
    "created_at": "2026-08-24T09:15:00",
    "updated_at": "2026-09-21T13:24:51",
    "resolved_at": null,
    "closed_at": null
  },
  {
    "id": 1,
    "title": "Máy in không in được từ máy tính kế toán",
    "description": "Người dùng gửi lệnh in từ PC-001 nhưng máy in Canon không phản hồi, đèn báo nháy đỏ.",
    "category": "INCIDENT",
    "priority": "MEDIUM",
    "status": "CLOSED",
    "user_id": 3,
    "device_id": 2,
    "technician_id": 2,
    "created_at": "2026-08-24T08:30:00",
    "updated_at": "2026-09-21T13:24:51",
    "resolved_at": "2026-08-24T11:00:00",
    "closed_at": "2026-08-24T13:59:00"
  }
]
```

### `ADM-18` - Admin gán Kỹ thuật viên cho Ticket
- **Mô tả:** Gán ticket cho tech01, tự động chuyển OPEN -> ASSIGNED và ghi log history
- **Request:** `PATCH /api/tickets/2/assign`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `42.78 ms`
```json
// Request Body:
{
  "technician_id": 2
}
```
```json
// Response Body:
{
  "id": 2,
  "title": "Màn hình PC-001 không lên nguồn",
  "description": "Màn hình bật không lên tín hiệu, quạt máy tính vẫn quay. Đã thử đổi ổ cắm.",
  "category": "INCIDENT",
  "priority": "URGENT",
  "status": "ASSIGNED",
  "user_id": 4,
  "device_id": 1,
  "technician_id": 2,
  "created_at": "2026-08-24T09:15:00",
  "updated_at": "2026-09-21T13:24:52",
  "resolved_at": null,
  "closed_at": null
}
```

### `ADM-19` - Gán User không phải Kỹ thuật viên (Expect 400)
- **Mô tả:** User có role USER không thể được gán làm kỹ thuật viên
- **Request:** `PATCH /api/tickets/2/assign`
- **HTTP Status:** Kỳ vọng `400` | Thực tế `400` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `29.06 ms`
```json
// Request Body:
{
  "technician_id": 3
}
```
```json
// Response Body:
{
  "detail": "INVALID_TECHNICIAN_ROLE",
  "path": "/api/tickets/2/assign"
}
```

---

## 3. Kết luận và đánh giá luồng (Workflow Review)
- Toàn bộ các API thuộc vai trò `ADMIN` đã được kiểm thử cả Happy Path và Negative/Security Path.
- Luồng dữ liệu, mã trạng thái HTTP và cấu trúc JSON trả về hoàn toàn đúng theo API Contract và DB Schema của dự án.