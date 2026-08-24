# API Contract - CS466 Helpdesk

Status: LOCKED FOR CURRENT BACKEND

Base path: `/api`

Content type:

- Request: `application/json` khi endpoint co body
- Response: `application/json`

Auth:

- Scheme: `Authorization: Bearer <access_token>`
- JWT algorithm: `HS256`
- Token claims toi thieu: `sub`, `username`, `role`, `exp`
- Backend luon reload user hien tai tu MySQL truoc khi authorize request protected

## Common error envelope

Tat ca loi ung dung tra ve:

```json
{
  "detail": "ERROR_CODE",
  "path": "/api/example"
}
```

Validation error co them `errors`:

```json
{
  "detail": "INVALID_INPUT",
  "path": "/api/example",
  "errors": []
}
```

## Status code baseline

- `200` success
- `201` created
- `400` invalid input
- `401` missing token, invalid token, expired token, inactive account, invalid credentials
- `403` authenticated but forbidden by role
- `404` missing resource
- `409` duplicate/conflict business rule
- `500` internal server error

## Endpoint matrix (19 APIs)

### Public

#### `GET /health`

Response `200`:

```json
{
  "status": "ok"
}
```

#### `POST /login`

Request:

```json
{
  "username": "admin",
  "password": "CS466@123"
}
```

Response `200`:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "ho_ten": "System Administrator",
    "email": "admin@cs466.local",
    "vai_tro": "ADMIN",
    "trang_thai": "ACTIVE"
  }
}
```

Notes:

- Khong tra field `token`
- Khong tra `password_hash`
- Login chi thanh cong khi user ton tai, `trang_thai = ACTIVE`, va bcrypt verify pass

### User management (ADMIN only)

#### `GET /users`

Query params:

- `role`: `USER | TECHNICIAN | ADMIN`
- `status`: `ACTIVE | INACTIVE`
- `keyword`: free text

Response `200`: `UserResponse[]`

#### `POST /users`

Request:

```json
{
  "username": "user02",
  "password": "CS466@123",
  "ho_ten": "Nguyen Van B",
  "email": "user02@cs466.local",
  "vai_tro": "USER"
}
```

Response `201`: `UserResponse`

#### `GET /users/{id}`

Response `200`: `UserResponse`

#### `PATCH /users/{id}`

Request body cho phep:

```json
{
  "ho_ten": "Nguyen Van B Updated",
  "email": "user02@cs466.local",
  "vai_tro": "USER"
}
```

Response `200`: `UserResponse`

#### `PATCH /users/{id}/status`

Request:

```json
{
  "status": "INACTIVE"
}
```

Response `200`: `UserResponse`

### Device management

#### `GET /devices`

Roles: `ADMIN`, `TECHNICIAN`

Query params:

- `status`: `ACTIVE | MAINTENANCE | BROKEN | INACTIVE`
- `type`: free text
- `keyword`: free text

Response `200`: `DeviceResponse[]`

#### `POST /devices`

Roles: `ADMIN`

Request:

```json
{
  "ma_thiet_bi": "PC-002",
  "ten_thiet_bi": "May tinh phong ke toan 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Tang 2",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Vostro i5 16GB"
}
```

Response `201`: `DeviceResponse`

#### `GET /devices/{id}`

Roles: `ADMIN`, `TECHNICIAN`

Response `200`: `DeviceResponse`

#### `PATCH /devices/{id}`

Roles: `ADMIN`, `TECHNICIAN`

Request body cho phep bat ky tap con nao cua:

```json
{
  "ma_thiet_bi": "PC-002",
  "ten_thiet_bi": "May tinh phong ke toan 02",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Tang 2",
  "trang_thai": "MAINTENANCE",
  "mo_ta": "Dang gui bao hanh"
}
```

Response `200`: `DeviceResponse`

### Ticket management

#### `GET /tickets`

Roles: `USER`, `TECHNICIAN`, `ADMIN`

Query params:

- `status`: `OPEN | ASSIGNED | IN_PROGRESS | RESOLVED | CLOSED`
- `priority`: `LOW | MEDIUM | HIGH | URGENT`
- `category`: `INCIDENT | SERVICE_REQUEST | MAINTENANCE`
- `technician_id`: integer
- `user_id`: integer
- `keyword`: free text

Response `200`: `TicketSummaryResponse[]`

#### `POST /tickets`

Roles: `USER`, `ADMIN`

Request:

```json
{
  "title": "Printer khong in duoc",
  "description": "May in phong ke toan bi ket lenh",
  "device_id": 1,
  "category": "INCIDENT",
  "priority": "HIGH"
}
```

Response `201`: `TicketSummaryResponse`

#### `GET /tickets/{id}`

Roles: `USER`, `TECHNICIAN`, `ADMIN`

Response `200`: `TicketDetailResponse`

Includes:

- summary fields
- `creator`
- `device`
- `technician`

#### `PATCH /tickets/{id}`

Roles: `USER`, `ADMIN`

Request body cho phep:

```json
{
  "title": "Printer khong in duoc - updated",
  "description": "Cap nhat mo ta",
  "category": "INCIDENT",
  "priority": "MEDIUM"
}
```

Response `200`: `TicketSummaryResponse`

#### `PATCH /tickets/{id}/assign`

Roles: `ADMIN`

Request:

```json
{
  "technician_id": 2
}
```

Response `200`: `TicketSummaryResponse`

#### `PATCH /tickets/{id}/status`

Roles: `TECHNICIAN`, `ADMIN`

Request:

```json
{
  "status": "IN_PROGRESS"
}
```

Response `200`: `TicketSummaryResponse`

#### `PATCH /tickets/{id}/close`

Roles: `TECHNICIAN`, `ADMIN`

Request:

```json
{
  "note": "Da thay the linh kien va test OK"
}
```

Response `200`: `TicketSummaryResponse`

#### `GET /tickets/{id}/history`

Roles: `USER`, `TECHNICIAN`, `ADMIN`

Response `200`:

```json
[
  {
    "id": 1,
    "action": "STATUS_CHANGED",
    "old_status": "OPEN",
    "new_status": "ASSIGNED",
    "detail": "Assigned to technician 2",
    "performed_by": 1,
    "performed_at": "2026-08-24T10:00:00"
  }
]
```

## Response models

### `UserResponse`

```json
{
  "id": 1,
  "username": "admin",
  "ho_ten": "System Administrator",
  "email": "admin@cs466.local",
  "vai_tro": "ADMIN",
  "trang_thai": "ACTIVE",
  "created_at": "2026-08-24T10:00:00",
  "updated_at": "2026-08-24T10:00:00"
}
```

### `DeviceResponse`

```json
{
  "id": 1,
  "ma_thiet_bi": "PC-001",
  "ten_thiet_bi": "May tinh phong ke toan 01",
  "loai_thiet_bi": "COMPUTER",
  "vi_tri": "Tang 2",
  "trang_thai": "ACTIVE",
  "mo_ta": "Dell Optiplex",
  "created_at": "2026-08-24T10:00:00",
  "updated_at": "2026-08-24T10:00:00"
}
```

### `TicketSummaryResponse`

```json
{
  "id": 1,
  "title": "Printer khong in duoc",
  "description": "May in phong ke toan bi ket lenh",
  "category": "INCIDENT",
  "priority": "HIGH",
  "status": "OPEN",
  "user_id": 3,
  "device_id": 1,
  "technician_id": null,
  "created_at": "2026-08-24T10:00:00",
  "updated_at": "2026-08-24T10:00:00",
  "resolved_at": null,
  "closed_at": null
}
```
