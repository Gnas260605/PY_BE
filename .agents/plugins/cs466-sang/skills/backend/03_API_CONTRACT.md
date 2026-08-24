# API CONTRACT — FINAL 19 ENDPOINTS

> JSON API dùng tên tiếng Anh; Backend map sang cột MySQL tiếng Việt.

## 1. Health

### GET /api/health

Response:
```json
{"status":"ok"}
```

Status:
```text
200
```

---

## 2. Auth

### POST /api/login

Request:
```json
{
  "username": "admin",
  "password": "..."
}
```

Response không chứa `password_hash`.

Status:
```text
200  login success
400  invalid input
401  wrong credential / inactive account
```

---

## 3. User Management — ADMIN

### GET /api/users

Optional query:
```text
role
status
keyword
```

Status:
```text
200
401
403
```

Empty:
```json
[]
```

### POST /api/users

Request baseline:
```json
{
  "username": "user02",
  "password": "...",
  "ho_ten": "Nguyen Van B",
  "email": "user02@example.local",
  "vai_tro": "USER"
}
```

Status:
```text
201
400
409 duplicate username/email
```

### GET /api/users/{id}

Status:
```text
200
404
```

### PATCH /api/users/{id}

Allowed baseline:
```text
ho_ten
email
vai_tro
```

Không update plaintext password ở endpoint này nếu API contract không bổ sung reset-password.

Status:
```text
200
400
404
409
```

### PATCH /api/users/{id}/status

Request:
```json
{"status":"ACTIVE"}
```

Allowed:
```text
ACTIVE
INACTIVE
```

Status:
```text
200
400
404
```

---

## 4. Device Management

### GET /api/devices

Role baseline:
```text
ADMIN
TECHNICIAN
```

Optional:
```text
status
type
keyword
```

Status:
```text
200
```

### POST /api/devices

ADMIN only.

Request baseline:
```json
{
  "ma_thiet_bi": "PC-002",
  "ten_thiet_bi": "Laptop phòng IT",
  "loai_thiet_bi": "LAPTOP",
  "vi_tri": "Phòng IT",
  "trang_thai": "ACTIVE",
  "mo_ta": "..."
}
```

Status:
```text
201
400
409
```

### GET /api/devices/{id}

Status:
```text
200
404
```

### PATCH /api/devices/{id}

Allowed theo contract/schema.

Status:
```text
200
400
404
```

---

## 5. Ticket Management

### GET /api/tickets

Optional filter:
```text
status
priority
category
technician_id
user_id
keyword
```

Visibility:
- USER: ticket mình;
- TECHNICIAN: ticket được giao/phạm vi contract;
- ADMIN: tất cả.

Status:
```text
200
```

### POST /api/tickets

Role:
```text
USER
ADMIN
```

Request:
```json
{
  "title": "Máy in không hoạt động",
  "description": "...",
  "device_id": 2,
  "category": "INCIDENT",
  "priority": "MEDIUM"
}
```

Mapping:
```text
title       → TICKETS.tieu_de
description → TICKETS.mo_ta
category    → TICKETS.loai_yeu_cau
priority    → TICKETS.muc_do_uu_tien
status      → TICKETS.trang_thai
```

Default:
```text
OPEN
```

Status:
```text
201
400
404
```

### GET /api/tickets/{id}

Response baseline:
- ticket;
- creator;
- device;
- technician;
- fields theo contract.

Status:
```text
200
403
404
```

### PATCH /api/tickets/{id}

Allowed baseline:
```text
title
description
category
priority
```

Không update:
```text
technician_id
status
```

qua generic PATCH.

Status:
```text
200
400
403
404
```

### PATCH /api/tickets/{id}/assign

ADMIN only.

Request:
```json
{"technician_id":2}
```

Rule:
- user tồn tại;
- role = TECHNICIAN;
- status account = ACTIVE;
- nếu ticket OPEN → ASSIGNED.

Status:
```text
200
400
404
```

### PATCH /api/tickets/{id}/status

TECHNICIAN/ADMIN.

Request:
```json
{"status":"IN_PROGRESS"}
```

Lifecycle:
```text
OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
```

Status:
```text
200
400
403
404
```

### PATCH /api/tickets/{id}/close

TECHNICIAN/ADMIN.

Rule:
```text
RESOLVED → CLOSED
```

Request có thể có:
```json
{"note":"Hoàn tất xử lý"}
```

Status:
```text
200
400
403
404
```

### GET /api/tickets/{id}/history

Theo quyền xem ticket.

Response:
```json
[
  {
    "action":"CREATED",
    "old_status":null,
    "new_status":"OPEN",
    "detail":"...",
    "performed_at":"..."
  }
]
```

Status:
```text
200
403
404
```
