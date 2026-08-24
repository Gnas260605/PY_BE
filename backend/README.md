# Backend - CS466 Helpdesk

Backend hien tai da qua giai doan bootstrap. Day la service FastAPI cung cap 19 REST API cho health, auth, user management, device management, ticket management, ticket history va RBAC.

## Runtime

- Framework: FastAPI
- Server: Uvicorn
- Database: MySQL 8
- Password hashing: bcrypt
- Auth: JWT Bearer
- JWT algorithm: `HS256`
- JWT expiry: `JWT_EXPIRE_MINUTES` (mac dinh 480)
- JWT secret: bat buoc doc tu `JWT_SECRET_KEY`

## Required environment

Backend doc env tu:

1. `backend/.env`
2. `../.env`

Can co it nhat cac bien:

```env
APP_NAME=cs466-service-desk
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
LOG_LEVEL=INFO
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=cs466_helpdesk
MYSQL_USER=root
MYSQL_PASSWORD=change-me
JWT_SECRET_KEY=change-me-before-running
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480
```

Neu thieu `JWT_SECRET_KEY`, app se fail ngay luc load config thay vi tu sinh secret.

## Run local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Public endpoints

- `GET /api/health`
- `POST /api/login`

## Protected modules

- `GET /api/users`
- `POST /api/users`
- `GET /api/users/{id}`
- `PATCH /api/users/{id}`
- `PATCH /api/users/{id}/status`
- `GET /api/devices`
- `POST /api/devices`
- `GET /api/devices/{id}`
- `PATCH /api/devices/{id}`
- `GET /api/tickets`
- `POST /api/tickets`
- `GET /api/tickets/{id}`
- `PATCH /api/tickets/{id}`
- `PATCH /api/tickets/{id}/assign`
- `PATCH /api/tickets/{id}/status`
- `PATCH /api/tickets/{id}/close`
- `GET /api/tickets/{id}/history`

## Ticket lifecycle

Trang thai ticket hien tai:

- `OPEN`
- `ASSIGNED`
- `IN_PROGRESS`
- `RESOLVED`
- `CLOSED`

Luong xu ly thong dung:

`OPEN -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED`

## Error behavior

- `400` invalid input
- `401` missing token, invalid token, expired token, invalid credentials, inactive account
- `403` authenticated but khong du role
- `404` resource khong ton tai
- `409` duplicate business constraint
- `500` sanitized internal/server or database error

Khong tra traceback, raw SQL error, password, password hash, hoac JWT secret.
