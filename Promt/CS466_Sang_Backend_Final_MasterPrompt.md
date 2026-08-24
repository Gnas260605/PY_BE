# CS466 – Sang Backend Final Master Prompt

# CS466 – Sang Backend Final Prompt Pack

Dùng cho phần Backend/API Python của Huỳnh Thanh Sang.

Thứ tự khuyên dùng:
1. `00_MASTER_BACKEND_PROMPT.md`
2. `01_AUDIT_BACKEND.md`
3. `02_AUTH_USER_MANAGEMENT.md`
4. `03_DEVICE_MANAGEMENT.md`
5. `04_TICKET_CORE_MANAGEMENT.md`
6. `05_LIFECYCLE_HISTORY_LOGGING.md`
7. `06_FINAL_BACKEND_CHECK.md`

Mỗi lần dùng Codex/Antigravity có thể đọc thêm `07_CODEX_ANTIGRAVITY_WRAPPER.md`.
Nếu muốn làm gần như toàn bộ trong một lượt, dùng `08_ONE_SHOT_FULL_BACKEND.md`.

Bộ này mô tả **sản phẩm cuối hoàn chỉnh để tích hợp và nộp**, không chia release v0.x/v1.x.


---

# MASTER BACKEND PROMPT – HUỲNH THANH SANG

Bạn là senior backend engineer làm trực tiếp trong repository đồ án CS466: **Hệ thống quản lý bảo trì và yêu cầu dịch vụ CNTT**.

## Scope bắt buộc
Chỉ sửa `/backend/**`. Các thư mục `/database/**`, `/docs/**`, `/frontend/**`, `/perl/**`, `/tests/**`, `/postman/**` chỉ được đọc để đối chiếu. Nếu cần đổi schema/contract, báo owner; không tự sửa.

## Công nghệ đã khóa
- Python 3.12
- FastAPI + Uvicorn
- MySQL
- pydantic-settings
- biến môi trường `MYSQL_*`
- bcrypt cho password hash

Không đổi framework.

## Source of truth
Ưu tiên: `docs/api-contract.md` → `database/schema.sql` → `docs/db-contract.md` → `docs/log-format.md` → code backend hiện tại → prompt này.
Nếu xung đột, báo `CONTRACT_DRIFT`, không tự đoán.

## Entity
`USERS`, `DEVICES`, `TICKETS`, `TICKET_HISTORY`.
Không tự ALTER TABLE, không invent cột.

## Role
`USER`, `TECHNICIAN`, `ADMIN`.

Baseline quyền:
- USER: login, tạo ticket, xem ticket của mình và lịch sử có quyền xem.
- TECHNICIAN: login, xem ticket được phân công, cập nhật trạng thái hợp lệ, xem/cập nhật thiết bị nếu contract cho phép.
- ADMIN: quản lý user, quản lý device, xem toàn bộ ticket, phân loại, gán kỹ thuật viên, chuyển trạng thái, đóng ticket, xem history.

## Ticket lifecycle
`OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED`.

## API cuối phải có
```text
GET  /api/health
POST /api/login

GET   /api/users
POST  /api/users
GET   /api/users/{id}
PATCH /api/users/{id}
PATCH /api/users/{id}/status

GET   /api/devices
POST  /api/devices
GET   /api/devices/{id}
PATCH /api/devices/{id}

GET   /api/tickets
POST  /api/tickets
GET   /api/tickets/{id}
PATCH /api/tickets/{id}
PATCH /api/tickets/{id}/assign
PATCH /api/tickets/{id}/status
PATCH /api/tickets/{id}/close
GET   /api/tickets/{id}/history
```

## HTTP/error baseline
200, 201, 400, 401, 403, 404, 409, 500.
Không trả traceback, raw SQL, password, password_hash, secret.

## DB safety
- parameterized queries;
- clean connection lifecycle;
- multi-write dùng transaction;
- lỗi thì rollback;
- không SQL concat từ input user.

## Ticket history
Các thao tác create/update/classify/assign/status/close phải ghi history theo schema/contract. Ticket write + history write phải cùng transaction.

## Logging
Tuân thủ `docs/log-format.md`. Không log password/hash/secret. Không đổi format vì Perl phụ thuộc log.

## Trước khi code
Trả:
```text
TASK ANALYSIS
Task:
Current backend state:
Contracts inspected:
DB schema inspected:
Relevant tables/fields:
Files to modify:
Files explicitly not touching:
Dependencies:
Blockers:
Implementation plan:
```

## Sau khi code
Trả:
```text
IMPLEMENTATION RESULT
Status: DONE/PARTIAL/BLOCKED
Files changed:
Endpoints implemented/changed:
DB tables touched:
Transactions:
History behavior:
Logging behavior:
Commands run:
Tests/smoke actually run:
Not tested:
Contract drift:
Cross-owner follow-up:
```


---

# PROMPT 01 – AUDIT BACKEND HIỆN TẠI

Đọc `00_MASTER_BACKEND_PROMPT.md`. Không sửa code ở bước đầu.

Kiểm tra:
1. FastAPI/Uvicorn startup, `/api/health`, route→service→repository/db.
2. Backend dùng đúng `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`.
3. Đọc `database/schema.sql`, xác nhận field thật của USERS/DEVICES/TICKETS/TICKET_HISTORY.
4. Đọc `docs/api-contract.md` và đánh dấu mỗi API: IMPLEMENTED/PARTIAL/STUB/MISSING/CONTRACT_MISMATCH.
5. Kiểm tra User Management, Device Management, Ticket Management, History, Logging.
6. Kiểm tra raw traceback/MySQL error, password/hash exposure, hard-code credential, SQL injection risk.

Trả:
```text
BACKEND_AUDIT_RESULT
Framework:
Startup:
Health:
MySQL:
Auth schema:
User management:
Device management:
Ticket management:
History:
Logging:
Security:
Contract drift:
Blockers:
IMPLEMENTATION_ORDER:
READY_TO_IMPLEMENT: YES/NO
```

Không sửa module owner khác.


---

# PROMPT 02 – AUTH + USER MANAGEMENT

Đọc Master Prompt + API Contract + DB schema. Chỉ sửa `/backend/**`.

## Login – POST /api/login
1. parse/validate body;
2. query USERS bằng identifier contract;
3. user không có → 401;
4. inactive → chặn;
5. bcrypt verify password_hash;
6. sai → 401;
7. đúng → user/role/auth state theo contract;
8. không trả password_hash;
9. log success/fail nhưng không log password.
Không tự invent JWT/session.

## GET /api/users
ADMIN only. Hỗ trợ role/status/keyword nếu contract có. Empty → 200 []. Không trả hash.

## POST /api/users
ADMIN only. Validate username/password/ho_ten/role; duplicate username/email → 409; bcrypt hash; INSERT; 201.

## GET /api/users/{id}
ADMIN only. 200/404. Không trả hash.

## PATCH /api/users/{id}
ADMIN only. Chỉ allowed fields. Duplicate → 409. Không reset password qua endpoint này nếu contract không khóa.

## PATCH /api/users/{id}/status
ADMIN only. ACTIVE/INACTIVE. Không xóa vật lý user.

Verify thật: login valid/wrong/inactive; create; duplicate; list; detail; update; disable; login disabled; enable.


---

# PROMPT 03 – DEVICE MANAGEMENT

Đọc Master Prompt + API Contract + DB schema. Chỉ sửa `/backend/**`.

## GET /api/devices
List/filter theo contract: status/type/keyword. Empty → 200 [].

## POST /api/devices
ADMIN only. Validate `ma_thiet_bi`, `ten_thiet_bi`, optional type/location/description/status. Duplicate code → 409. 201.

## GET /api/devices/{id}
200/404.

## PATCH /api/devices/{id}
Chỉ allowed fields. Status phải lấy từ schema thật. Nếu schema đang dùng baseline: ACTIVE, MAINTENANCE, BROKEN, INACTIVE. Invalid → 400. Log nếu log contract yêu cầu.

Authorization ưu tiên API Contract. Không tự mở quyền rộng hơn.

Verify: create, duplicate, list, filter, detail, update info, update status, invalid status, missing id.


---

# PROMPT 04 – TICKET CORE MANAGEMENT

Đọc Master Prompt + API Contract + DB schema. Chỉ sửa `/backend/**`.

## POST /api/tickets
1. validate body;
2. xác định creator;
3. validate device nếu có;
4. validate category/priority theo schema;
5. status mặc định OPEN;
6. BEGIN;
7. INSERT TICKETS;
8. INSERT TICKET_HISTORY(CREATED);
9. COMMIT;
10. 201.
Lỗi → ROLLBACK.

## GET /api/tickets
List/search/filter theo contract: status, priority, category, technician_id, user_id, keyword. Dùng parameterized query.
Visibility theo role: USER chỉ ticket có quyền xem; TECHNICIAN ticket liên quan/được phân công; ADMIN toàn bộ. Empty → 200 [].

## GET /api/tickets/{id}
404 nếu thiếu; 403 nếu không có quyền; trả ticket detail theo contract.

## PATCH /api/tickets/{id}
Chỉ field nội dung/phân loại được contract cho phép. Không assign/status/close bằng generic PATCH. Nếu update/classify thì ghi history cùng transaction.

Verify: create valid/invalid/missing device; list; filters; detail; forbidden; missing; update content; classify; history.


---

# PROMPT 05 – ASSIGN + LIFECYCLE + CLOSE + HISTORY + LOGGING

Đọc Master Prompt + API Contract + DB schema + Log Contract. Chỉ sửa `/backend/**`.

## PATCH /api/tickets/{id}/assign
- validate ticket/technician;
- ticket missing → 404;
- reject CLOSED;
- technician missing → 404;
- role phải TECHNICIAN và ACTIVE;
- BEGIN;
- update technician_id;
- nếu OPEN → ASSIGNED;
- history ASSIGNED;
- log;
- COMMIT;
- 200.

## PATCH /api/tickets/{id}/status
Central transition:
`OPEN→ASSIGNED`, `ASSIGNED→IN_PROGRESS`, `IN_PROGRESS→RESOLVED`, `RESOLVED→CLOSED`, `CLOSED→none`.
Invalid transition → 400. Dùng transaction. Set resolved_at/closed_at nếu schema có. Ghi STATUS_CHANGED history + log.

## PATCH /api/tickets/{id}/close
Chỉ `RESOLVED→CLOSED`; already CLOSED không duplicate history; sai trạng thái → 400; transaction + CLOSED history + log.

## GET /api/tickets/{id}/history
Check ticket + authorization; trả history theo thời gian; ticket missing → 404.

## Logging
Tuân thủ docs/log-format.md. Event name ưu tiên contract. Không log secret.

Negative verify: assign non-tech/inactive; invalid transition; close trước RESOLVED; forbidden access.

Full verify: create→assign→IN_PROGRESS→RESOLVED→close→history→DB→log.


---

# PROMPT 06 – FINAL BACKEND CHECK TRƯỚC KHI NỘP

Không thêm chức năng ngoài đặc tả. Chỉ sửa `/backend/**`.

Kiểm tra đủ 19 API trong Master Prompt, mỗi endpoint đánh PASS/FAIL/BLOCKED.

Audit:
- method/path/request/response/status/authorization đúng contract;
- query đúng schema;
- bcrypt, no plaintext/no hash response;
- parameterized queries;
- không secret/raw SQL/traceback;
- 400/401/403/404/409/500 nhất quán;
- create/update/classify/assign/status/close ghi history đúng transaction;
- logging đúng format Perl dùng.

Full smoke nếu môi trường cho phép:
```text
health
→ login ADMIN
→ create USER
→ create TECHNICIAN
→ disable/enable USER
→ create/update device
→ login USER
→ create/list/detail/update ticket
→ ADMIN assign TECHNICIAN
→ TECHNICIAN IN_PROGRESS
→ TECHNICIAN RESOLVED
→ close
→ history
→ verify MySQL
→ verify log
```

Không sửa test expectation để ép pass.

Trả:
```text
BACKEND_FINAL_REPORT
Endpoint pass: X/19
Endpoint fail:
Endpoint blocked:
Auth:
User Management:
Device Management:
Ticket Management:
Lifecycle:
History:
Logging:
MySQL:
Security:
Contract drift:
Tests actually run:
Known issues:
BACKEND_READY_FOR_INTEGRATION: YES/NO
BACKEND_READY_FOR_SUBMISSION: YES/NO
```


---

# CODEX / ANTIGRAVITY WRAPPER

Trước task:
1. Đọc `00_MASTER_BACKEND_PROMPT.md`.
2. Inspect repo thực tế.
3. Đọc API Contract, schema, DB/log contract liên quan.
4. Writable scope chỉ `/backend/**`.
5. Lập plan file-level trước khi sửa.
6. Implement working code, không pseudo-code.
7. Chạy command/test nếu môi trường cho phép.
8. Không fabricate kết quả.
9. Không refactor unrelated code.
10. Không tự đổi contract/schema/framework.

Trước code trả `TASK ANALYSIS`.
Sau code trả `IMPLEMENTATION RESULT`.
Sau đó thực hiện prompt task được nối tiếp.


---

# ONE-SHOT – HOÀN THIỆN TOÀN BỘ BACKEND

Đọc Master Prompt. Chỉ sửa `/backend/**`.

Phase 1: audit contracts/schema/backend.
Phase 2: xác nhận FastAPI, MYSQL_*, health, DB connector, error handler.
Phase 3: Auth + User Management.
Phase 4: Device Management.
Phase 5: Ticket Core create/list/filter/detail/update/classify.
Phase 6: Assign + lifecycle + close + history + logging.
Phase 7: security/status/response/transaction consistency.
Phase 8: full smoke.

Stop only affected feature nếu schema/contract thiếu; tiếp tục feature độc lập nếu an toàn. Không dùng best guess để vượt contract/schema blocker.

Cuối cùng tạo bảng:
`Feature | Endpoint | Status | Verified | Blocker`

Trả thêm:
`BACKEND_READY_FOR_INTEGRATION: YES/NO`
`BACKEND_READY_FOR_SUBMISSION: YES/NO`


---

# BACKEND ACCEPTANCE CHECKLIST

## System
- [ ] FastAPI start clean
- [ ] `/api/health` 200
- [ ] MySQL qua `MYSQL_*`
- [ ] no hard-coded secret

## Auth/User
- [ ] login success/fail/inactive
- [ ] bcrypt
- [ ] no password_hash response
- [ ] user list/create/detail/update/status
- [ ] ADMIN enforcement
- [ ] duplicate → 409

## Device
- [ ] list/filter/create/detail/update
- [ ] invalid enum → 400
- [ ] duplicate code → 409

## Ticket
- [ ] create/list/search/filter/detail/update/classify
- [ ] role visibility
- [ ] 403/404 đúng

## Lifecycle/History
- [ ] assign TECHNICIAN
- [ ] OPEN→ASSIGNED→IN_PROGRESS→RESOLVED→CLOSED
- [ ] invalid transition → 400
- [ ] close before RESOLVED → 400
- [ ] CREATED/UPDATED/CLASSIFIED/ASSIGNED/STATUS_CHANGED/CLOSED history
- [ ] history endpoint

## DB/Log/Security
- [ ] multi-write transaction + rollback
- [ ] parameterized query
- [ ] safe 500
- [ ] no raw SQL/traceback/secret
- [ ] log đúng docs/log-format.md
- [ ] Perl parse được log

## Ready
- [ ] Frontend dùng được API
- [ ] Postman test được API
- [ ] MySQL đúng
- [ ] không blocker Must
