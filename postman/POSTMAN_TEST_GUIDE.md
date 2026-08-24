# HƯỚNG DẪN KIỂM THỬ TOÀN BỘ API VỚI POSTMAN THEO TỪNG ROLE
> **Dự án:** CS466 - Hệ thống quản lý bảo trì và yêu cầu dịch vụ CNTT  
> **Dành cho:** QA / Tester (Ngô Đức Minh Quân) & Developers  
> **Base URL:** `http://127.0.0.1:8000/api`  
> **Mật khẩu demo chung:** `CS466@123`

---

## 1. Thiết lập môi trường (Postman Environment)

Tạo một **Environment** mới trong Postman (ví dụ: `CS466_Local`) và cấu hình các biến sau:

| Variable Name | Initial Value | Current Value | Ghi chú |
|:---|:---|:---|:---|
| `baseUrl` | `http://127.0.0.1:8000/api` | `http://127.0.0.1:8000/api` | Base URL của Backend |
| `admin_token` | *(để trống)* | *(tự động lưu khi login)* | Token của tài khoản Admin |
| `tech_token` | *(để trống)* | *(tự động lưu khi login)* | Token của tài khoản Technician |
| `user_token` | *(để trống)* | *(tự động lưu khi login)* | Token của tài khoản User |
| `created_user_id` | `4` | `4` | ID user tạo trong bài test |
| `created_device_id`| `4` | `4` | ID device tạo trong bài test |
| `created_ticket_id`| `2` | `2` | ID ticket tạo trong bài test |

> **Mẹo tự động lưu Token trong Postman:**  
> Ở tab **Tests** của Request `POST /api/login`, chèn đoạn script:
> ```javascript
> if (pm.response.code === 200) {
>     const data = pm.response.json();
>     if (data.vai_tro === "ADMIN") pm.environment.set("admin_token", data.token);
>     if (data.vai_tro === "TECHNICIAN") pm.environment.set("tech_token", data.token);
>     if (data.vai_tro === "USER") pm.environment.set("user_token", data.token);
> }
> ```

---

## 2. Kịch bản kiểm thử chi tiết theo từng Role

```
                     ┌──────────────────────────────────────┐
                     │     PHASE 1: HEALTH & PUBLIC AUTH    │
                     └──────────────────┬───────────────────┘
                                        │
        ┌───────────────────────────────┼──────────────────────────────┐
        ▼                               ▼                              ▼
┌───────────────┐               ┌───────────────┐              ┌───────────────┐
│PHASE 2: ADMIN │               │ PHASE 3: USER │              │ PHASE 4: TECH │
│- User CRUD    │               │- Create Ticket│              │- Assigned Tkts│
│- Device CRUD  │               │- My Tickets   │              │- IN_PROGRESS  │
│- Assign Tech  │               │- View History │              │- RESOLVED     │
│- Close Ticket │               │- Check 403    │              │- Close / Devs │
└───────────────┘               └───────────────┘              └───────────────┘
```

---

### 🟢 GIAI ĐOẠN 1: Kiểm tra Hệ thống & Xác thực cơ bản (Public)

#### Request 1.1: Healthcheck
- **Method / URL:** `GET {{baseUrl}}/health`
- **Headers:** *(Không cần)*
- **Kỳ vọng:** `200 OK`, body: `{"status": "ok"}`

#### Request 1.2: Login sai mật khẩu (Negative Test)
- **Method / URL:** `POST {{baseUrl}}/login`
- **Body (raw JSON):**
```json
{
  "username": "admin",
  "password": "WrongPassword123"
}
```
- **Kỳ vọng:** `401 Unauthorized`, body: `{"detail": "INVALID_CREDENTIALS"}`

#### Request 1.3: Login thiếu trường dữ liệu (Validation Test)
- **Method / URL:** `POST {{baseUrl}}/login`
- **Body (raw JSON):**
```json
{
  "username": "admin"
}
```
- **Kỳ vọng:** `400 Bad Request`

---

### 🔴 GIAI ĐOẠN 2: Kiểm thử vai trò ADMIN (Toàn quyền quản trị)

#### Bước 2.1: Đăng nhập lấy Admin Token
- **Method / URL:** `POST {{baseUrl}}/login`
- **Body:** `{"username": "admin", "password": "CS466@123"}`
- **Kỳ vọng:** `200 OK`, lưu `admin_token`.

---

#### 👤 [ADMIN] Quản lý Người dùng (User Management)

#### Request 2.2: Lấy danh sách Users (Hỗ trợ lọc & tìm kiếm)
- **Method / URL:** `GET {{baseUrl}}/users?role=USER&status=ACTIVE&keyword=user`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Kỳ vọng:** `200 OK`, trả về danh sách `[]`.

#### Request 2.3: Tạo User mới hợp lệ
- **Method / URL:** `POST {{baseUrl}}/users`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body (raw JSON):**
```json
{
  "username": "user02",
  "password": "CS466@123",
  "ho_ten": "Nguyễn Văn B",
  "email": "user02@cs466.local",
  "vai_tro": "USER"
}
```
- **Kỳ vọng:** `201 Created`, trả về thông tin User (không có `password_hash`). Lưu `created_user_id`.

#### Request 2.4: Thử tạo trùng Username (Negative Test - Duplicate)
- **Method / URL:** `POST {{baseUrl}}/users`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body:** *(Giống Request 2.3)*
- **Kỳ vọng:** `409 Conflict`, body: `{"detail": "DUPLICATE_USERNAME"}`

#### Request 2.5: Xem chi tiết User vừa tạo
- **Method / URL:** `GET {{baseUrl}}/users/{{created_user_id}}`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Kỳ vọng:** `200 OK`.

#### Request 2.6: Cập nhật thông tin User
- **Method / URL:** `PATCH {{baseUrl}}/users/{{created_user_id}}`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body (raw JSON):**
```json
{
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "ketoan_b@cs466.local",
  "vai_tro": "USER"
}
```
- **Kỳ vọng:** `200 OK`, thông tin cập nhật chính xác.

#### Request 2.7: Vô hiệu hóa tài khoản (Deactivate User)
- **Method / URL:** `PATCH {{baseUrl}}/users/{{created_user_id}}/status`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body (raw JSON):**
```json
{
  "status": "INACTIVE"
}
```
- **Kỳ vọng:** `200 OK`, `trang_thai: "INACTIVE"`.

#### Request 2.8: Thử Login với tài khoản vừa bị vô hiệu hóa
- **Method / URL:** `POST {{baseUrl}}/login`
- **Body:** `{"username": "user02", "password": "CS466@123"}`
- **Kỳ vọng:** `401 Unauthorized`, body: `{"detail": "ACCOUNT_INACTIVE"}`.

#### Request 2.9: Kích hoạt lại tài khoản (Re-activate User)
- **Method / URL:** `PATCH {{baseUrl}}/users/{{created_user_id}}/status`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body:** `{"status": "ACTIVE"}`
- **Kỳ vọng:** `200 OK`, `trang_thai: "ACTIVE"`.

---

#### 💻 [ADMIN] Quản lý Thiết bị (Device Management)

#### Request 2.10: Thêm thiết bị mới
- **Method / URL:** `POST {{baseUrl}}/devices`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body (raw JSON):**
```json
{
  "ma_thiet_bi": "PC-002",
  "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Kế Toán - Tầng 2",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Vostro i5 16GB"
}
```
- **Kỳ vọng:** `201 Created`. Lưu `created_device_id`.

#### Request 2.11: Thử thêm trùng Mã thiết bị (Duplicate Code)
- **Method / URL:** `POST {{baseUrl}}/devices`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body:** *(Giống Request 2.10)*
- **Kỳ vọng:** `409 Conflict`, body: `{"detail": "DUPLICATE_DEVICE_CODE"}`.

#### Request 2.12: Lấy danh sách thiết bị
- **Method / URL:** `GET {{baseUrl}}/devices?status=ACTIVE&keyword=PC`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Kỳ vọng:** `200 OK`.

#### Request 2.13: Cập nhật trạng thái thiết bị sang Bảo trì
- **Method / URL:** `PATCH {{baseUrl}}/devices/{{created_device_id}}`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body (raw JSON):**
```json
{
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Đang gửi bảo hành ổ cứng"
}
```
- **Kỳ vọng:** `200 OK`.

---

### 🔵 GIAI ĐOẠN 3: Kiểm thử vai trò USER (Người dùng tạo & theo dõi Ticket)

#### Bước 3.1: Đăng nhập lấy User Token
- **Method / URL:** `POST {{baseUrl}}/login`
- **Body:** `{"username": "user01", "password": "CS466@123"}`
- **Kỳ vọng:** `200 OK`, lưu `user_token`.

#### Request 3.2: User tạo Ticket yêu cầu hỗ trợ mới
- **Method / URL:** `POST {{baseUrl}}/tickets`
- **Headers:** `Authorization: Bearer {{user_token}}`
- **Body (raw JSON):**
```json
{
  "title": "Màn hình máy tính không lên nguồn",
  "description": "Bật nút nguồn màn hình PC-001 nhưng đèn không sáng, dây nguồn đã cắm chặt.",
  "device_id": 1,
  "category": "INCIDENT",
  "priority": "HIGH"
}
```
- **Kỳ vọng:** `201 Created`, trạng thái mặc định `OPEN`. Lưu `created_ticket_id`.

#### Request 3.3: User xem danh sách Ticket của mình (Role Visibility Check)
- **Method / URL:** `GET {{baseUrl}}/tickets`
- **Headers:** `Authorization: Bearer {{user_token}}`
- **Kỳ vọng:** `200 OK`. *(Tất cả ticket trả về đều có `user_id == 3`, không thấy ticket của người khác).*

#### Request 3.4: User xem chi tiết Ticket
- **Method / URL:** `GET {{baseUrl}}/tickets/{{created_ticket_id}}`
- **Headers:** `Authorization: Bearer {{user_token}}`
- **Kỳ vọng:** `200 OK`.

#### Request 3.5: User chỉnh sửa nội dung Ticket
- **Method / URL:** `PATCH {{baseUrl}}/tickets/{{created_ticket_id}}`
- **Headers:** `Authorization: Bearer {{user_token}}`
- **Body (raw JSON):**
```json
{
  "title": "Màn hình PC-001 không lên nguồn (Bổ sung: Đã thử đổi ổ cắm)",
  "priority": "URGENT"
}
```
- **Kỳ vọng:** `200 OK`.

#### Request 3.6: User xem Lịch sử xử lý Ticket
- **Method / URL:** `GET {{baseUrl}}/tickets/{{created_ticket_id}}/history`
- **Headers:** `Authorization: Bearer {{user_token}}`
- **Kỳ vọng:** `200 OK`, có ít nhất 1 sự kiện `action: "CREATED"`.

#### 🛡️ Kiểm tra Quyền bảo mật của USER (Security Tests - 403 Forbidden):
- **Request 3.7 (Test 403):** `GET {{baseUrl}}/users` với `user_token` $\rightarrow$ Kỳ vọng `403 Forbidden`.
- **Request 3.8 (Test 403):** `POST {{baseUrl}}/devices` với `user_token` $\rightarrow$ Kỳ vọng `403 Forbidden`.
- **Request 3.9 (Test 403):** `PATCH {{baseUrl}}/tickets/1/assign` với `user_token` $\rightarrow$ Kỳ vọng `403 Forbidden`.

---

### 🟢 GIAI ĐOẠN 4: Phân công & Vòng đời Ticket (ADMIN + TECHNICIAN)

#### Bước 4.1: ADMIN Phân công Kỹ thuật viên (Assign Technician)
- **Method / URL:** `PATCH {{baseUrl}}/tickets/{{created_ticket_id}}/assign`
- **Headers:** `Authorization: Bearer {{admin_token}}`
- **Body (raw JSON):**
```json
{
  "technician_id": 2
}
```
- **Kỳ vọng:** `200 OK`, ticket chuyển trạng thái từ `OPEN` $\rightarrow$ `ASSIGNED`.

---

#### 🛠️ [TECHNICIAN] Tiếp nhận & Xử lý sự cố

#### Bước 4.2: TECHNICIAN Đăng nhập
- **Method / URL:** `POST {{baseUrl}}/login`
- **Body:** `{"username": "tech01", "password": "CS466@123"}`
- **Kỳ vọng:** `200 OK`, lưu `tech_token`.

#### Request 4.3: Tech xem danh sách Ticket được phân công
- **Method / URL:** `GET {{baseUrl}}/tickets?status=ASSIGNED`
- **Headers:** `Authorization: Bearer {{tech_token}}`
- **Kỳ vọng:** `200 OK`.

#### Request 4.4: Tech chuyển trạng thái sang ĐANG XỬ LÝ (IN_PROGRESS)
- **Method / URL:** `PATCH {{baseUrl}}/tickets/{{created_ticket_id}}/status`
- **Headers:** `Authorization: Bearer {{tech_token}}`
- **Body (raw JSON):**
```json
{
  "status": "IN_PROGRESS"
}
```
- **Kỳ vọng:** `200 OK`, `trang_thai: "IN_PROGRESS"`.

#### Request 4.5: Thử chuyển trạng thái sai quy trình (Negative Lifecycle Test)
- **Method / URL:** `PATCH {{baseUrl}}/tickets/{{created_ticket_id}}/status`
- **Headers:** `Authorization: Bearer {{tech_token}}`
- **Body:** `{"status": "OPEN"}` *(Không được phép quay lui OPEN)*
- **Kỳ vọng:** `400 Bad Request`, body: `{"detail": "INVALID_TRANSITION"}`.

#### Request 4.6: Tech cập nhật trạng thái ĐÃ GIẢI QUYẾT (RESOLVED)
- **Method / URL:** `PATCH {{baseUrl}}/tickets/{{created_ticket_id}}/status`
- **Headers:** `Authorization: Bearer {{tech_token}}`
- **Body (raw JSON):**
```json
{
  "status": "RESOLVED"
}
```
- **Kỳ vọng:** `200 OK`, `trang_thai: "RESOLVED"`.

#### Request 4.7: Tech Đóng Ticket hoàn tất (CLOSE)
- **Method / URL:** `PATCH {{baseUrl}}/tickets/{{created_ticket_id}}/close`
- **Headers:** `Authorization: Bearer {{tech_token}}`
- **Body (raw JSON):**
```json
{
  "note": "Đã thay adapter nguồn màn hình mới, thiết bị hoạt động tốt."
}
```
- **Kỳ vọng:** `200 OK`, `trang_thai: "CLOSED"`.

#### Request 4.8: Kiểm tra toàn bộ Lịch sử Ticket (History Audit Check)
- **Method / URL:** `GET {{baseUrl}}/tickets/{{created_ticket_id}}/history`
- **Headers:** `Authorization: Bearer {{tech_token}}`
- **Kỳ vọng:** `200 OK`, chứa đủ chuỗi sự kiện tuần tự:
  1. `CREATED` (Trạng thái: null $\rightarrow$ `OPEN`)
  2. `ASSIGNED` (Trạng thái: `OPEN` $\rightarrow$ `ASSIGNED`, gán cho tech01)
  3. `STATUS_CHANGED` (Trạng thái: `ASSIGNED` $\rightarrow$ `IN_PROGRESS`)
  4. `STATUS_CHANGED` (Trạng thái: `IN_PROGRESS` $\rightarrow$ `RESOLVED`)
  5. `CLOSED` (Trạng thái: `RESOLVED` $\rightarrow$ `CLOSED`, có note chi tiết)

---

## 3. Bảng tóm tắt ma trận phân quyền (RBAC Matrix)

| Endpoint | Method | USER | TECHNICIAN | ADMIN |
|:---|:---:|:---:|:---:|:---:|
| `/health` | GET |  |  |  |
| `/login` | POST |  |  |  |
| `/users` | GET, POST | ❌ 403 | ❌ 403 |  |
| `/users/{id}` | GET, PATCH | ❌ 403 | ❌ 403 |  |
| `/users/{id}/status` | PATCH | ❌ 403 | ❌ 403 |  |
| `/devices` | GET | ❌ 403 |  |  |
| `/devices` | POST | ❌ 403 | ❌ 403 |  |
| `/devices/{id}` | GET, PATCH | ❌ 403 |  |  |
| `/tickets` | GET |  *(Chỉ ticket của mình)* |  *(Ticket được giao/chung)* |  *(Toàn bộ)* |
| `/tickets` | POST |  | ❌ 403 |  |
| `/tickets/{id}` | GET, PATCH |  *(Nếu là chủ ticket)* |  |  |
| `/tickets/{id}/assign` | PATCH | ❌ 403 | ❌ 403 |  |
| `/tickets/{id}/status` | PATCH | ❌ 403 |  |  |
| `/tickets/{id}/close` | PATCH | ❌ 403 |  |  |
| `/tickets/{id}/history` | GET |  *(Nếu có quyền xem)* |  |  |
