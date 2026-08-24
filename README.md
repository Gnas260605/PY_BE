# CS466 Helpdesk Project

Monorepo cho nhom CS466 gom backend FastAPI, database MySQL, frontend web, Postman collection, test evidence, va tai lieu tich hop.

## Current backend status

- Backend contract da khoa va da pass 19/19 API regression.
- Auth dung JWT Bearer (`HS256`) voi secret doc tu environment.
- Khong dung hard-coded JWT secret.
- Login response contract:

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

## Repo layout

- `backend/` FastAPI app va modules auth, users, devices, tickets.
- `database/` SQL schema va seed data. Khong sua schema neu task khong thuoc owner DB.
- `frontend/` web client va tai lieu tich hop API.
- `postman/` collection va huong dan test theo role.
- `tests/` script regression va markdown evidence.
- `docs/` API contract, log format, va tai lieu bo tro.

## Environment convention

Dung `root/.env` lam nguon cau hinh chinh cho Docker Compose.

Backend cung ho tro doc `backend/.env` khi chay local bang `uvicorn`, nhung hai file nay phai dong bo gia tri.

Bat buoc cung cap:

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM=HS256`
- `JWT_EXPIRE_MINUTES=480`

Khoi tao nhanh:

```powershell
Copy-Item .env.example .env
Copy-Item .env.example backend/.env
```

Sau do cap nhat gia tri local trong 2 file `.env`:

- `MYSQL_PASSWORD`
- `JWT_SECRET_KEY`
- cac bien MySQL khac neu may local khong dung `127.0.0.1:3306/root`

Khong commit secret that vao repo.

## Database setup

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cs466_helpdesk;"
mysql -u root -p cs466_helpdesk < database/schema.sql
mysql -u root -p cs466_helpdesk < database/seed.sql
```

## Run backend locally

```powershell
Set-Location backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Smoke endpoints:

- Health: `http://127.0.0.1:8000/api/health`
- Swagger: `http://127.0.0.1:8000/docs`

## Demo accounts from seed data

- `admin / CS466@123`
- `tech01 / CS466@123`
- `user01 / CS466@123`

## Team handoff references

- API contract: [docs/api-contract.md](/D:/Individua_Project/Python_Project/docs/api-contract.md)
- Log format: [docs/log-format.md](/D:/Individua_Project/Python_Project/docs/log-format.md)
- Backend guide: [backend/README.md](/D:/Individua_Project/Python_Project/backend/README.md)
- Frontend guide: [frontend/API_INTEGRATION_GUIDE.md](/D:/Individua_Project/Python_Project/frontend/API_INTEGRATION_GUIDE.md)
- Postman guide: [postman/POSTMAN_TEST_GUIDE.md](/D:/Individua_Project/Python_Project/postman/POSTMAN_TEST_GUIDE.md)
