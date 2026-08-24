# BACKEND ALGORITHMS — FINAL

## A00 — Health

1. nhận request;
2. không mutate DB;
3. trả:
```json
{"status":"ok"}
```
4. HTTP 200.

---

## A01 — Login

1. parse username/password;
2. validate;
3. SELECT USERS by username;
4. missing → 401;
5. status != ACTIVE → 401;
6. bcrypt verify password vs password_hash;
7. fail → 401;
8. success → return user info + role/auth state theo contract;
9. không trả password_hash;
10. log LOGIN_SUCCESS/LOGIN_FAILED theo log contract.

---

## A02 — List Users

1. authorize ADMIN;
2. parse role/status/keyword;
3. parameterized SELECT;
4. bỏ password_hash khỏi result;
5. empty → [];
6. return 200.

---

## A03 — Create User

1. authorize ADMIN;
2. validate username/password/ho_ten/vai_tro;
3. validate role enum;
4. check duplicate username/email;
5. duplicate → 409;
6. bcrypt hash password;
7. INSERT USERS;
8. return 201 without hash.

---

## A04 — User Detail

1. authorize ADMIN;
2. validate id;
3. SELECT USERS;
4. missing → 404;
5. remove password_hash;
6. return 200.

---

## A05 — Update User

1. authorize ADMIN;
2. validate id/body;
3. load user;
4. missing → 404;
5. only allowed fields;
6. duplicate email/username if applicable → 409;
7. UPDATE;
8. return 200.

---

## A06 — User Status

1. authorize ADMIN;
2. validate id;
3. validate ACTIVE/INACTIVE;
4. load user;
5. missing → 404;
6. UPDATE trang_thai;
7. log status event if required;
8. return 200.

---

## A07 — List Devices

1. authorize per contract;
2. parse filter status/type/keyword;
3. parameterized SELECT;
4. empty → [];
5. return 200.

---

## A08 — Create Device

1. authorize ADMIN;
2. validate required fields;
3. validate status enum;
4. check duplicate ma_thiet_bi;
5. duplicate → 409;
6. INSERT DEVICES;
7. log if required;
8. return 201.

---

## A09 — Device Detail

1. authorize;
2. validate id;
3. SELECT;
4. missing → 404;
5. return 200.

---

## A10 — Update Device

1. authorize;
2. validate allowed fields;
3. validate status enum;
4. load device;
5. missing → 404;
6. UPDATE parameterized;
7. log;
8. return 200.

---

## A11 — Create Ticket

1. authorize USER/ADMIN;
2. validate body;
3. resolve creator from auth context;
4. validate device if supplied;
5. validate category/priority;
6. status = OPEN;
7. BEGIN;
8. INSERT TICKETS;
9. INSERT TICKET_HISTORY:
```text
CREATED
null → OPEN
```
10. COMMIT;
11. exception → ROLLBACK;
12. return 201.

---

## A12 — List Tickets

1. authorize;
2. parse filters;
3. enforce role visibility:
   - USER → own tickets;
   - TECHNICIAN → assigned scope;
   - ADMIN → all;
4. parameterized SELECT/JOIN;
5. empty → [];
6. return 200.

---

## A13 — Ticket Detail

1. validate id;
2. load ticket;
3. missing → 404;
4. verify role/ownership;
5. forbidden → 403;
6. load related user/device/technician if contract requests;
7. return 200.

---

## A14 — Update / Classify Ticket

1. load ticket;
2. 404 if missing;
3. authorization;
4. validate allowed fields;
5. forbid generic status/assignee mutation;
6. determine action:
   - category/priority changed → CLASSIFIED;
   - content changed → UPDATED;
7. BEGIN;
8. UPDATE TICKETS;
9. INSERT history;
10. COMMIT;
11. rollback on error;
12. return 200.

---

## A15 — Assign Technician

1. authorize ADMIN;
2. load ticket;
3. missing → 404;
4. reject CLOSED;
5. load technician user;
6. missing → 404;
7. vai_tro != TECHNICIAN → 400;
8. trang_thai != ACTIVE → 400;
9. BEGIN;
10. set technician_id;
11. if current OPEN → ASSIGNED;
12. INSERT history ASSIGNED;
13. COMMIT;
14. log;
15. return 200.

---

## A16 — Update Status

Allowed transitions:
```text
OPEN        → ASSIGNED
ASSIGNED    → IN_PROGRESS
IN_PROGRESS → RESOLVED
RESOLVED    → CLOSED
CLOSED      → none
```

1. authorize TECHNICIAN/ADMIN;
2. load ticket;
3. missing → 404;
4. verify technician scope if required;
5. validate target status;
6. invalid transition → 400;
7. BEGIN;
8. UPDATE TICKETS.trang_thai;
9. target RESOLVED → resolved_at = now;
10. target CLOSED → closed_at = now;
11. INSERT STATUS_CHANGED history;
12. COMMIT;
13. log;
14. return 200.

---

## A17 — Close Ticket

1. authorize TECHNICIAN/ADMIN;
2. load;
3. missing → 404;
4. if CLOSED → do not duplicate history;
5. current != RESOLVED → 400;
6. BEGIN;
7. update CLOSED + closed_at;
8. INSERT CLOSED history;
9. COMMIT;
10. log;
11. return 200.

---

## A18 — Read Ticket History

1. load ticket;
2. missing → 404;
3. verify access;
4. SELECT TICKET_HISTORY by ticket_id;
5. order by thoi_gian ASC, id ASC;
6. return 200 array.

---

## A19 — Transaction Wrapper

Pseudo:
```text
BEGIN
try:
    operation
    related history
    COMMIT
except:
    ROLLBACK
    raise safe application error
```

---

## A20 — Error Mapping

```text
Validation/input      → 400
Authentication fail   → 401
Permission denied     → 403
Missing entity        → 404
Duplicate             → 409
Unexpected internal   → 500
```

Never return raw DB exception.

---

## A21 — Logging

Read `docs/log-format.md`.

Never log:
```text
password
password_hash
secret
token
```

Useful events:
```text
LOGIN_SUCCESS
LOGIN_FAILED
USER_CREATED
USER_STATUS_CHANGED
DEVICE_CREATED
DEVICE_UPDATED
TICKET_CREATED
TICKET_UPDATED
TICKET_ASSIGNED
TICKET_STATUS_CHANGED
TICKET_CLOSED
ERROR
```

If docs/log-format.md defines different event names, follow docs.
