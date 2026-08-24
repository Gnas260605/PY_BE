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
