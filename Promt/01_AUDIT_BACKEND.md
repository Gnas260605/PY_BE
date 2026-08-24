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
