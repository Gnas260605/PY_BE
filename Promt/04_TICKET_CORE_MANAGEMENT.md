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
