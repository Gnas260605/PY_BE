# CS466 Sang AI Skill Bundle


<!-- FILE: SKILL.md -->

---
name: cs466-sang-backend
description: Dùng khi AI/Coding Agent triển khai Backend/API Python thuộc phạm vi Huỳnh Thanh Sang cho đồ án CS466 Nhóm 1. Skill khóa phạm vi, Sprint, API, thuật toán, DB boundary, Git ownership và Definition of Done để tránh code sai chức năng hoặc xung đột với thành viên khác.
---

# CS466 – Huỳnh Thanh Sang Backend/API Skill

## 1. Vai trò của AI

Bạn là Coding Agent phụ trách **chỉ phần Backend/API của Huỳnh Thanh Sang**.

Bạn phải triển khai đúng kế hoạch Scrum 4 tuần của nhóm và không mở rộng scope ngoài backlog được giao.

## 2. Nhiệm vụ chính của Sang

- Python Backend.
- Flask **hoặc** FastAPI theo framework repository đã khóa.
- REST API.
- HTTP/JSON.
- Kết nối Backend với MySQL.
- Đăng nhập cơ bản.
- Ticket API:
  - tạo;
  - danh sách;
  - chi tiết;
  - cập nhật;
  - gán kỹ thuật viên;
  - cập nhật trạng thái;
  - đóng ticket.
- Device API:
  - danh sách/chi tiết;
  - cập nhật trạng thái.
- Validation.
- Chuẩn hóa HTTP response/status code.
- Ghi log theo format mà nhóm đã khóa.
- Hỗ trợ Postman/QA bằng cách giữ API ổn định; không sở hữu test module của Quân.

## 3. Thứ tự nguồn chuẩn

Khi có mâu thuẫn, ưu tiên:

1. `/docs/api-contract.md` trong repository.
2. `/database/schema.sql` và DB contract do Lộc quản lý.
3. `/docs/log-format.md`.
4. Code hiện có đã merge vào `develop`.
5. Kế hoạch Sprint/Backlog trong bộ skill này.
6. Các ví dụ trong skill.

**Không dùng ví dụ trong skill để ghi đè contract thật của repository.**

## 4. Hard boundaries

Mặc định chỉ được sửa:

```text
/backend/**
```

Không tự sửa:

```text
/database/**
/perl/**
/frontend/**
/tests/**
/postman/**
/docs/**
README.md
.env.example
root config
```

Nếu task yêu cầu thay đổi ngoài `/backend/**`:
1. DỪNG phần thay đổi đó.
2. Ghi rõ file cần owner khác sửa.
3. Đề xuất diff/contract cần thay đổi.
4. Chờ owner hoặc người tích hợp xử lý.

## 5. Framework gate

Tài liệu dự án cho phép **Flask hoặc FastAPI** nhưng chưa mặc định một framework duy nhất.

Trước khi code:
1. kiểm tra `requirements*.txt`, `pyproject.toml`, imports và backend skeleton;
2. nếu repository đã dùng Flask → tiếp tục Flask;
3. nếu repository đã dùng FastAPI → tiếp tục FastAPI;
4. nếu chưa có framework hoặc có cả hai nhưng không rõ lựa chọn → **không tự quyết định**; báo blocker `FRAMEWORK_DECISION_REQUIRED`.

Không tự chuyển framework giữa Sprint.

## 6. Schema gate

Không tự invent field DB.

Đặc biệt:
- tài liệu khái quát chỉ chắc chắn có `USERS`, `DEVICES`, `TICKETS`, `TICKET_HISTORY`;
- auth cần định danh đăng nhập/mật khẩu nhưng ERD khái quát chưa khóa các field này.

Trước `AUTH-01`, phải kiểm tra schema thật.
Nếu thiếu field auth → báo blocker cho Lộc/Ân, không tự ALTER TABLE.

## 7. Quy trình bắt buộc trước khi code

Cho mỗi task:
1. Xác định Task ID.
2. Đọc Sprint tương ứng.
3. Đọc API Contract.
4. Đọc DB schema liên quan.
5. Đọc log format nếu task có ghi log.
6. Liệt kê file dự kiến sửa.
7. Kiểm tra file đều thuộc `/backend/**`.
8. Kiểm tra dependency đã có.
9. Chỉ sau đó mới code.

## 8. Quy trình sau khi code

1. Chạy ứng dụng local.
2. Chạy smoke check phù hợp.
3. Kiểm tra status code.
4. Kiểm tra JSON response.
5. Kiểm tra transaction/rollback nếu có ghi DB.
6. Kiểm tra log.
7. Không làm hỏng API Sprint trước.
8. Báo:
   - file đã sửa;
   - endpoint đã làm;
   - test/smoke đã chạy;
   - blocker;
   - contract change nếu có.

## 9. Definition of Done tối thiểu

Một task Backend chỉ được coi là DONE khi:
- chạy local không lỗi chặn luồng;
- đúng API Contract;
- đúng DB Contract;
- validation chính có;
- happy path chạy được;
- lỗi chính trả đúng 4xx/5xx;
- DB write dùng transaction khi có nhiều write liên quan;
- ghi history/log nếu thuật toán yêu cầu;
- không sửa module owner khác;
- merge vào `develop` không phá chức năng Sprint trước.

## 10. Tài liệu bắt buộc đọc tiếp

- `01_SCOPE_AND_BOUNDARIES.md`
- `02_SPRINT_PLAN.md`
- `03_API_CONTRACT.md`
- `04_DATABASE_AND_INTEGRATION_CONTRACT.md`
- `05_BACKEND_ARCHITECTURE_RULES.md`
- `06_ALGORITHMS.md`
- `07_ERROR_RESPONSE_LOGGING.md`
- `08_ACCEPTANCE_AND_TESTING.md`
- `09_GIT_WORKFLOW.md`
- `10_AI_EXECUTION_PLAYBOOK.md`


<!-- FILE: 01_SCOPE_AND_BOUNDARIES.md -->

# 01 – Scope & Ownership của Huỳnh Thanh Sang

## Vai trò

**Backend/API bằng Python.**

Phạm vi lấy từ phân công nhóm:
- nghiên cứu Flask/FastAPI;
- REST API, HTTP/JSON;
- API tạo/xem/cập nhật/phân loại/đóng yêu cầu;
- đăng nhập;
- xử lý nghiệp vụ cơ bản;
- kết nối MySQL;
- hỗ trợ kiểm thử API qua Postman.

## Module Sang sở hữu

```text
/backend/auth/**
/backend/tickets/**
/backend/devices/**
/backend/**   # các thành phần backend chung nếu đã thuộc backend skeleton
```

## Backlog Sang

### Sprint 1
- Backend skeleton.
- `GET /api/health`.
- Route skeleton.
- DB connector.

### Sprint 2
- `AUTH-01` – Đăng nhập.
- `TKT-01` – Tạo ticket.
- `TKT-02` – Danh sách ticket.
- `TKT-03` – Chi tiết ticket.
- `TKT-04` – Cập nhật nội dung ticket.
- Kết nối MySQL thật.

### Sprint 3
- `TKT-05` – Gán kỹ thuật viên.
- `TKT-06` – Cập nhật trạng thái.
- `TKT-07` – Đóng ticket.
- Ticket history ở các thao tác thay đổi.
- `DEV-01` – Danh sách/chi tiết thiết bị.
- `DEV-02` – Cập nhật trạng thái thiết bị.
- Validation.
- Logging.

### Sprint 4
- Fix Backend bug.
- Chuẩn hóa response.
- Chuẩn hóa HTTP status.
- Hỗ trợ regression.
- Không thêm feature mới.

## Không thuộc scope của Sang

### Lộc
```text
/database/**
/perl/**
```
Không tự:
- sửa schema;
- đổi tên cột;
- thêm migration;
- đổi PK/FK;
- viết Perl.

### Phương
```text
/frontend/**
```
Không sửa UI để “làm cho API chạy”.

### Quân
```text
/tests/**
/postman/**
```
Không sửa test expectation chỉ để test pass.

### Ân
```text
/docs/**
README.md
.env.example
root integration config
```
Không tự đổi contract.

## Reviewer

- Backend feature: **Quân** review hành vi/test.
- Thay đổi DB: **Lộc** phải xác nhận.
- Thay đổi API contract: **Ân** điều phối, Phương + Quân đồng bộ.


<!-- FILE: 02_SPRINT_PLAN.md -->

# 02 – Kế hoạch Backend theo 4 Sprint

## Sprint 1 – Nền tảng & khóa contract

### Mục tiêu
Có backend skeleton chạy được và kết nối được với DB contract v1.

### Sang phải làm
- detect và dùng framework đã khóa;
- cấu trúc backend;
- endpoint:
  ```http
  GET /api/health
  ```
- route skeleton cho auth/ticket/device;
- DB connector theo schema/config hiện có;
- không implement business feature lớn trước khi API/DB contract khóa.

### Output cuối tuần
- Backend start được.
- `/api/health` trả 200.
- DB connection smoke check pass.
- Không có import/runtime error chặn startup.

### Tag chung
`v0.1-sprint1`

---

## Sprint 2 – MVP login + CRUD ticket

### Mục tiêu
Luồng MVP:

```text
Login → Create Ticket → List → Detail → Update → MySQL
```

### Sang phải làm
- `AUTH-01`
- `TKT-01`
- `TKT-02`
- `TKT-03`
- `TKT-04`

### Output cuối tuần
- API MVP.
- Postman của Quân có thể test login + CRUD.
- UI của Phương có contract ổn định để tích hợp.

### Tag chung
`v0.5-sprint2`

---

## Sprint 3 – Full lifecycle + Device

### Mục tiêu
Hoàn thiện backend bắt buộc trước feature freeze.

### Sang phải làm
- `TKT-05` assign;
- `TKT-06` status;
- `TKT-07` close;
- ghi `TICKET_HISTORY`;
- `DEV-01`;
- `DEV-02`;
- validation;
- logging;
- xử lý lỗi/status code.

### Lifecycle bắt buộc

```text
OPEN
  ↓
ASSIGNED
  ↓
IN_PROGRESS
  ↓
RESOLVED
  ↓
CLOSED
```

### Output cuối tuần
- Full Backend.
- Không còn feature Must chưa làm.
- Sẵn sàng integration test.
- **FEATURE FREEZE**.

### Tag chung
`v0.9-sprint3`

---

## Sprint 4 – Ổn định & release

### Sang chỉ làm
- fix bug;
- response consistency;
- status code consistency;
- transaction/rollback bug;
- logging bug;
- regression fixes.

### Sang không được
- thêm endpoint mới tùy ý;
- đổi schema;
- redesign architecture;
- đổi framework;
- đổi JSON contract nếu không phải critical fix được cả nhóm chấp nhận.

### Output
Backend stable cho `v1.0`.


<!-- FILE: 03_API_CONTRACT.md -->

# 03 – API Contract cho phạm vi Sang

> Đây là contract theo plan. Nếu `/docs/api-contract.md` trong repository khác file này thì **contract trong repository thắng**.

## Quy ước

Base path:

```text
/api
```

JSON:
- request/response dùng JSON trừ endpoint không có body;
- không tự đổi field naming sau khi contract khóa.

## S1

### GET /api/health

Mục tiêu: xác nhận Backend đang chạy.

Default response:

```json
{
  "status": "ok"
}
```

Status:
- `200 OK`

---

## S2 – Authentication

### POST /api/login

Input **phải đọc contract/schema thật**.

Không tự invent:
- `email`;
- `username`;
- `password_hash`;
- JWT/session schema.

Acceptance từ plan:
- đúng dữ liệu → `200`;
- sai thông tin xác thực → `401`.

Nếu schema auth chưa đủ:
`BLOCKED: AUTH_SCHEMA_REQUIRED`.

---

## S2 – Ticket

### POST /api/tickets

Contract plan mẫu:

```json
{
  "title": "Máy in không hoạt động",
  "description": "Không thể in tài liệu",
  "device_id": 1
}
```

Response mẫu:

```json
{
  "id": 10,
  "status": "OPEN",
  "message": "Created"
}
```

Status mặc định:
- `201 Created`
- `400 Bad Request` nếu input sai
- `404 Not Found` nếu contract yêu cầu reference phải tồn tại
- `500` cho lỗi ngoài dự kiến sau rollback

### GET /api/tickets

Output:
- JSON array/list theo contract thật.

Status:
- `200 OK`

### GET /api/tickets/{id}

Status:
- `200 OK`
- `404 Not Found`

### PATCH /api/tickets/{id}

Mục tiêu:
- cập nhật **các field được API Contract cho phép**.

Không tự cho phép client sửa:
- `id`;
- FK/hệ thống field nếu contract không cho;
- `status` nếu đã có endpoint status riêng.

Status:
- `200 OK`
- `400 Bad Request`
- `404 Not Found`

---

## S3 – Ticket lifecycle

### PATCH /api/tickets/{id}/assign

Body điển hình:

```json
{
  "technician_id": 2
}
```

Chỉ dùng key này nếu contract thật đã khóa.

Hành vi:
- kiểm tra ticket;
- kiểm tra technician;
- cập nhật assignee theo schema thật;
- nếu trạng thái hiện tại `OPEN`, chuyển `ASSIGNED`;
- ghi history;
- ghi log.

### PATCH /api/tickets/{id}/status

Body điển hình:

```json
{
  "status": "IN_PROGRESS"
}
```

Lifecycle:

```text
OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
```

Không cho transition ngoài lifecycle nếu contract không cho phép.

### PATCH /api/tickets/{id}/close

Hành vi plan:
- chỉ đóng ticket hợp lệ;
- ưu tiên yêu cầu current status = `RESOLVED`;
- update `CLOSED`;
- history;
- log.

---

## S3 – Device

### GET /api/devices

- `200 OK`

### GET /api/devices/{id}

- `200 OK`
- `404 Not Found`

### PATCH /api/devices/{id}

Mục tiêu:
- cập nhật status của device theo tập giá trị đã khóa trong DB/API contract.

Không invent device status enum.

---

## Ticket History

Plan yêu cầu history để UI hiển thị.

AI phải kiểm tra contract thật:
- nếu `GET /api/tickets/{id}` đã chứa `history` → dùng cách đó;
- nếu contract có endpoint riêng → implement endpoint đó;
- nếu chưa có contract → không tự thêm endpoint, báo:
  `TICKET_HISTORY_READ_CONTRACT_REQUIRED`.

## Quy tắc không phá contract

Không tự:
- đổi `/api/tickets` thành `/tickets`;
- đổi `title` thành `tieu_de` ở JSON chỉ vì DB dùng tên khác;
- đổi `PATCH` thành `PUT`;
- thêm wrapper `data`/`result` nếu contract không quy định.


<!-- FILE: 04_DATABASE_AND_INTEGRATION_CONTRACT.md -->

# 04 – Database & Integration Contract

## DB owner

**Trần Duy Lộc** là owner `/database/**`.

Sang chỉ tiêu thụ schema từ Backend.

## Bảng cốt lõi đã xác định

```text
USERS
DEVICES
TICKETS
TICKET_HISTORY
```

Mô hình khái quát trong tài liệu:

```text
USERS(id, ho_ten, vai_tro, ...)
DEVICES(id, ten_thiet_bi, trang_thai, ...)
TICKETS(id, tieu_de, trang_thai, user_id, device_id, ...)
TICKET_HISTORY(id, ticket_id, chi_tiet_cap_nhat, thoi_gian, ...)
```

Dấu `...` có nghĩa:
- schema thật có thể có thêm field;
- AI **không được tự đoán field còn thiếu**.

## Mapping API ↔ DB

API có thể dùng key tiếng Anh:

```text
title
description
device_id
status
```

DB có thể dùng:

```text
tieu_de
trang_thai
device_id
...
```

Mapping phải nằm trong Backend/service/repository layer.
Không bắt Frontend dùng tên cột DB.

## Auth blocker

Tài liệu khái quát chưa khóa:
- username/email;
- password/password_hash;
- token/session table.

Vì vậy trước `AUTH-01`:
1. đọc `/database/schema.sql`;
2. xác định field xác thực thật;
3. xác định mechanism đã được nhóm chốt;
4. nếu chưa có → dừng và báo Lộc/Ân.

## Transaction rule

Dùng transaction khi một nghiệp vụ ghi nhiều bảng.

Ví dụ Create Ticket:

```text
BEGIN
  INSERT TICKETS
  INSERT TICKET_HISTORY(CREATED)
COMMIT
```

Nếu bất kỳ bước nào lỗi:

```text
ROLLBACK
```

Tương tự:
- assign + history;
- status + history;
- close + history.

## Foreign key rule

Trước write có reference:
- `user_id`;
- `device_id`;
- `technician_id` nếu schema có;

phải xử lý theo DB contract.

Không tạo dữ liệu mồ côi.

## DB connection

- config lấy từ cơ chế đã có trong repo;
- không hard-code password;
- không commit credential;
- không sửa `.env.example` vì file root do Ân quản lý;
- nếu cần biến môi trường mới → đề xuất cho Ân.

## Integration points

```text
Frontend (Phương)
       ↓ HTTP/JSON
Backend (Sang)
       ↓ SQL/driver/ORM theo repo
MySQL (Lộc)
       ↓ dữ liệu/log
Perl (Lộc)
```

Backend phải giữ interface ổn định để Phương và Quân không bị block.


<!-- FILE: 05_BACKEND_ARCHITECTURE_RULES.md -->

# 05 – Backend Architecture Rules

## Mục tiêu

Giữ Backend dễ merge, ít conflict, không trộn trách nhiệm.

## Rule 1 – Tôn trọng cấu trúc hiện có

Nếu repository đã có cấu trúc Backend:
- tiếp tục theo cấu trúc đó;
- không refactor toàn bộ chỉ để “đẹp hơn”.

Nếu backend còn trống, cấu trúc tham khảo tối thiểu:

```text
backend/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── auth/
│   ├── tickets/
│   ├── devices/
│   └── common/
└── requirements.txt   # chỉ nếu dependency file thuộc /backend
```

Không bắt buộc tạo đúng cấu trúc trên nếu repo đã khác.

## Rule 2 – Tách HTTP và nghiệp vụ nếu project cho phép

Tối thiểu nên tránh nhét tất cả SQL + validation + response vào một file.

Mẫu trách nhiệm:

```text
route/controller
  ↓
service/business logic
  ↓
repository/db access
```

Nếu project nhỏ và đang dùng pattern khác:
- giữ nhất quán;
- không over-engineer.

## Rule 3 – Không SQL/string từ input

- dùng parameterized query hoặc ORM/driver an toàn;
- không nối chuỗi raw input vào SQL.

## Rule 4 – Validation

Validate:
- required field;
- type;
- enum/status theo contract;
- ID format;
- state transition.

Không invent business rule ngoài contract/plan.

## Rule 5 – Consistent response

Dùng cùng pattern mà backend hiện có.

Không để endpoint A trả:

```json
{"message": "..."}
```

còn endpoint B tự đổi thành:

```json
{"data": {"result": "..."}}
```

nếu contract không yêu cầu.

## Rule 6 – Lifecycle tập trung

Không viết transition logic rải rác.

Nên có một nguồn duy nhất:

```text
OPEN -> ASSIGNED
ASSIGNED -> IN_PROGRESS
IN_PROGRESS -> RESOLVED
RESOLVED -> CLOSED
```

Ví dụ pseudocode:

```python
ALLOWED_TRANSITIONS = {
    "OPEN": {"ASSIGNED"},
    "ASSIGNED": {"IN_PROGRESS"},
    "IN_PROGRESS": {"RESOLVED"},
    "RESOLVED": {"CLOSED"},
    "CLOSED": set(),
}
```

Nếu contract thật thay đổi, cập nhật một chỗ.

## Rule 7 – DB write + History

Mọi thay đổi lifecycle phải ghi:
- record chính;
- `TICKET_HISTORY`;
- log nếu log format đã khóa.

Ba bước phải nhất quán transaction.

## Rule 8 – Không dependency drift

Không thêm package mới nếu:
- stdlib/framework hiện tại làm được;
- package chưa được team chấp nhận.

Nếu cần package:
- nêu lý do;
- nêu file dependency cần owner cập nhật nếu file đó ngoài scope.

## Rule 9 – No secret

Không hard-code:
- DB password;
- secret key;
- token secret.

## Rule 10 – Sprint 4

Không refactor lớn.
Chỉ fix tối thiểu để ổn định release.


<!-- FILE: 06_ALGORITHMS.md -->

# 06 – Thuật toán chi tiết Backend của Huỳnh Thanh Sang

Các thuật toán dưới đây là **behavior contract** cho AI.  
Nếu API/DB contract thật khác, phải điều chỉnh thuật toán theo contract thật nhưng không mở rộng scope.

---

# A00 – Health Check

**Task:** Sprint 1  
**Endpoint:** `GET /api/health`

## Input
Không có.

## Algorithm
1. Nhận request.
2. Xác nhận application process đang hoạt động.
3. Nếu plan/repo yêu cầu DB health:
   - thực hiện truy vấn nhẹ hoặc ping connection;
   - không mutate DB.
4. Trả JSON health.
5. Không log stack trace ở response.

## Output
- `200 OK` khi healthy.
- Nếu DB health bắt buộc và DB không kết nối được: dùng error policy của repo.

---

# A01 – Đăng nhập

**Task:** `AUTH-01`  
**Endpoint:** `POST /api/login`

## Precondition
- API contract auth đã khóa.
- Schema USERS có đủ field xác thực.
- Cơ chế xác thực đã được nhóm quyết định.

## Input
Theo contract thật, ví dụ:

```text
identifier + password
```

## Algorithm
1. Parse JSON body.
2. Validate required field.
3. Normalize identifier chỉ nếu contract yêu cầu.
4. Query `USERS` bằng identifier đã khóa.
5. Nếu user không tồn tại:
   - ghi `LOGIN_FAILED` nếu log format cho phép;
   - trả `401 Unauthorized`.
6. Kiểm tra password theo mechanism của project.
7. Nếu password sai:
   - ghi `LOGIN_FAILED`;
   - trả `401 Unauthorized`.
8. Nếu đúng:
   - tạo session/token **chỉ theo cơ chế đã khóa**;
   - ghi `LOGIN_SUCCESS`;
   - trả thông tin user cần thiết:
     - `user_id`;
     - `ho_ten`;
     - `vai_tro`;
     - auth artifact nếu contract có.
9. Không trả password/password_hash.

## Error
- input sai format → `400`
- auth sai → `401`
- lỗi ngoài dự kiến → `500`

## Không được
- tự chọn JWT;
- tự thêm cột password;
- hard-code user demo trong endpoint.

---

# A02 – Tạo Ticket

**Task:** `TKT-01`  
**Endpoint:** `POST /api/tickets`

## Input
Theo API Contract. Mẫu plan:

```json
{
  "title": "...",
  "description": "...",
  "device_id": 1
}
```

User tạo ticket lấy theo auth context hoặc field contract.

## Algorithm
1. Parse body.
2. Validate required field.
3. Xác định user tạo ticket theo contract.
4. Kiểm tra user tồn tại nếu cần.
5. Nếu `device_id` có:
   - kiểm tra device tồn tại.
6. Gán status ban đầu:
   ```text
   OPEN
   ```
7. Begin transaction.
8. Insert `TICKETS`.
9. Lấy `ticket_id` vừa tạo.
10. Insert `TICKET_HISTORY` với event/chi tiết `CREATED` theo schema thật.
11. Ghi log theo log-format, có TicketID nếu contract log yêu cầu.
12. Commit transaction.
13. Serialize response.
14. Trả `201 Created`.

## Rollback
Nếu bước 8–11 lỗi:
1. rollback;
2. không để ticket/history nửa vời;
3. trả lỗi theo error policy.

## Output
Mẫu:

```json
{
  "id": 10,
  "status": "OPEN",
  "message": "Created"
}
```

---

# A03 – Lấy danh sách Ticket

**Task:** `TKT-02`  
**Endpoint:** `GET /api/tickets`

## Algorithm
1. Parse query params **chỉ những filter đã có trong API contract**.
2. Validate filter.
3. Query `TICKETS`.
4. Join USERS/DEVICES chỉ khi response contract cần dữ liệu hiển thị.
5. Không query N+1 nếu có cách query gọn trong kiến trúc hiện tại.
6. Map DB row/model → API JSON.
7. Trả danh sách.
8. Không trả field nội bộ/secret.

## Output
- `200 OK`
- empty result → trả danh sách rỗng, không tự biến thành 404.

---

# A04 – Lấy chi tiết Ticket

**Task:** `TKT-03`  
**Endpoint:** `GET /api/tickets/{id}`

## Algorithm
1. Validate `id`.
2. Query ticket theo id.
3. Nếu không có → `404`.
4. Lấy dữ liệu user/device nếu response contract cần.
5. Lấy history:
   - nếu contract detail bao gồm history;
   - nếu không, không tự thêm.
6. Serialize JSON.
7. Trả `200`.

---

# A05 – Cập nhật nội dung Ticket

**Task:** `TKT-04`  
**Endpoint:** `PATCH /api/tickets/{id}`

## Algorithm
1. Validate `id`.
2. Parse body.
3. Xây allowed-field set từ API Contract.
4. Loại/reject field không được cập nhật.
5. Nếu body không có field hợp lệ → `400`.
6. Query ticket.
7. Nếu không có → `404`.
8. Begin transaction nếu update kèm history theo contract.
9. Update chỉ các field được phép.
10. Nếu project yêu cầu lưu history cho content update:
    - insert history theo schema/contract.
11. Ghi log nếu log-format yêu cầu.
12. Commit.
13. Return updated ticket/response theo contract.

## Không được
Client tự PATCH:
- `id`;
- `status` qua endpoint này nếu status có endpoint riêng;
- assignee nếu assign có endpoint riêng;
- DB technical field.

---

# A06 – Gán kỹ thuật viên

**Task:** `TKT-05`  
**Endpoint:** `PATCH /api/tickets/{id}/assign`

## Input
`technician_id` theo contract.

## Algorithm
1. Validate ticket_id và technician_id.
2. Query ticket.
3. Nếu không có → `404`.
4. Nếu ticket `CLOSED` → reject theo business rule plan.
5. Query technician trong `USERS`.
6. Nếu không có → `404`.
7. Kiểm tra `vai_tro` phù hợp theo role values trong DB contract.
8. Nếu role không hợp lệ → `400` hoặc `403` theo API contract.
9. Begin transaction.
10. Update assignee field **theo schema thật**.
11. Nếu current status = `OPEN`:
    - update status → `ASSIGNED`.
12. Insert `TICKET_HISTORY`:
    - event ASSIGNED;
    - technician reference/chi tiết theo schema thật.
13. Ghi log.
14. Commit.
15. Return `200`.

## Rollback
Bất kỳ DB write nào lỗi → rollback toàn transaction.

---

# A07 – Cập nhật trạng thái Ticket

**Task:** `TKT-06`  
**Endpoint:** `PATCH /api/tickets/{id}/status`

## Input

```text
ticket_id
new_status
```

## Allowed lifecycle

```text
OPEN -> ASSIGNED
ASSIGNED -> IN_PROGRESS
IN_PROGRESS -> RESOLVED
RESOLVED -> CLOSED
CLOSED -> (none)
```

## Algorithm
1. Validate id.
2. Parse `new_status`.
3. Kiểm tra `new_status` nằm trong status enum đã khóa.
4. Query ticket/current status.
5. Nếu không có → `404`.
6. Nếu `new_status == current_status`:
   - xử lý theo API contract;
   - không tự tạo history giả nếu không thay đổi.
7. Kiểm tra:
   ```text
   new_status ∈ ALLOWED_TRANSITIONS[current_status]
   ```
8. Nếu sai transition → `400`.
9. Begin transaction.
10. Update `TICKETS.trang_thai`.
11. Insert `TICKET_HISTORY` mô tả old → new.
12. Ghi log.
13. Commit.
14. Trả `200`.

---

# A08 – Đóng Ticket

**Task:** `TKT-07`  
**Endpoint:** `PATCH /api/tickets/{id}/close`

## Algorithm
1. Validate id.
2. Query ticket.
3. Nếu không có → `404`.
4. Nếu đã `CLOSED`:
   - trả theo contract; mặc định không thực hiện write lần hai.
5. Theo plan, chỉ chấp nhận close từ `RESOLVED`.
6. Nếu current != `RESOLVED` → `400`.
7. Begin transaction.
8. Update status → `CLOSED`.
9. Nếu schema có `closed_at`, chỉ update nếu field thật tồn tại/contract dùng.
10. Insert history `CLOSED`.
11. Ghi log.
12. Commit.
13. Trả `200`.

---

# A09 – Lấy danh sách Thiết bị

**Task:** `DEV-01`  
**Endpoint:** `GET /api/devices`

## Algorithm
1. Parse filter chỉ nếu contract có.
2. Query `DEVICES`.
3. Serialize:
   - id;
   - tên thiết bị;
   - trạng thái;
   - field khác chỉ theo contract.
4. Trả `200`.
5. Không có dữ liệu → list rỗng.

---

# A10 – Lấy chi tiết Thiết bị

**Task:** `DEV-01`  
**Endpoint:** `GET /api/devices/{id}`

## Algorithm
1. Validate id.
2. Query device.
3. Nếu không có → `404`.
4. Serialize theo contract.
5. Trả `200`.

---

# A11 – Cập nhật trạng thái Thiết bị

**Task:** `DEV-02`  
**Endpoint:** `PATCH /api/devices/{id}`

## Algorithm
1. Validate id.
2. Parse body.
3. Đọc tập device status hợp lệ từ contract/schema.
4. Không tự invent enum.
5. Query device.
6. Nếu không có → `404`.
7. Nếu status invalid → `400`.
8. Update `DEVICES.trang_thai`.
9. Ghi log nếu log-format yêu cầu.
10. Return `200` với device đã cập nhật.

---

# A12 – Ghi Ticket History

Đây là internal algorithm, không nhất thiết là endpoint.

## Input
- ticket_id
- event type
- chi tiết update
- timestamp do DB/app theo convention project

## Algorithm
1. Chỉ gọi sau khi ticket tồn tại.
2. Chuẩn hóa event name theo contract.
3. Insert vào `TICKET_HISTORY`.
4. Đặt trong cùng transaction với thay đổi ticket.
5. Không commit riêng trước khi ticket update thành công.

## Event tối thiểu theo plan
- CREATED
- ASSIGNED
- STATUS_CHANGED
- CLOSED

Có thể có UPDATE nếu contract thật yêu cầu.

---

# A13 – DB Transaction Wrapper

## Algorithm
1. Acquire connection/session.
2. Begin transaction.
3. Run write operations.
4. Nếu tất cả thành công:
   - commit.
5. Nếu exception:
   - rollback.
   - map exception → safe API error.
6. Release/close session theo framework/driver convention.
7. Không expose raw SQL error cho client.

---

# A14 – Response/Error Mapping

## Algorithm
1. Validation error → `400`.
2. Authentication failure → `401`.
3. Permission failure → `403` chỉ khi contract/role rule có.
4. Resource missing → `404`.
5. Invalid lifecycle transition → `400`.
6. Unexpected DB/runtime failure → `500`.
7. Response body theo format chung của project.
8. Log chi tiết server-side.
9. Không gửi stack trace, password, SQL credential ra client.

---

# A15 – Backend Logging

## Precondition
Đọc `/docs/log-format.md`.

## Algorithm
1. Xác định event:
   - LOGIN_SUCCESS/FAILED;
   - TICKET_CREATED;
   - TICKET_ASSIGNED;
   - TICKET_STATUS_CHANGED;
   - TICKET_CLOSED;
   - DEVICE_STATUS_CHANGED;
   - ERROR.
2. Ghi đúng field/order/format đã khóa để Perl parse được.
3. Ticket event phải có TicketID nếu log contract yêu cầu.
4. Không ghi password/token/secret.
5. Error log có correlation/context đủ debug nhưng không leak secret.
6. Không tự đổi format giữa Sprint vì Perl của Lộc phụ thuộc format này.


<!-- FILE: 07_ERROR_RESPONSE_LOGGING.md -->

# 07 – Error, Response & Logging Rules

## HTTP status baseline

| Case | Default |
|---|---:|
| GET thành công | 200 |
| POST tạo ticket thành công | 201 |
| PATCH thành công | 200 |
| Input sai | 400 |
| Login sai | 401 |
| Không đủ quyền | 403 nếu contract có phân quyền |
| Không tìm thấy | 404 |
| Server/DB lỗi ngoài dự kiến | 500 |

Contract repository có quyền override.

## Response consistency

AI phải tìm format chung hiện có trước.

Ví dụ nếu repo dùng:

```json
{
  "message": "Created",
  "data": {}
}
```

thì mọi endpoint mới phải theo pattern đó.

Không tự đổi format giữa Sprint.

## Validation checklist

### Path param
- int/id hợp lệ;
- > 0 nếu project quy định.

### JSON body
- required;
- type;
- empty string;
- status enum;
- allowed update field.

### Reference
- user tồn tại;
- device tồn tại;
- technician tồn tại.

## Exception safety

Không trả client:
- Python traceback;
- raw MySQL exception;
- SQL statement chứa dữ liệu nhạy cảm;
- secret;
- password hash.

## Logging contract

Perl của Lộc đọc log nên Backend phải:
- tuân thủ `/docs/log-format.md`;
- không đổi delimiter/key tùy ý;
- có TicketID ở event ticket nếu format yêu cầu;
- log level rõ ràng.

## Event baseline

```text
LOGIN_SUCCESS
LOGIN_FAILED
TICKET_CREATED
TICKET_ASSIGNED
TICKET_STATUS_CHANGED
TICKET_CLOSED
DEVICE_STATUS_CHANGED
ERROR
```

Chỉ dùng baseline này nếu log-format thật chưa định nghĩa tên khác.
Nếu log-format đã định nghĩa → dùng log-format thật.

## Không log
- password;
- password_hash;
- token/session secret;
- DB password.


<!-- FILE: 08_ACCEPTANCE_AND_TESTING.md -->

# 08 – Acceptance & Testing cho Backend

Quân là owner QA/Postman. Sang không sửa test để ép pass.

## Sang phải hỗ trợ test bằng cách

- API đúng contract.
- seed data của Lộc dùng được.
- lỗi trả deterministic status code.
- không random response field.
- không thay endpoint sau khi QA đã viết test nếu chưa cập nhật contract.

## Acceptance theo task

### Sprint 1
#### Backend skeleton
- start được.
- `/api/health` = 200.
- DB connector không hard-code secret.

### AUTH-01
- valid credential → 200.
- invalid credential → 401.
- không trả password/hash.

### TKT-01
- valid input → 201.
- ticket được insert.
- history CREATED được insert.
- rollback nếu history/write lỗi.

### TKT-02
- 200.
- list JSON.
- không có dữ liệu → list rỗng.

### TKT-03
- id đúng → 200.
- id không tồn tại → 404.

### TKT-04
- update allowed field → 200.
- invalid field/body → 400.
- missing id → 404.

### TKT-05
- technician hợp lệ → 200.
- assignee được lưu.
- OPEN có thể chuyển ASSIGNED theo plan.
- history có.

### TKT-06
- transition hợp lệ → 200.
- transition sai → 400.
- history old/new có theo schema.

### TKT-07
- RESOLVED → CLOSED = 200.
- trạng thái không hợp lệ → 400.
- history CLOSED có.

### DEV-01
- list/detail = 200.
- detail missing = 404.

### DEV-02
- status hợp lệ = 200.
- status invalid = 400.
- device missing = 404.

## Smoke flow cuối Sprint 2

```text
health
→ login
→ create ticket
→ list
→ detail
→ update
```

## Smoke flow cuối Sprint 3

```text
login
→ create
→ assign
→ IN_PROGRESS
→ RESOLVED
→ close
→ verify history
→ device list/detail/status
```

## Regression rule Sprint 4

Fix bug phải:
1. reproduce;
2. fix tối thiểu;
3. chạy lại flow lỗi;
4. chạy lại smoke flow liên quan;
5. không đổi contract trừ khi cả nhóm đồng ý.

## Definition of Done

Không mark DONE chỉ vì endpoint “chạy được”.

DONE =

```text
Code
+ Contract
+ Validation
+ Correct DB write
+ History/log khi cần
+ Expected HTTP status
+ Smoke pass
+ Không conflict owner khác
```


<!-- FILE: 09_GIT_WORKFLOW.md -->

# 09 – Git Workflow của Sang

## Branch model

```text
main
  ↑
develop
  ↑
feature/*
```

Không push trực tiếp `main`.

## Branch Sang

```text
feature/sang-backend-skeleton
feature/sang-auth-api
feature/sang-ticket-create
feature/sang-ticket-read
feature/sang-ticket-update
feature/sang-ticket-assign
feature/sang-ticket-status
feature/sang-ticket-close
feature/sang-device-api
fix/sang-<bug-name>
```

Mỗi branch nên nhỏ và một mục tiêu rõ.

## Ownership

Sang mặc định chỉ commit:

```text
/backend/**
```

Nếu `git diff --name-only` có file module khác:
- kiểm tra ngay;
- không commit nhầm.

## Trước PR

1. Fetch.
2. Update từ `develop`.
3. Resolve conflict trên branch Sang.
4. Run backend startup.
5. Run smoke check.
6. Review diff.
7. Đảm bảo không có secret.
8. Mở PR vào `develop`.

## Commit convention

```text
feat(auth): implement login endpoint
feat(ticket): create ticket with history
feat(ticket): add status transition
feat(device): update device status
fix(ticket): rollback when history insert fails
refactor(backend): normalize response helper
```

Sprint 4 hạn chế `refactor`.

## PR description tối thiểu

```markdown
Task: TKT-01
Sprint: S2

Changed:
- POST /api/tickets
- transaction ticket + history

Contract:
- no contract change

DB:
- no schema change

Smoke:
- create valid -> 201
- invalid body -> 400

Needs:
- Quân review API behavior
```

## Khi cần đổi contract

Không code trước.

Tạo đề xuất:

```text
CONTRACT CHANGE REQUEST
Task:
Reason:
Current:
Proposed:
Affected owners: Ân / Lộc / Phương / Quân
```

Chỉ code sau khi contract được chốt.


<!-- FILE: 10_AI_EXECUTION_PLAYBOOK.md -->

# 10 – AI Execution Playbook

File này quy định cách AI phải làm việc mỗi khi được giao code.

## Phase 0 – Không code ngay

Trước tiên trả về ngắn gọn:

```text
Task ID:
Sprint:
Scope:
Endpoint:
Dependencies:
Contracts read:
Files expected to modify:
Blockers:
```

Nếu có blocker → dừng trước khi tạo code sai.

## Phase 1 – Inspect repository

AI phải kiểm tra:
- framework;
- backend structure;
- api-contract;
- schema;
- log-format;
- current branch;
- feature đã có;
- test expectation có liên quan.

Không dựa chỉ vào skill nếu repo đã tiến xa hơn.

## Phase 2 – Plan minimal diff

Nguyên tắc:
- ít file nhất đủ rõ;
- không refactor ngoài task;
- không sửa owner khác;
- không thêm feature “tiện tay”.

## Phase 3 – Implement

Theo thuật toán `06_ALGORITHMS.md`.

## Phase 4 – Self-review

Checklist:
- endpoint đúng path/method?
- field đúng contract?
- query an toàn?
- transaction đúng?
- rollback?
- history?
- logging?
- 200/201/400/401/404/500?
- leak secret?
- import error?
- changed files có ngoài `/backend/**`?

## Phase 5 – Verify

Tối thiểu:
- app start;
- endpoint happy path;
- một lỗi chính;
- DB result nếu write.

Nếu không có môi trường DB:
- không fake “test passed”;
- báo `NOT_RUN` và lý do.

## Phase 6 – Report

AI phải trả:

```text
DONE/PARTIAL/BLOCKED
Task:
Files changed:
Endpoints:
Behavior:
Verification:
Known limitations:
Contract changes:
Next dependency:
```

## Cấm

- nói “hoàn thành” khi chưa chạy được kiểm chứng;
- invent schema;
- invent auth;
- đổi framework;
- sửa test expectation để pass;
- bỏ history chỉ để code ngắn hơn;
- bỏ rollback cho multi-write;
- push/merge main nếu người dùng không yêu cầu.


<!-- FILE: 11_TASK_PROMPTS.md -->

# 11 – Prompt mẫu để gọi AI Code

Các prompt này dùng cùng với `SKILL.md`.

---

## Sprint 1 – Backend skeleton

```text
Đọc SKILL.md của CS466 Sang Backend.
Thực hiện Sprint 1 cho Huỳnh Thanh Sang:
- detect framework hiện tại;
- dựng/hoàn thiện backend skeleton;
- GET /api/health;
- route skeleton;
- DB connector.
Chỉ sửa /backend/**.
Trước khi code, báo framework, contract/schema đã đọc, file sẽ sửa và blocker.
```

---

## AUTH-01

```text
Đọc CS466 Sang Backend skill.
Thực hiện AUTH-01 đúng Sprint 2.
Bắt buộc đọc schema USERS và API contract trước.
Không tự invent field username/email/password hoặc JWT.
Nếu schema auth chưa đủ, dừng với AUTH_SCHEMA_REQUIRED.
Chỉ sửa /backend/**.
```

---

## TKT-01

```text
Đọc CS466 Sang Backend skill.
Implement TKT-01 POST /api/tickets.
Yêu cầu:
- validate;
- status OPEN;
- transaction;
- insert TICKETS;
- insert HISTORY CREATED;
- logging đúng log-format;
- rollback khi lỗi;
- 201 khi thành công.
Không sửa schema.
```

---

## TKT-02 + TKT-03

```text
Đọc skill.
Implement ticket list/detail đúng API contract:
- GET /api/tickets
- GET /api/tickets/{id}
- list rỗng vẫn 200;
- detail missing 404;
- không expose field ngoài contract.
Chỉ sửa /backend/**.
```

---

## TKT-04

```text
Đọc skill.
Implement PATCH /api/tickets/{id}.
Chỉ update field API contract cho phép.
Không cho update status/assignee qua endpoint này nếu đã có endpoint riêng.
Missing -> 404, invalid body -> 400.
```

---

## TKT-05

```text
Đọc skill.
Implement assign technician:
PATCH /api/tickets/{id}/assign
- kiểm tra ticket;
- kiểm tra technician + role theo DB;
- OPEN -> ASSIGNED nếu hợp lệ;
- transaction;
- history;
- log;
- không sửa DB schema.
```

---

## TKT-06

```text
Đọc skill.
Implement status lifecycle:
OPEN -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED.
Reject transition sai với 400.
Update ticket + history cùng transaction.
```

---

## TKT-07

```text
Đọc skill.
Implement close ticket.
Theo plan chỉ close từ RESOLVED.
Update CLOSED + history + log trong transaction.
```

---

## DEV-01/DEV-02

```text
Đọc skill.
Implement Device API theo API/DB contract thật:
- GET /api/devices
- GET /api/devices/{id}
- PATCH /api/devices/{id}
Không invent device status enum.
```

---

## Sprint 4 fix

```text
Đọc skill.
Đây là Sprint 4 feature freeze.
Chỉ sửa bug được mô tả.
Không thêm endpoint, không đổi schema, không refactor lớn.
Reproduce -> minimal fix -> regression smoke -> report.
```


<!-- FILE: 12_SOURCE_TRACEABILITY.md -->

# 12 – Source Traceability

Bộ skill này bám theo các quyết định đã có trong tài liệu nhóm và Scrum plan.

## Phân công gốc

Huỳnh Thanh Sang:
- Backend/API Python.
- Flask/FastAPI.
- REST API.
- HTTP/JSON.
- API quản lý yêu cầu: tạo, xem, cập nhật, phân loại, đóng.
- đăng nhập.
- kết nối MySQL.
- Postman để kiểm tra API.

## Kiến trúc dự án

```text
Người dùng
→ Giao diện Web
→ HTTP/JSON
→ Backend REST API Python
→ MySQL
```

Nhánh dữ liệu:

```text
Log/Dữ liệu
→ Perl Script
→ Thống kê/CSV/Báo cáo
```

## Scrum plan

### S1
Backend skeleton + health + route skeleton + DB connector.

### S2
Login + list/detail/create/update ticket + MySQL.

### S3
Assign + status + close + history + device API + validation/logging.

### S4
Backend bugfix + response/status consistency.

## Git ownership

```text
Sang: /backend/**
Lộc: /database/**, /perl/**
Phương: /frontend/**
Quân: /tests/**, /postman/**
Ân: /docs/** + root integration
```

## Business lifecycle

```text
OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
```

Đây là lifecycle phải dùng trừ khi API contract đã được nhóm thay đổi chính thức.
