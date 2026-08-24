# Log Format - CS466 Helpdesk Backend

Status: CURRENT BACKEND FORMAT

## Python logging format

Backend dang dung `logging.basicConfig(...)` voi format:

```text
%(asctime)s %(levelname)s %(name)s %(message)s
```

Vi du:

```text
2026-08-24 10:20:30,123 INFO app.auth.service LOGIN_SUCCESS user_id=1 username=admin role=ADMIN
```

## Log level

- Default tu env: `LOG_LEVEL`
- Gia tri thuong dung: `INFO`

## Event naming currently emitted by backend

- `LOGIN_SUCCESS`
- `LOGIN_FAILED`
- `USER_CREATED`
- `USER_UPDATED`
- `USER_STATUS_CHANGED`
- `DEVICE_CREATED`
- `DEVICE_UPDATED`
- `TICKET_CREATED`
- `TICKET_UPDATED`
- `TICKET_CLASSIFIED`
- `TICKET_ASSIGNED`
- `TICKET_STATUS_CHANGED`
- `TICKET_CLOSED`

## Security rules

- Khong log JWT secret
- Khong log password hoac password hash
- Khong expose raw SQL error trong HTTP response
- Authorization header phai duoc redact trong test evidence

## Perl integration note

Perl side can parse current backend logs theo dinh dang text 4 cot co message free-form o cuoi dong. Neu can log parser stricter, doi ben Perl nen theo format nay thay vi bootstrap placeholder cu.
