# TASK PROMPTS — FINAL

## Prompt 1 — Audit backend

```text
Đọc SKILL.md.
Đọc database/schema.sql và docs/api-contract.md.
Audit backend hiện tại.
Không sửa ngoài /backend/**.
Trả BACKEND_AUDIT_RESULT và READY_TO_CODE: YES/NO.
```

## Prompt 2 — Auth + User Management

```text
Đọc SKILL.md và 06_ALGORITHMS.md.

Implement:
POST  /api/login
GET   /api/users
POST  /api/users
GET   /api/users/{id}
PATCH /api/users/{id}
PATCH /api/users/{id}/status

Yêu cầu:
- bcrypt;
- ACTIVE/INACTIVE;
- ADMIN authorization;
- 409 duplicate;
- không trả password_hash;
- parameterized MySQL;
- chỉ sửa /backend/**;
- chạy smoke + negative tests thật.
```

## Prompt 3 — Device Management

```text
Đọc SKILL.md và schema.sql.

Implement:
GET   /api/devices
POST  /api/devices
GET   /api/devices/{id}
PATCH /api/devices/{id}

Yêu cầu:
- đúng enum schema;
- duplicate ma_thiet_bi → 409;
- role theo API contract;
- logging nếu required;
- chỉ sửa /backend/**.
```

## Prompt 4 — Ticket Core

```text
Implement:
GET   /api/tickets
POST  /api/tickets
GET   /api/tickets/{id}
PATCH /api/tickets/{id}

Yêu cầu:
- role visibility;
- filter;
- create = OPEN;
- create + CREATED history cùng transaction;
- update/classify + history;
- generic PATCH không thay status/technician_id.
```

## Prompt 5 — Lifecycle + History

```text
Implement:
PATCH /api/tickets/{id}/assign
PATCH /api/tickets/{id}/status
PATCH /api/tickets/{id}/close
GET   /api/tickets/{id}/history

Lifecycle:
OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED

Yêu cầu:
- assign chỉ TECHNICIAN ACTIVE;
- transaction + history;
- RESOLVED set resolved_at;
- CLOSED set closed_at;
- invalid transition → 400;
- close chỉ từ RESOLVED;
- logging đúng docs/log-format.md.
```

## Prompt 6 — Final 19 API audit

```text
Đọc SKILL.md.

Audit đủ 19 API.

Với từng endpoint báo:
PASS / FAIL / BLOCKED

Kiểm tra:
- schema compatibility;
- bcrypt;
- RBAC USER/TECHNICIAN/ADMIN;
- validation;
- transaction;
- history;
- logging;
- no secret/raw SQL/traceback.

Chạy full smoke nếu môi trường cho phép.

Trả:
BACKEND_READY_FOR_INTEGRATION: YES/NO
BACKEND_READY_FOR_SUBMISSION: YES/NO
```

## Prompt 7 — One-shot full backend

```text
Đọc SKILL.md, schema.sql, api-contract.md, log-format.md.

Hoàn thiện toàn bộ Backend theo 19 API đã khóa.
Chỉ sửa /backend/**.

Thực hiện theo thứ tự:
1. audit/foundation;
2. auth + user;
3. device;
4. ticket core;
5. assign/status/close/history;
6. security/error/logging;
7. full smoke.

Không đổi schema.
Không sửa module owner khác.
Không fabricate test result.
Nếu một feature bị blocker contract thì chỉ block feature đó và tiếp tục phần độc lập.
```
