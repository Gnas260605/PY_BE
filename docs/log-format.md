# Log Format - CS466 Helpdesk Backend

Status: CURRENT BACKEND FORMAT

## Python logging format

Backend dang dung `configure_logging(...)` voi format:

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
- `PASSWORD_CHANGED`
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
- `TICKET_BATCH_ASSIGNED`
- `TICKET_BATCH_STATUS_CHANGED`
- `TICKET_COMMENT_CREATED`
- `WEBSOCKET_CONNECTED`
- `WEBSOCKET_DISCONNECTED`
- `WEBSOCKET_SEND_FAILED`
- `WEBSOCKET_BROADCAST_FAILED`
- `TELEGRAM_CONFIG_MISSING`
- `TELEGRAM_NOTIFICATION_SENT`
- `TELEGRAM_NOTIFICATION_FAILED`
- `SMTP_CONFIG_MISSING`
- `EMAIL_NOTIFICATION_SENT`
- `EMAIL_NOTIFICATION_FAILED`
- `UNHANDLED_DB_EXCEPTION`
- `UNHANDLED_EXCEPTION`

All backend event log messages should follow:

```text
EVENT key=value key=value
```

Messages such as `WebSocket connected for user_id=...` or `Unhandled application error on ...` should not be emitted because Perl treats non-event messages as malformed lines.

## Security rules

- Khong log JWT secret
- Khong log password hoac password hash
- Khong expose raw SQL error trong HTTP response
- Authorization header phai duoc redact trong test evidence

## Perl integration note

Perl side can parse current backend logs theo dinh dang text 4 cot co message free-form o cuoi dong. Neu can log parser stricter, doi ben Perl nen theo format nay thay vi bootstrap placeholder cu.

## Optional file logging

Console logging is enabled by default. Rotating file logging can be enabled with:

```text
LOG_TO_FILE=true
LOG_FILE=logs/backend.log
```

Default sample values are documented in `.env.example` and forwarded by `docker-compose.yml`.
