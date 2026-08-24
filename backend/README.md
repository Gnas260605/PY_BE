# Backend

Backend duoc bootstrap voi FastAPI theo `Promt/00_MASTER_PROMPT.md` vi workspace ban dau chua co framework duoc khoa san.

## Scope hien tai

- App khoi dong duoc.
- `GET /api/health` san sang cho smoke test.
- Router skeleton da dang ky cho auth, tickets, devices.
- Chua implement Sprint 2/3 business logic truoc khi API contract va DB contract duoc khoa.

## Run local

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload
```

