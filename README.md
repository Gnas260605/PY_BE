# CS466 Nhom 1

Repository bootstrap cho he thong quan ly bao tri va yeu cau dich vu CNTT.

## Cau truc

- `backend/`: Backend Python REST API cua Sang.
- `database/`: DB contract, schema, seed cua Loc.
- `perl/`: Script va bao cao Perl cua Loc.
- `frontend/`: Frontend cua Phuong.
- `tests/`: Test va ket qua smoke/integration cua Quan.
- `postman/`: Collection Postman cua Quan.
- `docs/`: Tai lieu contract va kien truc cua An.

## Sprint 1 scope

- Khoa cau truc repo.
- Chon framework backend.
- Tao `GET /api/health`.
- Tao router skeleton cho auth, tickets, devices.
- Tao draft API/DB docs de ca nhom chot contract truoc Sprint 2.

## Backend quick start

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/health | Select-Object -ExpandProperty Content
```

