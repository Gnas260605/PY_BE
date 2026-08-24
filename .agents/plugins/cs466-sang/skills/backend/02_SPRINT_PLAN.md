# KẾ HOẠCH BACKEND HOÀN CHỈNH — FINAL

Đây là kế hoạch hoàn thiện sản phẩm, không phải các release riêng.

## Tuần 1 — Chốt nền

Backend:
- FastAPI + Uvicorn;
- config `MYSQL_*`;
- MySQL connector;
- `/api/health`;
- common error handlers;
- router/service/repository structure;
- đọc schema/contract thật.

Exit:
```text
Backend start
/api/health = 200
MySQL connected
Schema/API contract không còn blocker
```

## Tuần 2 — Auth + User + Device + Ticket Core

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

### Ticket Core
```text
GET   /api/tickets
POST  /api/tickets
GET   /api/tickets/{id}
PATCH /api/tickets/{id}
```

Exit:
- ADMIN quản lý user/device;
- USER login và tạo/xem/cập nhật ticket;
- DB lưu đúng;
- Postman có thể test.

## Tuần 3 — Lifecycle + History + Logging

```text
PATCH /api/tickets/{id}/assign
PATCH /api/tickets/{id}/status
PATCH /api/tickets/{id}/close
GET   /api/tickets/{id}/history
```

Bắt buộc:
- RBAC;
- transaction;
- history;
- logging;
- lifecycle:

```text
OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
```

Exit:
- full ticket flow chạy end-to-end;
- history đúng;
- log đủ cho Perl.

## Tuần 4 — Hoàn thiện trước nộp

Không thêm chức năng ngoài đặc tả.

Chỉ:
- fix bug;
- normalize response/status;
- regression;
- security check;
- integration support;
- README/backend notes nếu owner cho phép.

Backend final smoke:

```text
health
→ admin login
→ create user
→ create technician
→ disable/enable user
→ create device
→ user login
→ create ticket
→ list/detail/update
→ admin assign
→ technician IN_PROGRESS
→ RESOLVED
→ close
→ history
→ verify DB/log
```
