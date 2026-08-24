# KẾT QUẢ KIỂM THỬ API CHI TIẾT — VAI TRÒ: ADMIN
> **Thời gian chạy:** 2026-08-24 13:58:59  
> **Môi trường:** Local FastAPI (Python 3.12 + MySQL 8.0)  
> **Tổng số test cases:** 19 | **Thành công:** 19 | **Thất bại:** 0  
> **Đánh giá tổng thể:** **`PASSED`**

---

## 1. Bảng tóm tắt kết quả (Summary Table)

| ID | Tên kịch bản | Method | Endpoint | Expected | Actual | Thời gian | Trạng thái |
|:---|:---|:---:|:---|:---:|:---:|:---:|:---:|
| `ADM-01` | Kiểm tra Healthcheck hệ thống | `GET` | `/api/health` | `200` | `200` | 19.09ms | ✅ PASS |
| `ADM-02` | Đăng nhập ADMIN thành công | `POST` | `/api/login` | `200` | `200` | 246.38ms | ✅ PASS |
| `ADM-03` | Đăng nhập sai mật khẩu | `POST` | `/api/login` | `401` | `401` | 221.89ms | ✅ PASS |
| `ADM-04` | Lấy danh sách Users (Hỗ trợ lọc & tìm kiếm) | `GET` | `/api/users?role=USER&status=ACTIVE` | `200` | `200` | 12.69ms | ✅ PASS |
| `ADM-05` | Tạo User mới (user02) | `POST` | `/api/users` | `201` | `201` | 247.03ms | ✅ PASS |
| `ADM-06` | Tạo User trùng Username (Expect 409) | `POST` | `/api/users` | `409` | `409` | 15.46ms | ✅ PASS |
| `ADM-07` | Xem chi tiết User vừa tạo | `GET` | `/api/users/4` | `200` | `200` | 13.14ms | ✅ PASS |
| `ADM-08` | Cập nhật thông tin User | `PATCH` | `/api/users/4` | `200` | `200` | 19.8ms | ✅ PASS |
| `ADM-09` | Vô hiệu hóa User (INACTIVE) | `PATCH` | `/api/users/4/status` | `200` | `200` | 17.99ms | ✅ PASS |
| `ADM-10` | Đăng nhập bằng tài khoản INACTIVE (Expect 401) | `POST` | `/api/login` | `401` | `401` | 8.54ms | ✅ PASS |
| `ADM-11` | Kích hoạt lại User (ACTIVE) | `PATCH` | `/api/users/4/status` | `200` | `200` | 20.29ms | ✅ PASS |
| `ADM-12` | Thêm thiết bị mới (PC-002) | `POST` | `/api/devices` | `201` | `201` | 20.69ms | ✅ PASS |
| `ADM-13` | Thêm thiết bị trùng Mã (Expect 409) | `POST` | `/api/devices` | `409` | `409` | 15.2ms | ✅ PASS |
| `ADM-14` | Lấy danh sách thiết bị | `GET` | `/api/devices?status=ACTIVE&keyword=PC` | `200` | `200` | 14.46ms | ✅ PASS |
| `ADM-15` | Xem chi tiết thiết bị | `GET` | `/api/devices/4` | `200` | `200` | 15.61ms | ✅ PASS |
| `ADM-16` | Cập nhật thông tin & trạng thái thiết bị | `PATCH` | `/api/devices/4` | `200` | `200` | 21.6ms | ✅ PASS |
| `ADM-17` | Admin xem toàn bộ Ticket trong hệ thống | `GET` | `/api/tickets` | `200` | `200` | 15.3ms | ✅ PASS |
| `ADM-18` | Admin gán Kỹ thuật viên cho Ticket | `PATCH` | `/api/tickets/1/assign` | `200` | `200` | 18.74ms | ✅ PASS |
| `ADM-19` | Gán User không phải Kỹ thuật viên (Expect 400) | `PATCH` | `/api/tickets/1/assign` | `400` | `400` | 14.98ms | ✅ PASS |

---

## 2. Chi tiết từng kịch bản kiểm thử (Request & Response Details)

### `ADM-01` - Kiểm tra Healthcheck hệ thống
- **Mô tả:** Xác nhận server và kết nối MySQL hoạt động bình thường
- **Request:** `GET /api/health`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `19.09 ms`
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
- **Thời gian xử lý:** `246.38 ms`
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
- **Thời gian xử lý:** `221.89 ms`
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
- **Thời gian xử lý:** `12.69 ms`
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
    "created_at": "2026-08-24T13:58:59",
    "updated_at": "2026-08-24T13:58:59"
  }
]
```

### `ADM-05` - Tạo User mới (user02)
- **Mô tả:** Tạo người dùng mới với mật khẩu bcrypt, không trả về password_hash
- **Request:** `POST /api/users`
- **HTTP Status:** Kỳ vọng `201` | Thực tế `201` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `247.03 ms`
```json
// Request Body:
{
  "username": "user02",
  "password": "CS466@123",
  "ho_ten": "Nguyễn Văn B",
  "email": "user02@cs466.local",
  "vai_tro": "USER"
}
```
```json
// Response Body:
{
  "id": 4,
  "username": "user02",
  "ho_ten": "Nguyễn Văn B",
  "email": "user02@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00"
}
```

### `ADM-06` - Tạo User trùng Username (Expect 409)
- **Mô tả:** Kỳ vọng 409 Conflict khi username đã tồn tại
- **Request:** `POST /api/users`
- **HTTP Status:** Kỳ vọng `409` | Thực tế `409` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `15.46 ms`
```json
// Request Body:
{
  "username": "user02",
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
- **Request:** `GET /api/users/4`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `13.14 ms`
```json
// Response Body:
{
  "id": 4,
  "username": "user02",
  "ho_ten": "Nguyễn Văn B",
  "email": "user02@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00"
}
```

### `ADM-08` - Cập nhật thông tin User
- **Mô tả:** Cập nhật họ tên và email của user
- **Request:** `PATCH /api/users/4`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `19.8 ms`
```json
// Request Body:
{
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "ketoan_b@cs466.local",
  "vai_tro": "USER"
}
```
```json
// Response Body:
{
  "id": 4,
  "username": "user02",
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "ketoan_b@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00"
}
```

### `ADM-09` - Vô hiệu hóa User (INACTIVE)
- **Mô tả:** Khóa tài khoản user sang trạng thái INACTIVE
- **Request:** `PATCH /api/users/4/status`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `17.99 ms`
```json
// Request Body:
{
  "status": "INACTIVE"
}
```
```json
// Response Body:
{
  "id": 4,
  "username": "user02",
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "ketoan_b@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "INACTIVE",
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00"
}
```

### `ADM-10` - Đăng nhập bằng tài khoản INACTIVE (Expect 401)
- **Mô tả:** Tài khoản INACTIVE không được phép đăng nhập
- **Request:** `POST /api/login`
- **HTTP Status:** Kỳ vọng `401` | Thực tế `401` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `8.54 ms`
```json
// Request Body:
{
  "username": "user02",
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
- **Request:** `PATCH /api/users/4/status`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `20.29 ms`
```json
// Request Body:
{
  "status": "ACTIVE"
}
```
```json
// Response Body:
{
  "id": 4,
  "username": "user02",
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "ketoan_b@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00"
}
```

### `ADM-12` - Thêm thiết bị mới (PC-002)
- **Mô tả:** Admin thêm thiết bị mới vào hệ thống
- **Request:** `POST /api/devices`
- **HTTP Status:** Kỳ vọng `201` | Thực tế `201` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `20.69 ms`
```json
// Request Body:
{
  "ma_thiet_bi": "PC-002",
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
  "id": 4,
  "ma_thiet_bi": "PC-002",
  "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế Toán - Tầng 2",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Optiplex i7 16GB",
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00"
}
```

### `ADM-13` - Thêm thiết bị trùng Mã (Expect 409)
- **Mô tả:** Kỳ vọng 409 Conflict khi mã thiết bị đã tồn tại
- **Request:** `POST /api/devices`
- **HTTP Status:** Kỳ vọng `409` | Thực tế `409` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `15.2 ms`
```json
// Request Body:
{
  "ma_thiet_bi": "PC-002",
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
- **Thời gian xử lý:** `14.46 ms`
```json
// Response Body:
[
  {
    "id": 1,
    "ma_thiet_bi": "PC-001",
    "ten_thiet_bi": "Máy tính phòng Kế toán",
    "loai_thiet_bi": "COMPUTER",
    "vi_tri": "Phòng Kế toán",
    "trang_thai": "ACTIVE",
    "mo_ta": "Máy tính để bàn",
    "created_at": "2026-08-24T13:58:59",
    "updated_at": "2026-08-24T13:58:59"
  },
  {
    "id": 4,
    "ma_thiet_bi": "PC-002",
    "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
    "loai_thiet_bi": "COMPUTER",
    "vi_tri": "Phòng Kế Toán - Tầng 2",
    "trang_thai": "ACTIVE",
    "mo_ta": "Dell Optiplex i7 16GB",
    "created_at": "2026-08-24T13:59:00",
    "updated_at": "2026-08-24T13:59:00"
  }
]
```

### `ADM-15` - Xem chi tiết thiết bị
- **Mô tả:** Lấy thông tin chi tiết thiết bị
- **Request:** `GET /api/devices/4`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `15.61 ms`
```json
// Response Body:
{
  "id": 4,
  "ma_thiet_bi": "PC-002",
  "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế Toán - Tầng 2",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Optiplex i7 16GB",
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00"
}
```

### `ADM-16` - Cập nhật thông tin & trạng thái thiết bị
- **Mô tả:** Đổi trạng thái thiết bị sang MAINTENANCE
- **Request:** `PATCH /api/devices/4`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `21.6 ms`
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
  "id": 4,
  "ma_thiet_bi": "PC-002",
  "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế Toán - Tầng 2",
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Đang gửi bảo hành ổ cứng",
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00"
}
```

### `ADM-17` - Admin xem toàn bộ Ticket trong hệ thống
- **Mô tả:** Admin có quyền xem mọi ticket của toàn bộ người dùng
- **Request:** `GET /api/tickets`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `15.3 ms`
```json
// Response Body:
[
  {
    "id": 1,
    "title": "Máy in không in được",
    "description": "Người dùng gửi lệnh in nhưng máy không phản hồi.",
    "category": "INCIDENT",
    "priority": "MEDIUM",
    "status": "OPEN",
    "user_id": 3,
    "device_id": 2,
    "technician_id": null,
    "created_at": "2026-08-24T13:58:59",
    "updated_at": "2026-08-24T13:58:59",
    "resolved_at": null,
    "closed_at": null
  }
]
```

### `ADM-18` - Admin gán Kỹ thuật viên cho Ticket
- **Mô tả:** Gán ticket cho tech01, tự động chuyển OPEN -> ASSIGNED và ghi log history
- **Request:** `PATCH /api/tickets/1/assign`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `18.74 ms`
```json
// Request Body:
{
  "technician_id": 2
}
```
```json
// Response Body:
{
  "id": 1,
  "title": "Máy in không in được",
  "description": "Người dùng gửi lệnh in nhưng máy không phản hồi.",
  "category": "INCIDENT",
  "priority": "MEDIUM",
  "status": "ASSIGNED",
  "user_id": 3,
  "device_id": 2,
  "technician_id": 2,
  "created_at": "2026-08-24T13:58:59",
  "updated_at": "2026-08-24T13:59:00",
  "resolved_at": null,
  "closed_at": null
}
```

### `ADM-19` - Gán User không phải Kỹ thuật viên (Expect 400)
- **Mô tả:** User có role USER không thể được gán làm kỹ thuật viên
- **Request:** `PATCH /api/tickets/1/assign`
- **HTTP Status:** Kỳ vọng `400` | Thực tế `400` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `14.98 ms`
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
  "path": "/api/tickets/1/assign"
}
```

---

## 3. Kết luận và đánh giá luồng (Workflow Review)
- Toàn bộ các API thuộc vai trò `ADMIN` đã được kiểm thử cả Happy Path và Negative/Security Path.
- Luồng dữ liệu, mã trạng thái HTTP và cấu trúc JSON trả về hoàn toàn đúng theo API Contract và DB Schema của dự án.