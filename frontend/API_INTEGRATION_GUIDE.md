# TÀI LIỆU TỔNG HỢP & HƯỚNG DẪN TÍCH HỢP 19 API CHO FRONTEND
> **Dự án:** CS466 - Hệ thống quản lý bảo trì và yêu cầu dịch vụ CNTT  
> **Backend Host mặc định:** `http://127.0.0.1:8000`  
> **Base API Path:** `http://127.0.0.1:8000/api`  
> **Định dạng dữ liệu:** `application/json; charset=utf-8`  
> **Cơ chế xác thực:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`

---

## 1. Danh sách tài khoản mẫu để test (Seed Accounts)

Mật khẩu mặc định cho tất cả các tài khoản demo: **`CS466@123`**

| ID | Username | Vai trò (`vai_tro`) | Trạng thái | Quyền hạn trên giao diện Frontend |
|:---|:---|:---:|:---:|:---|
| `1` | **`admin`** | `ADMIN` | `ACTIVE` | **Toàn quyền:** Quản lý Người dùng (Users), Quản lý Thiết bị (Devices), Gán Kỹ thuật viên (Assign), Xem toàn bộ Tickets, Đóng Ticket |
| `2` | **`tech01`** | `TECHNICIAN` | `ACTIVE` | **Kỹ thuật viên:** Xem danh sách thiết bị, cập nhật tình trạng thiết bị, xem ticket được gán, chuyển trạng thái (`IN_PROGRESS`, `RESOLVED`, `CLOSED`) |
| `3` | **`user01`** | `USER` | `ACTIVE` | **Người dùng:** Tạo Ticket yêu cầu hỗ trợ, xem/sửa ticket của mình, xem lịch sử xử lý ticket |

---

## 2. Quy chuẩn chung khi gọi API từ Frontend

### 2.1. Đính kèm Token xác thực
Khi người dùng đăng nhập thành công qua `POST /api/login`, backend trả về `access_token`. Lưu token này vào `localStorage` hoặc `sessionStorage` và gửi kèm trong header của mọi request yêu cầu xác thực:

```javascript
const token = localStorage.getItem("access_token");
const headers = {
  "Content-Type": "application/json",
  ...(token ? { "Authorization": `Bearer ${token}` } : {})
};
```

### 2.2. Cấu trúc phản hồi lỗi chuẩn (Error Response)
Mọi lỗi từ API đều trả về dạng JSON chuẩn, an toàn (không leak thông tin bảo mật hay SQL error):
```json
{
  "detail": "Mã lỗi chi tiết (Ví dụ: INVALID_CREDENTIALS, FORBIDDEN, USER_NOT_FOUND, DUPLICATE_USERNAME)",
  "path": "/api/users/99"
}
```

Các mã HTTP Status chuẩn:
- `200 OK`: Thành công (truy vấn, cập nhật)
- `201 Created`: Tạo mới tài nguyên thành công (User, Device, Ticket)
- `400 Bad Request`: Dữ liệu đầu vào sai định dạng, thiếu trường bắt buộc hoặc vi phạm luồng chuyển trạng thái
- `401 Unauthorized`: Chưa đăng nhập, token không hợp lệ, token hết hạn hoặc tài khoản bị khóa (`INACTIVE`)
- `403 Forbidden`: Tài khoản không có quyền truy cập endpoint này (RBAC)
- `404 Not Found`: Không tìm thấy bản ghi theo ID
- `409 Conflict`: Trùng lặp dữ liệu duy nhất (Username, Email, Mã thiết bị `ma_thiet_bi`)
- `500 Internal Server Error`: Lỗi hệ thống server

---

## 3. Chi tiết đầy đủ 19 Endpoint Backend

---

### 🟢 NHÓM 1: HỆ THỐNG & XÁC THỰC (SYSTEM & AUTH) — 2 API

#### API 01. `GET /api/health`
- **Mô tả:** Kiểm tra trạng thái hoạt động của Backend server và kết nối cơ sở dữ liệu MySQL.
- **Quyền truy cập:** Public (Không cần token).
- **Request Headers:** Không bắt buộc.
- **Response 200 OK:**
```json
{
  "status": "ok"
}
```

---

#### API 02. `POST /api/login`
- **Mô tả:** Xác thực người dùng bằng username và mật khẩu, trả về JWT Access Token cùng thông tin tài khoản.
- **Quyền truy cập:** Public (Không cần token).
- **Request Body:**
```json
{
  "username": "admin",
  "password": "CS466@123"
}
```
- **Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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
- **Error Codes:**
  - `400 Bad Request`: Thiếu username hoặc password.
  - `401 Unauthorized`: Sai username/password (`INVALID_CREDENTIALS`) hoặc tài khoản bị khóa (`ACCOUNT_INACTIVE`).

---

### 🔵 NHÓM 2: QUẢN LÝ NGƯỜI DÙNG (USER MANAGEMENT) — 5 API (ADMIN ONLY)

#### API 03. `GET /api/users`
- **Mô tả:** Lấy danh sách tài khoản người dùng trong hệ thống (hỗ trợ lọc theo vai trò, trạng thái và tìm kiếm).
- **Quyền truy cập:** `ADMIN` (Bắt buộc Bearer Token của Admin).
- **Query Parameters (Tùy chọn):**
  - `role` *(string)*: Lọc theo vai trò (`USER` | `TECHNICIAN` | `ADMIN`).
  - `status` *(string)*: Lọc theo trạng thái (`ACTIVE` | `INACTIVE`).
  - `keyword` *(string)*: Tìm kiếm theo username, họ tên hoặc email.
- **Ví dụ Request:** `GET /api/users?role=USER&status=ACTIVE&keyword=Nguyen`
- **Response 200 OK:**
```json
[
  {
    "id": 3,
    "username": "user01",
    "ho_ten": "Người dùng 01",
    "email": "user01@cs466.local",
    "vai_tro": "USER",
    "trang_thai": "ACTIVE",
    "created_at": "2026-08-24T05:00:00",
    "updated_at": "2026-08-24T05:00:00"
  }
]
```
- **Error Codes:** `401 Unauthorized`, `403 Forbidden` (nếu không phải ADMIN).

---

#### API 04. `POST /api/users`
- **Mô tả:** Tạo mới một tài khoản người dùng trong hệ thống (Mật khẩu được mã hóa tự động bằng bcrypt).
- **Quyền truy cập:** `ADMIN`.
- **Request Body:**
```json
{
  "username": "user02",
  "password": "CS466@123",
  "ho_ten": "Nguyễn Văn B",
  "email": "user02@cs466.local",
  "vai_tro": "USER"
}
```
*Ghi chú:*
- `username`: 3 - 50 ký tự (Bắt buộc).
- `password`: Tối thiểu 8 ký tự (Bắt buộc).
- `ho_ten`: Họ và tên (Bắt buộc).
- `email`: Định dạng email hợp lệ (Tùy chọn).
- `vai_tro`: `USER` | `TECHNICIAN` | `ADMIN` (Bắt buộc).
- **Response 201 Created:**
```json
{
  "id": 4,
  "username": "user02",
  "ho_ten": "Nguyễn Văn B",
  "email": "user02@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "created_at": "2026-08-24T13:00:00",
  "updated_at": "2026-08-24T13:00:00"
}
```
- **Error Codes:**
  - `400 Bad Request`: Dữ liệu không hợp lệ.
  - `409 Conflict`: Username hoặc Email đã tồn tại trong hệ thống.

---

#### API 05. `GET /api/users/{id}`
- **Mô tả:** Lấy thông tin chi tiết của một tài khoản theo ID.
- **Quyền truy cập:** `ADMIN`.
- **Response 200 OK:**
```json
{
  "id": 4,
  "username": "user02",
  "ho_ten": "Nguyễn Văn B",
  "email": "user02@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "ACTIVE",
  "created_at": "2026-08-24T13:00:00",
  "updated_at": "2026-08-24T13:00:00"
}
```
- **Error Codes:** `404 Not Found` nếu ID không tồn tại.

---

#### API 06. `PATCH /api/users/{id}`
- **Mô tả:** Cập nhật họ tên, email hoặc vai trò của tài khoản.
- **Quyền truy cập:** `ADMIN`.
- **Request Body (Truyền các trường cần cập nhật):**
```json
{
  "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
  "email": "ketoan_b@cs466.local",
  "vai_tro": "TECHNICIAN"
}
```
- **Response 200 OK:** Trả về thông tin User sau khi cập nhật.
- **Error Codes:**
  - `400 Bad Request`: Không truyền trường nào để cập nhật hoặc email/role sai định dạng.
  - `404 Not Found`: Không tìm thấy user.
  - `409 Conflict`: Email mới trùng với tài khoản khác.

---

#### API 07. `PATCH /api/users/{id}/status`
- **Mô tả:** Khóa (Vô hiệu hóa) hoặc Kích hoạt lại tài khoản người dùng (Không xóa vật lý trong database).
- **Quyền truy cập:** `ADMIN`.
- **Request Body:**
```json
{
  "status": "INACTIVE"
}
```
*(Chỉ chấp nhận giá trị `ACTIVE` hoặc `INACTIVE`)*.
- **Response 200 OK:**
```json
{
  "id": 4,
  "username": "user02",
  "ho_ten": "Nguyễn Văn B",
  "email": "user02@cs466.local",
  "vai_tro": "USER",
  "trang_thai": "INACTIVE",
  "created_at": "2026-08-24T13:00:00",
  "updated_at": "2026-08-24T13:05:00"
}
```

---

### 🟡 NHÓM 3: QUẢN LÝ THIẾT BỊ (DEVICE MANAGEMENT) — 4 API

#### API 08. `GET /api/devices`
- **Mô tả:** Lấy danh sách thiết bị công nghệ thông tin trong hệ thống.
- **Quyền truy cập:** `ADMIN`, `TECHNICIAN`.
- **Query Parameters (Tùy chọn):**
  - `status` *(string)*: `ACTIVE` | `MAINTENANCE` | `BROKEN` | `INACTIVE`.
  - `type` *(string)*: Loại thiết bị (Ví dụ: `COMPUTER`, `PRINTER`, `ROUTER`, `LAPTOP`).
  - `keyword` *(string)*: Tìm theo mã thiết bị hoặc tên thiết bị.
- **Response 200 OK:**
```json
[
  {
    "id": 1,
    "ma_thiet_bi": "PC-001",
    "ten_thiet_bi": "Máy tính phòng Kế toán",
    "loai_thiet_bi": "COMPUTER",
    "vi_tri": "Phòng Kế toán",
    "trang_thai": "ACTIVE",
    "mo_ta": "Máy tính để bàn Dell Optiplex",
    "created_at": "2026-08-24T05:00:00",
    "updated_at": "2026-08-24T05:00:00"
  }
]
```

---

#### API 09. `POST /api/devices`
- **Mô tả:** Thêm mới thiết bị vào hệ thống.
- **Quyền truy cập:** `ADMIN` duy nhất.
- **Request Body:**
```json
{
  "ma_thiet_bi": "PC-002",
  "ten_thiet_bi": "Máy tính phòng Marketing",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Phòng Marketing - Tầng 3",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Vostro Core i7 16GB RAM"
}
```
*Ghi chú:*
- `ma_thiet_bi`: Duy nhất, không được trùng (Bắt buộc).
- `ten_thiet_bi`: Tên thiết bị (Bắt buộc).
- `trang_thai`: Mặc định `ACTIVE` nếu không truyền (Tùy chọn: `ACTIVE`, `MAINTENANCE`, `BROKEN`, `INACTIVE`).
- **Response 201 Created:** Thông tin thiết bị vừa tạo.
- **Error Codes:**
  - `400 Bad Request`: Thiếu trường bắt buộc hoặc trạng thái sai enum.
  - `409 Conflict`: Mã thiết bị `ma_thiet_bi` đã tồn tại.

---

#### API 10. `GET /api/devices/{id}`
- **Mô tả:** Lấy thông tin chi tiết một thiết bị theo ID.
- **Quyền truy cập:** `ADMIN`, `TECHNICIAN`.
- **Response 200 OK:** Chi tiết thiết bị.
- **Error Codes:** `404 Not Found` nếu không tìm thấy thiết bị.

---

#### API 11. `PATCH /api/devices/{id}`
- **Mô tả:** Cập nhật thông tin hoặc trạng thái hoạt động/bảo trì của thiết bị.
- **Quyền truy cập:**
  - `ADMIN`: Được sửa toàn bộ các trường (`ma_thiet_bi`, `ten_thiet_bi`, `loai_thiet_bi`, `vi_tri`, `trang_thai`, `mo_ta`).
  - `TECHNICIAN`: Được cập nhật `trang_thai` và `mo_ta` phục vụ công tác sửa chữa, bảo dưỡng.
- **Request Body (Truyền các trường cần cập nhật):**
```json
{
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Đang thay thế bộ nguồn và vệ sinh quạt tản nhiệt"
}
```
- **Response 200 OK:** Thông tin thiết bị sau cập nhật.
- **Error Codes:** `400 Bad Request`, `404 Not Found`, `409 Conflict` (nếu đổi mã thiết bị trùng).

---

### 🟣 NHÓM 4: QUẢN LÝ TICKET & VÒNG ĐỜI XỬ LÝ (TICKET LIFECYCLE) — 8 API

#### API 12. `GET /api/tickets`
- **Mô tả:** Lấy danh sách Ticket có phân quyền hiển thị theo vai trò (Role-based Visibility):
  - **`USER`:** Chỉ nhìn thấy các ticket do chính tài khoản của mình tạo.
  - **`TECHNICIAN`:** Nhìn thấy các ticket được phân công cho mình hoặc các ticket chung.
  - **`ADMIN`:** Nhìn thấy toàn bộ ticket trong hệ thống.
- **Quyền truy cập:** `USER`, `TECHNICIAN`, `ADMIN`.
- **Query Parameters (Tùy chọn):**
  - `status` *(string)*: `OPEN` | `ASSIGNED` | `IN_PROGRESS` | `RESOLVED` | `CLOSED`.
  - `priority` *(string)*: `LOW` | `MEDIUM` | `HIGH` | `URGENT`.
  - `category` *(string)*: `INCIDENT` | `SERVICE_REQUEST` | `MAINTENANCE`.
  - `technician_id` *(int)*: Lọc theo ID kỹ thuật viên phụ trách.
  - `user_id` *(int)*: Lọc theo ID người tạo.
  - `keyword` *(string)*: Tìm kiếm theo tiêu đề hoặc mô tả ticket.
- **Response 200 OK:**
```json
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
    "created_at": "2026-08-24T05:00:00",
    "updated_at": "2026-08-24T05:00:00",
    "resolved_at": null,
    "closed_at": null
  }
]
```

---

#### API 13. `POST /api/tickets`
- **Mô tả:** Tạo mới yêu cầu hỗ trợ dịch vụ hoặc báo cáo sự cố CNTT. Tự động lưu người tạo từ JWT Token và ghi nhận sự kiện lịch sử `CREATED`.
- **Quyền truy cập:** `USER`, `ADMIN`.
- **Request Body:**
```json
{
  "title": "Màn hình PC-001 không lên nguồn",
  "description": "Bật nút nguồn màn hình nhưng đèn tín hiệu không sáng, đã cắm lại dây nguồn.",
  "device_id": 1,
  "category": "INCIDENT",
  "priority": "HIGH"
}
```
*Ghi chú:*
- `title`: Tiêu đề sự cố (Bắt buộc).
- `description`: Mô tả chi tiết (Bắt buộc).
- `device_id`: ID thiết bị liên quan (Tùy chọn, có thể null).
- `category`: `INCIDENT` (Sự cố) | `SERVICE_REQUEST` (Yêu cầu dịch vụ) | `MAINTENANCE` (Bảo trì).
- `priority`: `LOW` | `MEDIUM` | `HIGH` | `URGENT`.
- **Response 201 Created:** Trả về ticket mới tạo với trạng thái ban đầu mặc định là `OPEN`.

---

#### API 14. `GET /api/tickets/{id}`
- **Mô tả:** Lấy thông tin chi tiết đầy đủ của ticket, kèm theo thông tin chi tiết người tạo (`creator`), thiết bị (`device`) và kỹ thuật viên phụ trách (`technician`).
- **Quyền truy cập:** `USER` (chỉ xem được ticket của mình), `TECHNICIAN`, `ADMIN`.
- **Response 200 OK:**
```json
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
  "created_at": "2026-08-24T05:00:00",
  "updated_at": "2026-08-24T05:30:00",
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
    "id": 2,
    "ma_thiet_bi": "PRN-001",
    "ten_thiet_bi": "Máy in văn phòng",
    "loai_thiet_bi": "PRN",
    "vi_tri": "Văn phòng",
    "trang_thai": "MAINTENANCE",
    "mo_ta": "Máy in dùng chung"
  },
  "technician": {
    "id": 2,
    "username": "tech01",
    "ho_ten": "Kỹ thuật viên 01",
    "email": "tech01@cs466.local",
    "vai_tro": "TECHNICIAN",
    "trang_thai": "ACTIVE"
  }
}
```
- **Error Codes:** `403 Forbidden` (nếu user xem ticket của người khác), `404 Not Found`.

---

#### API 15. `PATCH /api/tickets/{id}`
- **Mô tả:** Chỉnh sửa nội dung hoặc phân loại lại mức độ ưu tiên/danh mục của ticket (Tự động ghi lịch sử `UPDATED` hoặc `CLASSIFIED`).
- **Quyền truy cập:** `USER` (chỉ khi ticket còn ở trạng thái `OPEN`), `ADMIN`.
- **Request Body (Truyền các trường cần cập nhật):**
```json
{
  "title": "Màn hình PC-001 không lên nguồn (Bổ sung: Cần xử lý gấp trước 10h)",
  "priority": "URGENT",
  "category": "INCIDENT"
}
```
- **Response 200 OK:** Ticket sau khi cập nhật.

---

#### API 16. `PATCH /api/tickets/{id}/assign`
- **Mô tả:** Phân công kỹ thuật viên chịu trách nhiệm xử lý ticket. Tự động chuyển trạng thái ticket từ `OPEN` $\to$ `ASSIGNED` và ghi nhận lịch sử `ASSIGNED`.
- **Quyền truy cập:** `ADMIN` duy nhất.
- **Request Body:**
```json
{
  "technician_id": 2
}
```
- **Quy tắc nghiệp vụ:**
  - Kỹ thuật viên được gán phải có vai trò `vai_tro = 'TECHNICIAN'` và trạng thái tài khoản `trang_thai = 'ACTIVE'`.
  - Không được gán cho ticket đã đóng (`CLOSED`).
- **Response 200 OK:** Thông tin ticket sau khi gán.
- **Error Codes:**
  - `400 Bad Request`: Tài khoản được gán không phải kỹ thuật viên hoặc bị khóa.
  - `404 Not Found`: Không tìm thấy ticket hoặc kỹ thuật viên.

---

#### API 17. `PATCH /api/tickets/{id}/status`
- **Mô tả:** Cập nhật trạng thái tiến độ xử lý ticket theo đúng chu trình vòng đời nghiêm ngặt.
- **Quyền truy cập:** `TECHNICIAN`, `ADMIN`.
- **Chu trình trạng thái bắt buộc (Ticket Lifecycle):**
  $$\mathbf{OPEN} \longrightarrow \mathbf{ASSIGNED} \longrightarrow \mathbf{IN\_PROGRESS} \longrightarrow \mathbf{RESOLVED} \longrightarrow \mathbf{CLOSED}$$
- **Request Body:**
```json
{
  "status": "IN_PROGRESS"
}
```
- **Hành vi hệ thống:**
  - Chuyển sang `RESOLVED`: Tự động ghi nhận thời gian hoàn tất `resolved_at = NOW()`.
  - Chuyển sang `CLOSED`: Tự động ghi nhận thời gian đóng `closed_at = NOW()`.
  - Tự động ghi nhận sự kiện `STATUS_CHANGED` vào bảng lịch sử.
- **Response 200 OK:** Thông tin ticket sau cập nhật.
- **Error Codes:** `400 Bad Request` nếu chuyển trạng thái sai chu trình (ví dụ: chuyển từ `RESOLVED` quay lùi về `OPEN` hoặc từ `CLOSED` sang trạng thái khác).

---

#### API 18. `PATCH /api/tickets/{id}/close`
- **Mô tả:** Đóng hoàn tất ticket và lưu ghi chú xử lý (Tự động ghi nhận `closed_at` và lịch sử sự kiện `CLOSED`).
- **Quyền truy cập:** `TECHNICIAN`, `ADMIN`.
- **Quy tắc nghiệp vụ:** Chỉ cho phép đóng khi ticket đã được giải quyết (`RESOLVED`).
- **Request Body (Tùy chọn):**
```json
{
  "note": "Đã thay adapter nguồn màn hình mới, thiết bị hoạt động ổn định."
}
```
- **Response 200 OK:** Ticket sau khi chuyển trạng thái sang `CLOSED`.
- **Error Codes:** `400 Bad Request` nếu ticket chưa ở trạng thái `RESOLVED`.

---

#### API 19. `GET /api/tickets/{id}/history`
- **Mô tả:** Lấy toàn bộ timeline lịch sử thay đổi của ticket theo thứ tự thời gian tăng dần.
- **Quyền truy cập:** `USER` (xem ticket của mình), `TECHNICIAN`, `ADMIN`.
- **Response 200 OK:**
```json
[
  {
    "id": 1,
    "action": "CREATED",
    "old_status": null,
    "new_status": "OPEN",
    "detail": "Ticket mẫu được tạo",
    "performed_by": 3,
    "performed_at": "2026-08-24T05:00:00"
  },
  {
    "id": 2,
    "action": "ASSIGNED",
    "old_status": "OPEN",
    "new_status": "ASSIGNED",
    "detail": "Gán cho kỹ thuật viên tech01",
    "performed_by": 1,
    "performed_at": "2026-08-24T05:30:00"
  },
  {
    "id": 3,
    "action": "STATUS_CHANGED",
    "old_status": "ASSIGNED",
    "new_status": "IN_PROGRESS",
    "detail": "Chuyển trạng thái sang IN_PROGRESS",
    "performed_by": 2,
    "performed_at": "2026-08-24T06:00:00"
  },
  {
    "id": 4,
    "action": "STATUS_CHANGED",
    "old_status": "IN_PROGRESS",
    "new_status": "RESOLVED",
    "detail": "Chuyển trạng thái sang RESOLVED",
    "performed_by": 2,
    "performed_at": "2026-08-24T07:00:00"
  },
  {
    "id": 5,
    "action": "CLOSED",
    "old_status": "RESOLVED",
    "new_status": "CLOSED",
    "detail": "Đã thay adapter nguồn màn hình mới, thiết bị hoạt động tốt.",
    "performed_by": 2,
    "performed_at": "2026-08-24T07:15:00"
  }
]
```

---

## 4. Ma trận phân quyền truy cập (RBAC Access Matrix)

| STT | Endpoint | Method | USER | TECHNICIAN | ADMIN | Ghi chú quyền hạn |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| 01 | `/api/health` | GET |  |  |  | Public |
| 02 | `/api/login` | POST |  |  |  | Public |
| 03 | `/api/users` | GET | ❌ 403 | ❌ 403 |  | Quản trị viên quản lý tài khoản |
| 04 | `/api/users` | POST | ❌ 403 | ❌ 403 |  | Tạo người dùng mới |
| 05 | `/api/users/{id}` | GET | ❌ 403 | ❌ 403 |  | Xem chi tiết người dùng |
| 06 | `/api/users/{id}` | PATCH | ❌ 403 | ❌ 403 |  | Cập nhật người dùng |
| 07 | `/api/users/{id}/status` | PATCH | ❌ 403 | ❌ 403 |  | Khóa / Mở khóa tài khoản |
| 08 | `/api/devices` | GET | ❌ 403 |  |  | Xem danh sách thiết bị |
| 09 | `/api/devices` | POST | ❌ 403 | ❌ 403 |  | Thêm thiết bị mới |
| 10 | `/api/devices/{id}` | GET | ❌ 403 |  |  | Xem chi tiết thiết bị |
| 11 | `/api/devices/{id}` | PATCH | ❌ 403 |  |  | Cập nhật thiết bị |
| 12 | `/api/tickets` | GET |  *(Ticket mình)* |  *(Ticket được giao/chung)* |  *(Tất cả)* | Xem danh sách ticket |
| 13 | `/api/tickets` | POST |  | ❌ 403 |  | Tạo ticket yêu cầu mới |
| 14 | `/api/tickets/{id}` | GET |  *(Ticket mình)* |  |  | Chi tiết ticket & liên kết |
| 15 | `/api/tickets/{id}` | PATCH |  *(Khi OPEN)* | ❌ 403 |  | Sửa nội dung ticket |
| 16 | `/api/tickets/{id}/assign` | PATCH | ❌ 403 | ❌ 403 |  | Gán kỹ thuật viên |
| 17 | `/api/tickets/{id}/status` | PATCH | ❌ 403 |  |  | Chuyển trạng thái vòng đời |
| 18 | `/api/tickets/{id}/close` | PATCH | ❌ 403 |  |  | Đóng ticket đã hoàn tất |
| 19 | `/api/tickets/{id}/history`| GET |  *(Ticket mình)* |  |  | Lịch sử chu trình ticket |

---

## 5. Hướng dẫn tích hợp vào mã nguồn Frontend (JavaScript Client)

Frontend có thể trực tiếp import module [frontend/js/api.js](file:///d:/Individua_Project/Python_Project/frontend/js/api.js) đã xây dựng sẵn:

```javascript
import { authApi, usersApi, devicesApi, ticketsApi } from "./api.js";

// 1. Đăng nhập hệ thống
async function handleLogin() {
  try {
    const result = await authApi.login("admin", "CS466@123");
    console.log("Token:", result.access_token);
    console.log("User:", result.user);
    window.location.href = "/pages/dashboard.html";
  } catch (error) {
    alert("Đăng nhập thất bại: " + error.message);
  }
}

// 2. Tạo Ticket mới
async function handleCreateTicket() {
  try {
    const newTicket = await ticketsApi.createTicket({
      title: "Hỏng bàn phím PC-001",
      description: "Liệt các phím số bên phải",
      device_id: 1,
      category: "INCIDENT",
      priority: "MEDIUM"
    });
    console.log("Ticket vừa tạo:", newTicket);
  } catch (error) {
    console.error("Lỗi tạo ticket:", error);
  }
}

// 3. Đổi trạng thái Ticket (Dành cho Kỹ thuật viên)
async function handleUpdateStatus(ticketId, newStatus) {
  try {
    const updated = await ticketsApi.updateTicketStatus(ticketId, newStatus);
    console.log("Đã chuyển trạng thái:", updated.status);
  } catch (error) {
    alert("Không thể chuyển trạng thái: " + error.message);
  }
}
```
