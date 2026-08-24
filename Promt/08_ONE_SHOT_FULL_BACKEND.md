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
