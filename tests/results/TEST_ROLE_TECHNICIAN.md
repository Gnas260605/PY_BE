# KẾT QUẢ KIỂM THỬ API CHI TIẾT — VAI TRÒ: TECHNICIAN
> **Commit SHA:** `bf51d53f57ba2e0ac537dd1b349122e3400f28c4`  
> **Thời gian chạy:** 2026-09-21 20:24:53  
> **Môi trường:** Local FastAPI (Python 3.12 + MySQL 8.0)  
> **Tổng số test cases:** 11 | **Thành công:** 11 | **Thất bại:** 0  
> **Đánh giá tổng thể:** **`PASSED`**

---

## 1. Bảng tóm tắt kết quả (Summary Table)

| ID | Tên kịch bản | Method | Endpoint | Expected | Actual | Thời gian | Trạng thái |
|:---|:---|:---:|:---|:---:|:---:|:---:|:---:|
| `TEC-01` | Đăng nhập TECHNICIAN thành công | `POST` | `/api/login` | `200` | `200` | 387.58ms | ✅ PASS |
| `TEC-02` | Tech xem danh sách Ticket được phân công | `GET` | `/api/tickets?status=ASSIGNED` | `200` | `200` | 41.01ms | ✅ PASS |
| `TEC-03` | Tech xem danh sách thiết bị | `GET` | `/api/devices` | `200` | `200` | 25.35ms | ✅ PASS |
| `TEC-04` | Tech cập nhật trạng thái thiết bị | `PATCH` | `/api/devices/1` | `200` | `200` | 52.15ms | ✅ PASS |
| `TEC-05` | Đổi trạng thái Ticket: ASSIGNED -> IN_PROGRESS | `PATCH` | `/api/tickets/2/status` | `200` | `200` | 110.7ms | ✅ PASS |
| `TEC-06` | Đổi trạng thái Ticket: IN_PROGRESS -> RESOLVED | `PATCH` | `/api/tickets/2/status` | `200` | `200` | 161.49ms | ✅ PASS |
| `TEC-07` | Chuyển trạng thái sai quy trình (RESOLVED -> OPEN Expect 400) | `PATCH` | `/api/tickets/2/status` | `400` | `400` | 101.79ms | ✅ PASS |
| `TEC-08` | Đóng Ticket đã giải quyết (RESOLVED -> CLOSED) | `PATCH` | `/api/tickets/2/close` | `200` | `200` | 117.66ms | ✅ PASS |
| `TEC-09` | Kiểm tra toàn bộ Lịch sử chu trình xử lý Ticket | `GET` | `/api/tickets/2/history` | `200` | `200` | 36.87ms | ✅ PASS |
| `TEC-10` | Security: Tech truy cập Quản lý Users (Expect 403) | `GET` | `/api/users` | `403` | `403` | 82.0ms | ✅ PASS |
| `TEC-11` | Security: Tech thêm Thiết bị mới (Expect 403) | `POST` | `/api/devices` | `403` | `403` | 63.23ms | ✅ PASS |

---

## 2. Chi tiết từng kịch bản kiểm thử (Request & Response Details)

### `TEC-01` - Đăng nhập TECHNICIAN thành công
- **Mô tả:** Đăng nhập tài khoản tech01
- **Request:** `POST /api/login`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `387.58 ms`
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
- **Thời gian xử lý:** `41.01 ms`
```json
// Response Body:
[
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
]
```

### `TEC-03` - Tech xem danh sách thiết bị
- **Mô tả:** Technician có quyền xem danh sách thiết bị để hỗ trợ bảo trì
- **Request:** `GET /api/devices`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `25.35 ms`
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
    "id": 2,
    "ma_thiet_bi": "PRN-001",
    "ten_thiet_bi": "Máy in laser văn phòng",
    "loai_thiet_bi": "PRINTER",
    "vi_tri": "Hành lang Tầng 2",
    "trang_thai": "MAINTENANCE",
    "mo_ta": "Canon LBP 2900 đa năng",
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  },
  {
    "id": 3,
    "ma_thiet_bi": "RTR-001",
    "ten_thiet_bi": "Router Cisco Core Tầng 2",
    "loai_thiet_bi": "ROUTER",
    "vi_tri": "Phòng Server Tầng 2",
    "trang_thai": "ACTIVE",
    "mo_ta": "Cisco RV340 Dual WAN VPN",
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
    "id": 5,
    "ma_thiet_bi": "SRV-001",
    "ten_thiet_bi": "Máy chủ Database Chính",
    "loai_thiet_bi": "SERVER",
    "vi_tri": "Phòng Server Tầng 2",
    "trang_thai": "ACTIVE",
    "mo_ta": "Dell PowerEdge R740 64GB RAM",
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  },
  {
    "id": 6,
    "ma_thiet_bi": "PRN-002",
    "ten_thiet_bi": "Máy in màu phòng Thiết kế",
    "loai_thiet_bi": "PRINTER",
    "vi_tri": "Phòng Design - Tầng 4",
    "trang_thai": "ACTIVE",
    "mo_ta": "Epson L8056 Wifi",
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  },
  {
    "id": 7,
    "ma_thiet_bi": "SW-001",
    "ten_thiet_bi": "Switch mạng tầng 3",
    "loai_thiet_bi": "SWITCH",
    "vi_tri": "Hộp kỹ thuật Tầng 3",
    "trang_thai": "ACTIVE",
    "mo_ta": "TP-Link 24-Port Gigabit Switch",
    "created_at": "2026-09-21T13:24:51",
    "updated_at": "2026-09-21T13:24:51"
  },
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
]
```

### `TEC-04` - Tech cập nhật trạng thái thiết bị
- **Mô tả:** Technician cập nhật trạng thái thiết bị sang MAINTENANCE
- **Request:** `PATCH /api/devices/1`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `52.15 ms`
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
  "ten_thiet_bi": "Máy tính phòng Kế toán 01",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế toán - Tầng 2",
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Đang kiểm tra màn hình tại chỗ",
  "created_at": "2026-09-21T13:24:51",
  "updated_at": "2026-09-21T13:24:54"
}
```

### `TEC-05` - Đổi trạng thái Ticket: ASSIGNED -> IN_PROGRESS
- **Mô tả:** Kỹ thuật viên bắt đầu xử lý sự cố
- **Request:** `PATCH /api/tickets/2/status`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `110.7 ms`
```json
// Request Body:
{
  "status": "IN_PROGRESS"
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
  "status": "IN_PROGRESS",
  "user_id": 4,
  "device_id": 1,
  "technician_id": 2,
  "created_at": "2026-08-24T09:15:00",
  "updated_at": "2026-09-21T13:24:54",
  "resolved_at": null,
  "closed_at": null
}
```

### `TEC-06` - Đổi trạng thái Ticket: IN_PROGRESS -> RESOLVED
- **Mô tả:** Kỹ thuật viên hoàn tất khắc phục sự cố
- **Request:** `PATCH /api/tickets/2/status`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `161.49 ms`
```json
// Request Body:
{
  "status": "RESOLVED"
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
  "status": "RESOLVED",
  "user_id": 4,
  "device_id": 1,
  "technician_id": 2,
  "created_at": "2026-08-24T09:15:00",
  "updated_at": "2026-09-21T13:24:54",
  "resolved_at": "2026-09-21T13:24:54",
  "closed_at": null
}
```

### `TEC-07` - Chuyển trạng thái sai quy trình (RESOLVED -> OPEN Expect 400)
- **Mô tả:** Không cho phép chuyển lùi từ RESOLVED về OPEN
- **Request:** `PATCH /api/tickets/2/status`
- **HTTP Status:** Kỳ vọng `400` | Thực tế `400` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `101.79 ms`
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
  "path": "/api/tickets/2/status"
}
```

### `TEC-08` - Đóng Ticket đã giải quyết (RESOLVED -> CLOSED)
- **Mô tả:** Đóng ticket hoàn tất và lưu ghi chú đóng
- **Request:** `PATCH /api/tickets/2/close`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `117.66 ms`
```json
// Request Body:
{
  "note": "Đã thay adapter nguồn màn hình mới, thiết bị hoạt động tốt."
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
  "status": "CLOSED",
  "user_id": 4,
  "device_id": 1,
  "technician_id": 2,
  "created_at": "2026-08-24T09:15:00",
  "updated_at": "2026-09-21T13:24:54",
  "resolved_at": "2026-09-21T13:24:54",
  "closed_at": "2026-09-21T13:24:54"
}
```

### `TEC-09` - Kiểm tra toàn bộ Lịch sử chu trình xử lý Ticket
- **Mô tả:** Xác nhận đủ 5 sự kiện: CREATED -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED
- **Request:** `GET /api/tickets/2/history`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `36.87 ms`
```json
// Response Body:
[
  {
    "id": 6,
    "action": "CREATED",
    "old_status": null,
    "new_status": "OPEN",
    "detail": "Khởi tạo sự cố màn hình không nguồn",
    "performed_by": 4,
    "performed_at": "2026-08-24T09:15:00"
  },
  {
    "id": 10,
    "action": "ASSIGNED",
    "old_status": "OPEN",
    "new_status": "ASSIGNED",
    "detail": "Assigned technician_id=2",
    "performed_by": 1,
    "performed_at": "2026-09-21T13:24:52"
  },
  {
    "id": 13,
    "action": "STATUS_CHANGED",
    "old_status": "ASSIGNED",
    "new_status": "IN_PROGRESS",
    "detail": "Status changed to IN_PROGRESS",
    "performed_by": 2,
    "performed_at": "2026-09-21T13:24:54"
  },
  {
    "id": 14,
    "action": "STATUS_CHANGED",
    "old_status": "IN_PROGRESS",
    "new_status": "RESOLVED",
    "detail": "Status changed to RESOLVED",
    "performed_by": 2,
    "performed_at": "2026-09-21T13:24:54"
  },
  {
    "id": 15,
    "action": "CLOSED",
    "old_status": "RESOLVED",
    "new_status": "CLOSED",
    "detail": "Đã thay adapter nguồn màn hình mới, thiết bị hoạt động tốt.",
    "performed_by": 2,
    "performed_at": "2026-09-21T13:24:54"
  }
]
```

### `TEC-10` - Security: Tech truy cập Quản lý Users (Expect 403)
- **Mô tả:** Technician không được phép quản lý Users
- **Request:** `GET /api/users`
- **HTTP Status:** Kỳ vọng `403` | Thực tế `403` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `82.0 ms`
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
- **Thời gian xử lý:** `63.23 ms`
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