# API Contract

Status: DRAFT

Scope bootstrap Sprint 1:

- `GET /api/health`
- `POST /api/login`
- `GET /api/tickets`
- `GET /api/tickets/{id}`
- `POST /api/tickets`
- `PATCH /api/tickets/{id}`
- `PATCH /api/tickets/{id}/assign`
- `PATCH /api/tickets/{id}/status`
- `PATCH /api/tickets/{id}/close`
- `GET /api/devices`
- `GET /api/devices/{id}`
- `PATCH /api/devices/{id}`

## Locked now

- Base path: `/api`
- Content type: HTTP/JSON
- Health response:

```json
{
  "status": "ok"
}
```

## Not locked yet

- Auth request/response fields
- Ticket request/response body fields
- Device update fields
- Error payload standard beyond current bootstrap placeholder
- Ticket history read contract

## Bootstrap runtime behavior

- `GET /api/health` returns `200 OK`
- `POST /api/login` returns `501` with `BLOCKED: AUTH_SCHEMA_REQUIRED`
- Ticket/device skeleton endpoints return `501` with `CONTRACT_NOT_LOCKED`

