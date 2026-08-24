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
