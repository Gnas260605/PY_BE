# BÁO CÁO TỔNG KẾT CÁC MỤC ĐÃ HOÀN THÀNH — CS466 HELPDESK QA

> **Dự án:** CS466 Helpdesk (FastAPI + MySQL)  
> **Repository:** `https://github.com/Gnas260605/PY_BE.git`  
> **Branch:** `main`  
> **Backend Commit SHA:** `e2b610838226b2c414caf6d3c01c78af5405c08f`  
> **Ngày hoàn thành:** 2026-09-09  
> **Người thực hiện:** QA Engineer  

---

## 1. TUÂN THỦ PHẠM VI TUYỆT ĐỐI (SCOPE COMPLIANCE)

- [x] **Chỉ tạo/sửa file trong:** `tests/**` và `postman/**`.
- [x] **Giữ nguyên 100% không chỉnh sửa:** `backend/**` (0 file), `database/**` (0 file), `docs/**` (0 file).
- [x] **Trạng thái Backend:** Đóng băng (LOCKED) tại commit `e2b610838226b2c414caf6d3c01c78af5405c08f`.

---

## 2. CHI TIẾT CÁC HẠNG MỤC ĐÃ HOÀN THÀNH THEO 8 BƯỚC

### ✅ Bước 1 — Chuẩn bị môi trường & Cơ chế An toàn Database
- [x] Trích xuất và xác thực `HEAD_COMMIT_SHA = e2b610838226b2c414caf6d3c01c78af5405c08f`.
- [x] Kiểm thử cơ chế bảo vệ an toàn database: Chạy `run_role_based_tests.py` với `MYSQL_DATABASE=cs466_helpdesk` (không có hậu tố `_test`) $\to$ Đã raise chính xác `RuntimeError("REFUSING_TO_RESET_NON_TEST_DATABASE")`.
- [x] Khởi tạo container MySQL với database `cs466_helpdesk_test`, thực thi schema (`database/schema.sql`) và nạp seed data (`database/seed.sql`).
- [x] Xác thực endpoint sức khỏe hệ thống: `GET /api/health` trả về HTTP `200 OK` với `{"status": "ok"}`.

### ✅ Bước 2 — Dựng khung Pytest & Helper Modules trong `tests/`
- [x] **Tạo `tests/helpers.py`**:
  - `get_unique_suffix()`: Cung cấp timestamp + random hex phục vụ Data Isolation.
  - Các hàm sinh dữ liệu độc lập: `generate_user_data()`, `generate_device_data()`, `generate_ticket_data()`.
  - Hàm truy vấn trực tiếp cơ sở dữ liệu: `query_ticket_by_id()`, `query_ticket_history()`.
  - `BugReportCollector`: Tự động thu thập và xuất báo cáo khiếm khuyết chuẩn 15 trường.
- [x] **Tạo `tests/conftest.py`**:
  - Fixture `client`: `TestClient(app)` tái sử dụng cho toàn bộ test suite.
  - Fixture `admin_token`, `tech_token`, `user_token` & các fixture headers tương ứng.
  - Fixture `db_reset`: Kiểm tra kết nối và reset DB an toàn trước các ca test cần thiết.

### ✅ Bước 3 — Login Contract & Auth/Security Negative
- [x] **Tạo `tests/api/test_login_contract.py`**:
  - Đăng nhập 3 vai trò (`admin`, `tech01`, `user01` với mật khẩu `CS466@123`) $\to$ Trả về HTTP `200 OK`.
  - Xác thực đúng hợp đồng: `access_token`, `token_type: "bearer"`, `user: {id, username, ho_ten, email, vai_tro, trang_thai}`.
  - Assert nghiêm ngặt: **TUYỆT ĐỐI KHÔNG** chứa các trường nhạy cảm `token`, `password`, `password_hash`.
- [x] **Tạo `tests/api/test_auth_negative.py`**:
  - Token hết hạn (`exp` quá khứ) $\to$ Trả về `401 Unauthorized` (`TOKEN_EXPIRED`).
  - Token sai chữ ký (ký bằng secret lạ) $\to$ Trả về `401 Unauthorized` (`INVALID_TOKEN`).
  - Token thiếu claim `sub` $\to$ Trả về `401 Unauthorized` (`INVALID_TOKEN`).
  - Token dị dạng (chuỗi không phải JWT) $\to$ Trả về `401 Unauthorized` (`INVALID_TOKEN`).
  - Request không kèm header Authorization $\to$ Trả về `401 Unauthorized` (`MISSING_TOKEN`).
  - User gọi endpoint vượt quyền (USER gọi `/api/users`) $\to$ Trả về `403 Forbidden` (`FORBIDDEN`).
  - Assert ngăn chặn rò rỉ: Zero leak traceback, raw SQL statement, credentials, hay secret key.

### ✅ Bước 4 — RBAC, IDOR & Duplicate theo 3 Role
- [x] **Tạo `tests/api/test_rbac_idor.py`**:
  - **Role ADMIN**: Tạo tài khoản trùng username/email $\to$ `409 Conflict`; tạo thiết bị trùng mã $\to$ `409 Conflict`. Quản lý toàn diện users, devices, tickets.
  - **Role USER**: Tạo ticket (bắt buộc lấy `user_id` từ JWT token, không lấy từ body), danh sách ticket chỉ thấy vé của chính mình.
  - **Bảo vệ IDOR**: USER gọi `GET /api/tickets/{other_user_ticket_id}` hoặc xem lịch sử vé người khác $\to$ Trả về `403 Forbidden`.
  - USER bị chặn khi truy cập endpoint ADMIN/TECH: `GET /api/users` (403), `POST /api/devices` (403), `PATCH .../assign` (403).
  - **Role TECHNICIAN**: Cập nhật thiết bị chỉ được phép sửa `trang_thai` và `mo_ta` (200); nếu gửi trường cấm (`ten_thiet_bi`, `ma_thiet_bi`, `loai_thiet_bi`, `vi_tri`) $\to$ Bị chặn với `403 Forbidden`. Bị chặn khỏi quản lý users, tạo thiết bị, gán vé.

### ✅ Bước 5 — Vòng Đời Ticket & Chuyển Trạng Thái Sai Quy Trình
- [x] **Tạo `tests/integration/test_ticket_lifecycle.py` (Phần 1 - Transitions)**:
  - Chu trình đầy đủ: `OPEN` (User tạo) $\to$ `ASSIGNED` (Admin gán KTV) $\to$ `IN_PROGRESS` (KTV nhận việc) $\to$ `RESOLVED` (KTV hoàn thành) $\to$ `CLOSED` (Đóng vé).
  - Negative: Chuyển `OPEN` $\to$ `ASSIGNED` qua PATCH `/status` (thay vì `/assign`) $\to$ `400 Bad Request` (`INVALID_TRANSITION`).
  - Negative: Chuyển `RESOLVED` $\to$ `CLOSED` qua PATCH `/status` (thay vì `/close`) $\to$ `400 Bad Request` (`INVALID_TRANSITION`).
  - Negative: Chuyển lùi `RESOLVED` $\to$ `OPEN` $\to$ `400 Bad Request` (`INVALID_TRANSITION`).
  - Negative: Gọi `/close` lần thứ 2 trên ticket đã đóng (re-close) $\to$ `400 Bad Request` (`INVALID_TRANSITION`).

### ✅ Bước 6 — History Timeline & Kiểm Tra Trực Tiếp Database State
- [x] **Tạo `tests/integration/test_ticket_lifecycle.py` (Phần 2 - Audit)**:
  - Phân lập kiểm tra lịch sử theo đúng `ticket_id` của lượt test.
  - Xác minh chuỗi đúng 5 records theo đúng trình tự thời gian: `CREATED` $\to$ `ASSIGNED` $\to$ `STATUS_CHANGED` (`IN_PROGRESS`) $\to$ `STATUS_CHANGED` (`RESOLVED`) $\to$ `CLOSED`.
  - Assert hành động `CLOSED` **chỉ xuất hiện duy nhất 1 lần**, trường thời gian `performed_at` tăng dần liên tục.
  - Truy vấn trực tiếp bảng `TICKETS` bằng `connection_scope()`: `trang_thai == 'CLOSED'`, `technician_id == 2` (NOT NULL), `resolved_at IS NOT NULL`, `closed_at IS NOT NULL`.

### ✅ Bước 7 — Request Body Hardening, CORS & Error Handling
- [x] **Tạo `tests/api/test_request_hardening.py`**:
  - Gửi payload kèm các trường lạ/cấm vào `POST /api/tickets` (`user_id`, `status`, `technician_id`, `injected_field`) $\to$ Bị từ chối `400 Bad Request` (`INVALID_INPUT`).
  - Assert **không đột biến cơ sở dữ liệu (No DB Mutation)**: Xác minh không có bản ghi nào bị chèn sai lệch vào MySQL.
  - Gửi các trường cấm vào `PATCH /api/tickets/{id}` (`status`, `technician_id`, `user_id`, `closed_at`, `resolved_at`) $\to$ Bị từ chối `400 Bad Request`, assert DB giữ nguyên giá trị ban đầu.
  - Gửi extra fields vào `POST /api/login` $\to$ Bị từ chối `400 Bad Request`.
- [x] **Tạo `tests/api/test_cors.py`**:
  - `OPTIONS` preflight với 4 allowed origins (`http://127.0.0.1:3000`, `http://localhost:3000`, `http://127.0.0.1:5500`, `http://localhost:5500`) $\to$ Trả về `200 OK` kèm các headers `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`.
  - Kiểm tra origin bị cấm (`http://malicious-attacker.com`) $\to$ Không trả về allow origin header.
- [x] **Tạo `tests/api/test_error_handling.py`**:
  - Kiểm tra toàn diện ma trận mã lỗi: 400 (`INVALID_INPUT`), 401 (`AUTH_FAILED`), 403 (`FORBIDDEN`), 404 (`NOT_FOUND`), 409 (`CONFLICT`).
  - **Kiểm thử lỗi 500 an toàn (Non-destructive)**: Dùng monkeypatch mô phỏng unhandled exception có chứa thông tin nhạy cảm giả lập, xác nhận FastAPI exception handler trả về định dạng sanitized: `{"detail": "INTERNAL_SERVER_ERROR", "path": "/api/health"}` với HTTP `500`, zero leak stack trace/secret mà **hoàn toàn không làm hỏng hay bẩn database**.

### ✅ Bước 8 — Thực Thi Full Suite, Cập Nhật Postman & Báo Cáo
- [x] **Cập nhật `postman/CS466_Helpdesk_Postman_Collection.json`**:
  - Bổ sung 3 request còn thiếu: `GET /devices/{id}`, `PATCH /devices/{id}`, `PATCH /tickets/{id}`.
  - Đảm bảo bao phủ đầy đủ **19/19 APIs** của hệ thống.
  - Chuẩn hóa toàn bộ test script dùng `data.access_token` và `data.user.vai_tro`.
  - Làm sạch toàn bộ biến collection (không commit token thật hay mật khẩu).
- [x] **Tái tạo 3 file evidence báo cáo markdown**:
  - `tests/results/TEST_ROLE_ADMIN.md`: 19/19 test cases PASS (Commit SHA `e2b610838226b2c414caf6d3c01c78af5405c08f`).
  - `tests/results/TEST_ROLE_USER.md`: 9/9 test cases PASS (Commit SHA `e2b610838226b2c414caf6d3c01c78af5405c08f`).
  - `tests/results/TEST_ROLE_TECHNICIAN.md`: 11/11 test cases PASS (Commit SHA `e2b610838226b2c414caf6d3c01c78af5405c08f`).
- [x] **Chạy toàn bộ Pytest Suite (`pytest tests/api tests/integration -v`)**:
  - **Kết quả: `29/29 PASSED (100%)`**.
- [x] **Chạy Role-based Runner (`python tests/run_role_based_tests.py`)**:
  - **Kết quả: `39/39 PASSED (100%)`**.
- [x] **In bảng ma trận độc lập 19/19 API** và xuất khối **`QA_FINAL_RESULT`**.

---

## 3. BẢNG MA TRẬN ĐỘC LẬP 19/19 API (ACCESS & CONTRACT COVERAGE)

| # | Method | Endpoint | Quyền hạn hợp lệ (Role Access) | Quyền hạn bị chặn (403) | Trạng thái |
|:---:|:---:|:---|:---|:---|:---:|
| 1 | `GET` | `/api/health` | Public (Mọi role) | Không có | ✅ PASSED |
| 2 | `POST` | `/api/login` | Public (Xác thực JWT HS256) | Không có | ✅ PASSED |
| 3 | `GET` | `/api/users` | `ADMIN` | `USER`, `TECHNICIAN` | ✅ PASSED |
| 4 | `POST` | `/api/users` | `ADMIN` | `USER`, `TECHNICIAN` | ✅ PASSED |
| 5 | `GET` | `/api/users/{id}` | `ADMIN` | `USER`, `TECHNICIAN` | ✅ PASSED |
| 6 | `PATCH` | `/api/users/{id}` | `ADMIN` | `USER`, `TECHNICIAN` | ✅ PASSED |
| 7 | `PATCH` | `/api/users/{id}/status` | `ADMIN` | `USER`, `TECHNICIAN` | ✅ PASSED |
| 8 | `GET` | `/api/devices` | `ADMIN`, `TECHNICIAN` | `USER` | ✅ PASSED |
| 9 | `POST` | `/api/devices` | `ADMIN` | `USER`, `TECHNICIAN` | ✅ PASSED |
| 10 | `GET` | `/api/devices/{id}` | `ADMIN`, `TECHNICIAN` | `USER` | ✅ PASSED |
| 11 | `PATCH` | `/api/devices/{id}` | `ADMIN` (all), `TECH` (chỉ `trang_thai`, `mo_ta`) | `USER` (403), `TECH` field cấm (403) | ✅ PASSED |
| 12 | `GET` | `/api/tickets` | `ADMIN` (all), `USER` (own), `TECH` (assigned) | Không có (theo scope role) | ✅ PASSED |
| 13 | `POST` | `/api/tickets` | `ADMIN`, `USER` | `TECHNICIAN` | ✅ PASSED |
| 14 | `GET` | `/api/tickets/{id}` | `ADMIN`, `USER` (chính chủ), `TECH` (được gán) | `USER` vé người khác (403 IDOR), `TECH` vé chưa gán (403) | ✅ PASSED |
| 15 | `PATCH` | `/api/tickets/{id}` | `ADMIN`, `USER` (chính chủ & status `OPEN`) | `USER` vé người khác hoặc vé != OPEN (403), `TECH` (403) | ✅ PASSED |
| 16 | `PATCH` | `/api/tickets/{id}/assign` | `ADMIN` | `USER`, `TECHNICIAN` | ✅ PASSED |
| 17 | `PATCH` | `/api/tickets/{id}/status` | `ADMIN`, `TECHNICIAN` (được gán) | `USER` (403), `TECH` không được gán (403) | ✅ PASSED |
| 18 | `PATCH` | `/api/tickets/{id}/close` | `ADMIN`, `TECHNICIAN` (được gán) | `USER` (403), `TECH` không được gán (403) | ✅ PASSED |
| 19 | `GET` | `/api/tickets/{id}/history`| `ADMIN`, `USER` (chính chủ), `TECH` (được gán) | `USER` xem vé người khác (403 IDOR), `TECH` vé chưa gán (403) | ✅ PASSED |

---

## 4. TỔNG KẾT KẾT QUẢ KIỂM THỬ

- **Pytest Suite (`tests/api/` & `tests/integration/`):** **29 / 29 PASS (100%)**
- **Role-based Test Runner (`tests/run_role_based_tests.py`):** **39 / 39 PASS (100%)**
- **Bao phủ Endpoint API:** **19 / 19 PASS (100%)**
- **Số lượng Bug phát hiện:** **0** (Backend hoạt động hoàn toàn chính xác theo đặc tả `api-contract.md`).

---

## 5. KHỐI TỔNG KẾT CHÍNH THỨC (`QA_FINAL_RESULT`)

```
================================================================================
QA_FINAL_RESULT
================================================================================
BACKEND_COMMIT:         e2b610838226b2c414caf6d3c01c78af5405c08f
OVERALL_STATUS:         PASS
API_COVERAGE:           Passed: 19/19 (100%)
FLOW_LOGIN_CONTRACT:    PASS
FLOW_AUTH_NEGATIVE:     PASS
FLOW_RBAC_IDOR:         PASS
FLOW_TICKET_LIFECYCLE:  PASS
FLOW_HISTORY_AUDIT:     PASS
FLOW_DB_STATE_VERIFY:   PASS
FLOW_REQUEST_HARDENING: PASS
FLOW_CORS:              PASS
FLOW_ERROR_HANDLING:    PASS
TEST_DB_SAFETY:         PASS (REFUSING_TO_RESET_NON_TEST_DATABASE verified)
DATA_ISOLATION:         PASS (Dynamic suffix timestamps applied)
SECRET_SCAN:            PASS (0 tokens/credentials leaked)
BACKEND_FILES_CHANGED:  NONE (0 files modified)
================================================================================
```
