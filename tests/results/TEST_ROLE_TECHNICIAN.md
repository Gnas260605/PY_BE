# KẾT QUẢ KIỂM THỬ API CHI TIẾT — VAI TRÒ: TECHNICIAN
> **Thời gian chạy:** 2026-08-24 22:43:24  
> **Môi trường:** Local FastAPI (Python 3.12 + MySQL 8.0)  
> **Tổng số test cases:** 11 | **Thành công:** 11 | **Thất bại:** 0  
> **Đánh giá tổng thể:** **`PASSED`**

---

## 1. Bảng tóm tắt kết quả (Summary Table)

| ID | Tên kịch bản | Method | Endpoint | Expected | Actual | Thời gian | Trạng thái |
|:---|:---|:---:|:---|:---:|:---:|:---:|:---:|
| `TEC-01` | Đăng nhập TECHNICIAN thành công | `POST` | `/api/login` | `200` | `200` | 243.2ms | ✅ PASS |
| `TEC-02` | Tech xem danh sách Ticket được phân công | `GET` | `/api/tickets?status=ASSIGNED` | `200` | `200` | 11.79ms | ✅ PASS |
| `TEC-03` | Tech xem danh sách thiết bị | `GET` | `/api/devices` | `200` | `200` | 11.23ms | ✅ PASS |
| `TEC-04` | Tech cập nhật trạng thái thiết bị | `PATCH` | `/api/devices/1` | `200` | `200` | 15.4ms | ✅ PASS |
| `TEC-05` | Đổi trạng thái Ticket: ASSIGNED -> IN_PROGRESS | `PATCH` | `/api/tickets/1/status` | `200` | `200` | 16.09ms | ✅ PASS |
| `TEC-06` | Đổi trạng thái Ticket: IN_PROGRESS -> RESOLVED | `PATCH` | `/api/tickets/1/status` | `200` | `200` | 15.19ms | ✅ PASS |
| `TEC-07` | Chuyển trạng thái sai quy trình (RESOLVED -> OPEN Expect 400) | `PATCH` | `/api/tickets/1/status` | `400` | `400` | 11.15ms | ✅ PASS |
| `TEC-08` | Đóng Ticket đã giải quyết (RESOLVED -> CLOSED) | `PATCH` | `/api/tickets/1/close` | `200` | `200` | 15.69ms | ✅ PASS |
| `TEC-09` | Kiểm tra toàn bộ Lịch sử chu trình xử lý Ticket | `GET` | `/api/tickets/1/history` | `200` | `200` | 10.57ms | ✅ PASS |
| `TEC-10` | Security: Tech truy cập Quản lý Users (Expect 403) | `GET` | `/api/users` | `403` | `403` | 5.78ms | ✅ PASS |
| `TEC-11` | Security: Tech thêm Thiết bị mới (Expect 403) | `POST` | `/api/devices` | `403` | `403` | 7.16ms | ✅ PASS |

---

## 2. Chi tiết từng kịch bản kiểm thử (Request & Response Details)

### `TEC-01` - Đăng nhập TECHNICIAN thành công
- **Mô tả:** Đăng nhập tài khoản tech01
- **Request:** `POST /api/login`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `243.2 ms`
```json
// Request Body:
{
  "username": "tech01",
  "password": "CS466@123"
}
```
```json
// Response Body:
{
  "access_token": "<redacted>",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "tech01",
    "ho_ten": "Kỹ thuật viên 01",
    "email": "tech01@cs466.local",
    "vai_tro": "TECHNICIAN",
    "trang_thai": "ACTIVE"
  }
}
```

### `TEC-02` - Tech xem danh sách Ticket được phân công
- **Mô tả:** Lấy danh sách các ticket có trạng thái ASSIGNED
- **Request:** `GET /api/tickets?status=ASSIGNED`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `11.79 ms`
```json
// Response Body:
[
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
    "created_at": "2026-08-24T22:43:23",
    "updated_at": "2026-08-24T22:43:24",
    "resolved_at": null,
    "closed_at": null
  }
]
```

### `TEC-03` - Tech xem danh sách thiết bị
- **Mô tả:** Technician có quyền xem danh sách thiết bị để hỗ trợ bảo trì
- **Request:** `GET /api/devices`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `11.23 ms`
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
    "created_at": "2026-08-24T22:43:23",
    "updated_at": "2026-08-24T22:43:23"
  },
  {
    "id": 2,
    "ma_thiet_bi": "PRN-001",
    "ten_thiet_bi": "Máy in văn phòng",
    "loai_thiet_bi": "PRINTER",
    "vi_tri": "Văn phòng",
    "trang_thai": "MAINTENANCE",
    "mo_ta": "Máy in dùng chung",
    "created_at": "2026-08-24T22:43:23",
    "updated_at": "2026-08-24T22:43:23"
  },
  {
    "id": 3,
    "ma_thiet_bi": "RTR-001",
    "ten_thiet_bi": "Router tầng 2",
    "loai_thiet_bi": "ROUTER",
    "vi_tri": "Tầng 2",
    "trang_thai": "ACTIVE",
    "mo_ta": "Thiết bị mạng",
    "created_at": "2026-08-24T22:43:23",
    "updated_at": "2026-08-24T22:43:23"
  },
  {
    "id": 4,
    "ma_thiet_bi": "PC-002",
    "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
    "loai_thiet_bi": "COMPUTER",
    "vi_tri": "Phòng Kế Toán - Tầng 2",
    "trang_thai": "MAINTENANCE",
    "mo_ta": "Đang gửi bảo hành ổ cứng",
    "created_at": "2026-08-24T22:43:24",
    "updated_at": "2026-08-24T22:43:24"
  }
]
```

### `TEC-04` - Tech cập nhật trạng thái thiết bị
- **Mô tả:** Technician cập nhật trạng thái thiết bị sang MAINTENANCE
- **Request:** `PATCH /api/devices/1`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `15.4 ms`
```json
// Request Body:
{
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Đang kiểm tra màn hình tại chỗ"
}
```
```json
// Response Body:
{
  "id": 1,
  "ma_thiet_bi": "PC-001",
  "ten_thiet_bi": "Máy tính phòng Kế toán",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế toán",
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Đang kiểm tra màn hình tại chỗ",
  "created_at": "2026-08-24T22:43:23",
  "updated_at": "2026-08-24T22:43:25"
}
```

### `TEC-05` - Đổi trạng thái Ticket: ASSIGNED -> IN_PROGRESS
- **Mô tả:** Kỹ thuật viên bắt đầu xử lý sự cố
- **Request:** `PATCH /api/tickets/1/status`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `16.09 ms`
```json
// Request Body:
{
  "status": "IN_PROGRESS"
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
  "status": "IN_PROGRESS",
  "user_id": 3,
  "device_id": 2,
  "technician_id": 2,
  "created_at": "2026-08-24T22:43:23",
  "updated_at": "2026-08-24T22:43:25",
  "resolved_at": null,
  "closed_at": null
}
```

### `TEC-06` - Đổi trạng thái Ticket: IN_PROGRESS -> RESOLVED
- **Mô tả:** Kỹ thuật viên hoàn tất khắc phục sự cố
- **Request:** `PATCH /api/tickets/1/status`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `15.19 ms`
```json
// Request Body:
{
  "status": "RESOLVED"
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
  "status": "RESOLVED",
  "user_id": 3,
  "device_id": 2,
  "technician_id": 2,
  "created_at": "2026-08-24T22:43:23",
  "updated_at": "2026-08-24T22:43:25",
  "resolved_at": "2026-08-24T22:43:25",
  "closed_at": null
}
```

### `TEC-07` - Chuyển trạng thái sai quy trình (RESOLVED -> OPEN Expect 400)
- **Mô tả:** Không cho phép chuyển lùi từ RESOLVED về OPEN
- **Request:** `PATCH /api/tickets/1/status`
- **HTTP Status:** Kỳ vọng `400` | Thực tế `400` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `11.15 ms`
```json
// Request Body:
{
  "status": "OPEN"
}
```
```json
// Response Body:
{
  "detail": "INVALID_TRANSITION",
  "path": "/api/tickets/1/status"
}
```

### `TEC-08` - Đóng Ticket đã giải quyết (RESOLVED -> CLOSED)
- **Mô tả:** Đóng ticket hoàn tất và lưu ghi chú đóng
- **Request:** `PATCH /api/tickets/1/close`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `15.69 ms`
```json
// Request Body:
{
  "note": "Đã thay adapter nguồn màn hình mới, thiết bị hoạt động tốt."
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
  "status": "CLOSED",
  "user_id": 3,
  "device_id": 2,
  "technician_id": 2,
  "created_at": "2026-08-24T22:43:23",
  "updated_at": "2026-08-24T22:43:25",
  "resolved_at": "2026-08-24T22:43:25",
  "closed_at": "2026-08-24T22:43:25"
}
```

### `TEC-09` - Kiểm tra toàn bộ Lịch sử chu trình xử lý Ticket
- **Mô tả:** Xác nhận đủ 5 sự kiện: CREATED -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED
- **Request:** `GET /api/tickets/1/history`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `10.57 ms`
```json
// Response Body:
[
  {
    "id": 1,
    "action": "CREATED",
    "old_status": null,
    "new_status": "OPEN",
    "detail": "Ticket mẫu được tạo",
    "performed_by": 3,
    "performed_at": "2026-08-24T22:43:23"
  },
  {
    "id": 2,
    "action": "ASSIGNED",
    "old_status": "OPEN",
    "new_status": "ASSIGNED",
    "detail": "Assigned technician_id=2",
    "performed_by": 1,
    "performed_at": "2026-08-24T22:43:24"
  },
  {
    "id": 5,
    "action": "STATUS_CHANGED",
    "old_status": "ASSIGNED",
    "new_status": "IN_PROGRESS",
    "detail": "Status changed to IN_PROGRESS",
    "performed_by": 2,
    "performed_at": "2026-08-24T22:43:25"
  },
  {
    "id": 6,
    "action": "STATUS_CHANGED",
    "old_status": "IN_PROGRESS",
    "new_status": "RESOLVED",
    "detail": "Status changed to RESOLVED",
    "performed_by": 2,
    "performed_at": "2026-08-24T22:43:25"
  },
  {
    "id": 7,
    "action": "CLOSED",
    "old_status": "RESOLVED",
    "new_status": "CLOSED",
    "detail": "Đã thay adapter nguồn màn hình mới, thiết bị hoạt động tốt.",
    "performed_by": 2,
    "performed_at": "2026-08-24T22:43:25"
  }
]
```

### `TEC-10` - Security: Tech truy cập Quản lý Users (Expect 403)
- **Mô tả:** Technician không được phép quản lý Users
- **Request:** `GET /api/users`
- **HTTP Status:** Kỳ vọng `403` | Thực tế `403` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `5.78 ms`
```json
// Response Body:
{
  "detail": "FORBIDDEN",
  "path": "/api/users"
}
```

### `TEC-11` - Security: Tech thêm Thiết bị mới (Expect 403)
- **Mô tả:** Technician không được phép thêm thiết bị mới (chỉ ADMIN)
- **Request:** `POST /api/devices`
- **HTTP Status:** Kỳ vọng `403` | Thực tế `403` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `7.16 ms`
```json
// Request Body:
{
  "ma_thiet_bi": "PC-TECH",
  "ten_thiet_bi": "Test"
}
```
```json
// Response Body:
{
  "detail": "FORBIDDEN",
  "path": "/api/devices"
}
```

---

## 3. Kết luận và đánh giá luồng (Workflow Review)
- Toàn bộ các API thuộc vai trò `TECHNICIAN` đã được kiểm thử cả Happy Path và Negative/Security Path.
- Luồng dữ liệu, mã trạng thái HTTP và cấu trúc JSON trả về hoàn toàn đúng theo API Contract và DB Schema của dự án.