# CS466 Sang Backend Skill — FINAL

## Mục tiêu

Hướng dẫn AI coding agent phát triển phần Backend/API Python cho đồ án:

**Hệ thống quản lý bảo trì và yêu cầu dịch vụ CNTT**

Phạm vi owner:

```text
/backend/**
```

Các thư mục khác chỉ được đọc tham chiếu:

```text
/database/**
/docs/**
/frontend/**
/perl/**
/tests/**
/postman/**
```

Không tự sửa module của thành viên khác.

---

## Công nghệ đã khóa

```text
Python 3.12
FastAPI
Uvicorn
MySQL 8+
pydantic-settings
bcrypt
```

Không được đổi framework.

---

## Source of truth

Ưu tiên theo thứ tự:

1. `database/schema.sql`
2. `docs/api-contract.md`
3. `docs/db-contract.md`
4. `docs/log-format.md`
5. code hiện tại trong `/backend/**`
6. skill này

Nếu có xung đột:
- báo `CONTRACT_DRIFT`;
- không tự invent field/schema/endpoint.

---

## Database đã khóa

### USERS
```text
id
username
password_hash
ho_ten
email
vai_tro
trang_thai
created_at
updated_at
```

Role:

```text
USER
TECHNICIAN
ADMIN
```

Status:

```text
ACTIVE
INACTIVE
```

Password:
- dùng bcrypt;
- không lưu plaintext;
- không trả `password_hash`.

### DEVICES
```text
id
ma_thiet_bi
ten_thiet_bi
loai_thiet_bi
vi_tri
trang_thai
mo_ta
created_at
updated_at
```

Device status:

```text
ACTIVE
MAINTENANCE
BROKEN
INACTIVE
```

### TICKETS
```text
id
tieu_de
mo_ta
loai_yeu_cau
muc_do_uu_tien
trang_thai
user_id
device_id
technician_id
created_at
updated_at
resolved_at
closed_at
```

Category:

```text
INCIDENT
SERVICE_REQUEST
MAINTENANCE
```

Priority:

```text
LOW
MEDIUM
HIGH
URGENT
```

Lifecycle:

```text
OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
```

### TICKET_HISTORY
```text
id
ticket_id
nguoi_thuc_hien_id
hanh_dong
trang_thai_cu
trang_thai_moi
chi_tiet_cap_nhat
thoi_gian
```

Action:

```text
CREATED
UPDATED
CLASSIFIED
ASSIGNED
STATUS_CHANGED
CLOSED
```

---

## 19 API phải hoàn thành

### System
```text
GET /api/health
```

### Auth
```text
POST /api/login
```

### User Management
```text
GET   /api/users
POST  /api/users
GET   /api/users/{id}
PATCH /api/users/{id}
PATCH /api/users/{id}/status
```

### Device Management
```text
GET   /api/devices
POST  /api/devices
GET   /api/devices/{id}
PATCH /api/devices/{id}
```

### Ticket Management
```text
GET   /api/tickets
POST  /api/tickets
GET   /api/tickets/{id}
PATCH /api/tickets/{id}
PATCH /api/tickets/{id}/assign
PATCH /api/tickets/{id}/status
PATCH /api/tickets/{id}/close
GET   /api/tickets/{id}/history
```

---

## RBAC baseline

### USER
- login;
- tạo ticket;
- xem ticket của mình;
- xem detail/history ticket của mình;
- cập nhật nội dung ticket khi còn OPEN nếu API contract cho phép.

### TECHNICIAN
- login;
- xem ticket được phân công;
- xem device;
- cập nhật trạng thái ticket;
- cập nhật tình trạng device nếu contract cho phép;
- xem history;
- đóng ticket khi hợp lệ.

### ADMIN
- full User Management;
- full Device Management;
- xem tất cả ticket;
- phân loại;
- gán TECHNICIAN;
- cập nhật lifecycle;
- đóng ticket;
- xem history.

API contract có quyền ưu tiên nếu khác baseline.

---

## HTTP / Error rules

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
500 Internal Server Error
```

List empty → `200 []`.

Không expose:
- traceback;
- raw SQL;
- password;
- password_hash;
- secret.

---

## Transaction rules

Bắt buộc transaction cho:

```text
create ticket + CREATED history
update/classify + history
assign + history
status change + history
close + history
```

Pattern:

```text
BEGIN
mutation
history write
COMMIT
```

Lỗi:

```text
ROLLBACK
```

---

## Logging

Phải đọc `docs/log-format.md`.

Không tự đổi format vì Perl parser phụ thuộc log.

Không log:
- password;
- hash;
- secret;
- credential.

---

## Trước khi code

Bắt buộc báo:

```text
TASK ANALYSIS

Task:
Current backend state:
Contracts inspected:
DB schema inspected:
Relevant fields:
Files to modify:
Files not touching:
Blockers:
Plan:
```

## Sau khi code

Bắt buộc báo:

```text
IMPLEMENTATION RESULT

Status: DONE/PARTIAL/BLOCKED
Files changed:
Endpoints:
DB tables touched:
Transactions:
History:
Logging:
Commands run:
Tests actually run:
Not tested:
Contract drift:
Cross-owner follow-up:
```

Không được tuyên bố test pass nếu chưa chạy.
