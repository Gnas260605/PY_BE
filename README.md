# CS466 Helpdesk Project

CS466 Helpdesk is a student helpdesk system for IT service requests, device maintenance, ticket handling, role-based workflows, reporting, and log analytics.

## Architecture

```text
NiceGUI Frontend -> HTTP / WebSocket -> FastAPI Backend -> MySQL
FastAPI Backend -> Structured Logs -> Perl Log Analytics -> CSV / Reports
```

## Tech Stack

- Backend: Python 3.12, FastAPI, MySQL connector, JWT, bcrypt
- Frontend: Python NiceGUI
- Database: MySQL 8.0+
- Reports: Python CSV/Excel/PDF for business data, Perl CSV/security summaries for log analytics
- Tests: pytest for Python, `Test::More`/`prove` for Perl

## Roles

- `ADMIN`: user/device management, dispatch tickets, reports, all tickets
- `TECHNICIAN`: assigned tickets, status updates, comments, device lookup
- `USER`: create ticket, own tickets, comments, attachments, settings

Backend enforces RBAC and IDOR protection. Frontend role guards are for UX only.

## Required Environment

Create `.env` from `.env.example` and change local secrets:

```powershell
Copy-Item .env.example .env
Copy-Item .env.example backend/.env
```

Required:

- `APP_NAME`, `APP_ENV`, `APP_HOST`, `APP_PORT`
- `LOG_LEVEL`, `LOG_TO_FILE`, `LOG_FILE`
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`

Optional:

- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`

Never commit real `.env` files or production logs.

## Database

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cs466_helpdesk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p cs466_helpdesk < database/schema.sql
mysql -u root -p cs466_helpdesk < database/seed.sql
```

## Run Backend

```powershell
Set-Location backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Smoke endpoints:

- Health: `http://127.0.0.1:8000/api/health`
- Swagger: `http://127.0.0.1:8000/docs`

## Run Frontend

```powershell
Set-Location frontend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:API_BASE_URL = "http://127.0.0.1:8000/api"
python app.py
```

Default frontend URL: `http://127.0.0.1:8500`

## Run Docker

```powershell
docker compose up --build
```

`docker-compose.yml` includes a MySQL healthcheck and waits for MySQL before starting the API. The compose file exposes MySQL `3306` for development convenience; do not expose it publicly for production.

## Run Perl Analytics

```powershell
perl perl/bin/parse_logs.pl --input perl/samples/backend_sample.log --output perl/output/logs.csv
perl perl/bin/analyze_logs.pl --input perl/samples/backend_sample.log --config perl/config/perl.json
perl perl/bin/generate_report.pl --input perl/samples/backend_sample.log --output perl/reports --config perl/config/perl.json
```

## Run Tests

Python:

```powershell
python -m pip install -r backend/requirements-dev.txt
python -m compileall backend frontend
pytest -v
```

Perl:

```powershell
perl -c perl/bin/parse_logs.pl
perl -c perl/bin/analyze_logs.pl
perl -c perl/bin/generate_report.pl
prove -v -Iperl/lib perl/tests
```

## Demo Accounts

All seed demo accounts use password `CS466@123`.

- `admin`: ADMIN
- `tech01`: TECHNICIAN
- `user01`: USER

## Security Notes

- JWT secret is read from environment.
- Passwords are hashed with bcrypt.
- Backend responses must not expose `password_hash`, raw SQL errors, tracebacks, JWT secrets, or Authorization tokens.
- WebSocket currently authenticates with a query-string token; do not log WebSocket URLs.
- Attachments use generated filenames and enforce ticket visibility on upload/download.

## Key Documentation

- API contract: `docs/api-contract.md`
- Architecture: `docs/architecture.md`
- DB contract: `docs/db-contract.md`
- Log format: `docs/log-format.md`
- Frontend handoff: `frontend/FRONTEND_HANDOFF.md`
- Perl analytics: `perl/README.md`
