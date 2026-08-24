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
