# AI EXECUTION PLAYBOOK — FINAL

## 1. Trước mỗi task

AI phải:

1. đọc `SKILL.md`;
2. đọc `database/schema.sql`;
3. đọc `docs/api-contract.md`;
4. đọc `docs/log-format.md` nếu task liên quan log;
5. inspect code hiện tại;
6. liệt kê file sẽ sửa;
7. chỉ sửa `/backend/**`.

Không được dựa vào memory cũ nếu repo đã thay đổi.

---

## 2. Self-review bắt buộc

### Framework
- [ ] FastAPI
- [ ] Uvicorn
- [ ] không Flask

### DB
- [ ] đúng field schema.sql
- [ ] parameterized query
- [ ] không ALTER TABLE
- [ ] không invent field

### Auth
- [ ] bcrypt
- [ ] không plaintext
- [ ] inactive bị chặn
- [ ] không trả password_hash

### RBAC
- [ ] USER đúng phạm vi
- [ ] TECHNICIAN đúng phạm vi
- [ ] ADMIN đúng phạm vi
- [ ] 401/403 đúng

### API
- [ ] đủ endpoint task
- [ ] đúng method/path
- [ ] đúng request/response
- [ ] list empty = 200 []

### Ticket
- [ ] đúng lifecycle
- [ ] generic PATCH không đổi assignee/status
- [ ] assign chỉ TECHNICIAN ACTIVE
- [ ] close chỉ từ RESOLVED

### History
- [ ] CREATED
- [ ] UPDATED
- [ ] CLASSIFIED
- [ ] ASSIGNED
- [ ] STATUS_CHANGED
- [ ] CLOSED

### Transaction
- [ ] mutation + history cùng transaction
- [ ] rollback khi lỗi

### Security
- [ ] no traceback
- [ ] no raw SQL
- [ ] no secret
- [ ] no password/hash log

### Logging
- [ ] đúng log-format
- [ ] Perl parse được

---

## 3. Verify strategy

Ưu tiên:

```text
import check
→ backend startup
→ endpoint smoke
→ DB verification
→ negative case
```

Không nói “pass” nếu chưa chạy.

---

## 4. Contract drift

Nếu thấy:

```text
API contract != schema
API contract != backend
schema != merged code
```

thì:

```text
CONTRACT_DRIFT
```

và liệt kê:
- expected;
- actual;
- affected owner;
- task bị block hay không.

Không tự sửa `/docs` hoặc `/database`.

---

## 5. Final completeness check

Backend hoàn thành khi đủ:

```text
1 Health
1 Login
5 User Management
4 Device Management
8 Ticket/History
= 19 endpoints
```

---

## 6. Final smoke flow

```text
health
→ login ADMIN
→ create USER
→ create TECHNICIAN
→ list/detail/update user
→ deactivate/activate user
→ create device
→ list/detail/update device
→ login USER
→ create ticket
→ list/detail/update
→ ADMIN assign TECHNICIAN
→ TECHNICIAN IN_PROGRESS
→ TECHNICIAN RESOLVED
→ close
→ history
→ verify MySQL
→ verify logs
```
