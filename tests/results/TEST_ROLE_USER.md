# KẾT QUẢ KIỂM THỬ API CHI TIẾT — VAI TRÒ: USER
> **Thời gian chạy:** 2026-08-24 13:59:00  
> **Môi trường:** Local FastAPI (Python 3.12 + MySQL 8.0)  
> **Tổng số test cases:** 9 | **Thành công:** 9 | **Thất bại:** 0  
> **Đánh giá tổng thể:** **`PASSED`**

---

## 1. Bảng tóm tắt kết quả (Summary Table)

| ID | Tên kịch bản | Method | Endpoint | Expected | Actual | Thời gian | Trạng thái |
|:---|:---|:---:|:---|:---:|:---:|:---:|:---:|
| `USR-01` | Đăng nhập USER thành công | `POST` | `/api/login` | `200` | `200` | 250.66ms | ✅ PASS |
| `USR-02` | User tạo Ticket yêu cầu hỗ trợ mới | `POST` | `/api/tickets` | `201` | `201` | 16.71ms | ✅ PASS |
| `USR-03` | User xem danh sách Ticket của mình | `GET` | `/api/tickets` | `200` | `200` | 13.24ms | ✅ PASS |
| `USR-04` | User xem chi tiết Ticket của mình | `GET` | `/api/tickets/2` | `200` | `200` | 12.07ms | ✅ PASS |
| `USR-05` | User chỉnh sửa thông tin Ticket | `PATCH` | `/api/tickets/2` | `200` | `200` | 17.09ms | ✅ PASS |
| `USR-06` | User xem lịch sử xử lý Ticket | `GET` | `/api/tickets/2/history` | `200` | `200` | 11.89ms | ✅ PASS |
| `USR-07` | Security: User truy cập Quản lý Users (Expect 403) | `GET` | `/api/users` | `403` | `403` | 7.04ms | ✅ PASS |
| `USR-08` | Security: User thêm Thiết bị mới (Expect 403) | `POST` | `/api/devices` | `403` | `403` | 11.13ms | ✅ PASS |
| `USR-09` | Security: User gán Kỹ thuật viên (Expect 403) | `PATCH` | `/api/tickets/2/assign` | `403` | `403` | 8.92ms | ✅ PASS |

---

## 2. Chi tiết từng kịch bản kiểm thử (Request & Response Details)

### `USR-01` - Đăng nhập USER thành công
- **Mô tả:** Đăng nhập tài khoản user01
- **Request:** `POST /api/login`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `250.66 ms`
```json
// Request Body:
{
  "username": "user01",
  "password": "CS466@123"
}
```
```json
// Response Body:
{
  "access_token": "<redacted>",
  "token_type": "bearer",
  "user": {
    "id": 3,
    "username": "user01",
    "ho_ten": "Người dùng 01",
    "email": "user01@cs466.local",
    "vai_tro": "USER",
    "trang_thai": "ACTIVE"
  }
}
```

### `USR-02` - User tạo Ticket yêu cầu hỗ trợ mới
- **Mô tả:** Tạo ticket mới, trạng thái mặc định ban đầu là OPEN
- **Request:** `POST /api/tickets`
- **HTTP Status:** Kỳ vọng `201` | Thực tế `201` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `16.71 ms`
```json
// Request Body:
{
  "title": "Màn hình máy tính không lên nguồn",
  "description": "Bật nút nguồn màn hình PC-001 nhưng đèn không sáng, dây nguồn đã cắm chặt.",
  "device_id": 1,
  "category": "INCIDENT",
  "priority": "HIGH"
}
```
```json
// Response Body:
{
  "id": 2,
  "title": "Màn hình máy tính không lên nguồn",
  "description": "Bật nút nguồn màn hình PC-001 nhưng đèn không sáng, dây nguồn đã cắm chặt.",
  "category": "INCIDENT",
  "priority": "HIGH",
  "status": "OPEN",
  "user_id": 3,
  "device_id": 1,
  "technician_id": null,
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00",
  "resolved_at": null,
  "closed_at": null
}
```

### `USR-03` - User xem danh sách Ticket của mình
- **Mô tả:** User chỉ nhìn thấy các ticket do chính mình tạo, không thấy ticket của người khác
- **Request:** `GET /api/tickets`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `13.24 ms`
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
    "created_at": "2026-08-24T13:58:59",
    "updated_at": "2026-08-24T13:59:00",
    "resolved_at": null,
    "closed_at": null
  },
  {
    "id": 2,
    "title": "Màn hình máy tính không lên nguồn",
    "description": "Bật nút nguồn màn hình PC-001 nhưng đèn không sáng, dây nguồn đã cắm chặt.",
    "category": "INCIDENT",
    "priority": "HIGH",
    "status": "OPEN",
    "user_id": 3,
    "device_id": 1,
    "technician_id": null,
    "created_at": "2026-08-24T13:59:00",
    "updated_at": "2026-08-24T13:59:00",
    "resolved_at": null,
    "closed_at": null
  }
]
```

### `USR-04` - User xem chi tiết Ticket của mình
- **Mô tả:** Lấy chi tiết ticket kèm thông tin người tạo và thiết bị
- **Request:** `GET /api/tickets/2`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `12.07 ms`
```json
// Response Body:
{
  "id": 2,
  "title": "Màn hình máy tính không lên nguồn",
  "description": "Bật nút nguồn màn hình PC-001 nhưng đèn không sáng, dây nguồn đã cắm chặt.",
  "category": "INCIDENT",
  "priority": "HIGH",
  "status": "OPEN",
  "user_id": 3,
  "device_id": 1,
  "technician_id": null,
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00",
  "resolved_at": null,
  "closed_at": null,
  "creator": {
    "id": 3,
    "username": "user01",
    "ho_ten": "Người dùng 01",
    "email": "user01@cs466.local",
    "vai_tro": "USER",
    "trang_thai": "ACTIVE"
  },
  "device": {
    "id": 1,
    "ma_thiet_bi": "PC-001",
    "ten_thiet_bi": "Máy tính phòng Kế toán",
    "loai_thiet_bi": "COMPUTER",
    "vi_tri": "Phòng Kế toán",
    "trang_thai": "ACTIVE",
    "mo_ta": "Máy tính để bàn"
  },
  "technician": null
}
```

### `USR-05` - User chỉnh sửa thông tin Ticket
- **Mô tả:** Cập nhật tiêu đề và nâng mức ưu tiên
- **Request:** `PATCH /api/tickets/2`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `17.09 ms`
```json
// Request Body:
{
  "title": "Màn hình PC-001 không lên nguồn (Bổ sung: Đã thử đổi ổ cắm)",
  "priority": "URGENT"
}
```
```json
// Response Body:
{
  "id": 2,
  "title": "Màn hình PC-001 không lên nguồn (Bổ sung: Đã thử đổi ổ cắm)",
  "description": "Bật nút nguồn màn hình PC-001 nhưng đèn không sáng, dây nguồn đã cắm chặt.",
  "category": "INCIDENT",
  "priority": "URGENT",
  "status": "OPEN",
  "user_id": 3,
  "device_id": 1,
  "technician_id": null,
  "created_at": "2026-08-24T13:59:00",
  "updated_at": "2026-08-24T13:59:00",
  "resolved_at": null,
  "closed_at": null
}
```

### `USR-06` - User xem lịch sử xử lý Ticket
- **Mô tả:** Xem timeline các hành động CREATED, UPDATED của ticket
- **Request:** `GET /api/tickets/2/history`
- **HTTP Status:** Kỳ vọng `200` | Thực tế `200` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `11.89 ms`
```json
// Response Body:
[
  {
    "id": 3,
    "action": "CREATED",
    "old_status": null,
    "new_status": "OPEN",
    "detail": "Ticket created",
    "performed_by": 3,
    "performed_at": "2026-08-24T13:59:00"
  },
  {
    "id": 4,
    "action": "CLASSIFIED",
    "old_status": "OPEN",
    "new_status": "OPEN",
    "detail": "Updated fields: title, priority",
    "performed_by": 3,
    "performed_at": "2026-08-24T13:59:00"
  }
]
```

### `USR-07` - Security: User truy cập Quản lý Users (Expect 403)
- **Mô tả:** User không được phép truy cập module Users
- **Request:** `GET /api/users`
- **HTTP Status:** Kỳ vọng `403` | Thực tế `403` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `7.04 ms`
```json
// Response Body:
{
  "detail": "FORBIDDEN",
  "path": "/api/users"
}
```

### `USR-08` - Security: User thêm Thiết bị mới (Expect 403)
- **Mô tả:** User không được phép tạo thiết bị mới
- **Request:** `POST /api/devices`
- **HTTP Status:** Kỳ vọng `403` | Thực tế `403` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `11.13 ms`
```json
// Request Body:
{
  "ma_thiet_bi": "PC-HACK",
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

### `USR-09` - Security: User gán Kỹ thuật viên (Expect 403)
- **Mô tả:** User không được phép gán kỹ thuật viên
- **Request:** `PATCH /api/tickets/2/assign`
- **HTTP Status:** Kỳ vọng `403` | Thực tế `403` $\rightarrow$ **✅ PASS (Thành công)**
- **Thời gian xử lý:** `8.92 ms`
```json
// Request Body:
{
  "technician_id": 2
}
```
```json
// Response Body:
{
  "detail": "FORBIDDEN",
  "path": "/api/tickets/2/assign"
}
```

---

## 3. Kết luận và đánh giá luồng (Workflow Review)
- Toàn bộ các API thuộc vai trò `USER` đã được kiểm thử cả Happy Path và Negative/Security Path.
- Luồng dữ liệu, mã trạng thái HTTP và cấu trúc JSON trả về hoàn toàn đúng theo API Contract và DB Schema của dự án.