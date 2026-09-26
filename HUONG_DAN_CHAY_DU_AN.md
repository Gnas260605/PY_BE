# Huong Dan Chay Du An CS466 Helpdesk

Repository: `https://github.com/Gnas260605/PY_BE.git`

## 1. Tao File Moi Truong

```powershell
Copy-Item .env.example .env
Copy-Item .env.example backend/.env
```

Cap nhat cac gia tri bat buoc:

- `MYSQL_PASSWORD`
- `JWT_SECRET_KEY`
- cac thong tin MySQL neu may local khong dung `127.0.0.1:3306/root`

Khong commit `.env` hoac secret that.

## 2. Khoi Tao Database

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cs466_helpdesk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p cs466_helpdesk < database/schema.sql
mysql -u root -p cs466_helpdesk < database/seed.sql
```

Tai khoan demo, mat khau chung `CS466@123`:

- `admin` - ADMIN
- `tech01` - TECHNICIAN
- `user01` - USER

## 3. Chay Backend FastAPI

```powershell
Set-Location backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Kiem tra:

- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/docs`

## 4. Chay Frontend NiceGUI

Mo terminal moi:

```powershell
Set-Location frontend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:API_BASE_URL = "http://127.0.0.1:8000/api"
python app.py
```

Truy cap: `http://127.0.0.1:8500`

## 5. Chay Docker Compose

```powershell
docker compose up --build
```

Compose file dung MySQL healthcheck de API doi database san sang. Port `3306` chi nen expose cho moi truong development.

## 6. Chay Perl Log Analytics

```powershell
perl perl/bin/parse_logs.pl --input perl/samples/backend_sample.log --output perl/output/logs.csv
perl perl/bin/analyze_logs.pl --input perl/samples/backend_sample.log --config perl/config/perl.json
perl perl/bin/generate_report.pl --input perl/samples/backend_sample.log --output perl/reports --config perl/config/perl.json
```

## 7. Chay Test

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

## 8. Troubleshooting

- `Cannot find module fastapi`: chua cai dependency hoac chua kich hoat `.venv`.
- `JWT_SECRET_KEY is required`: chua tao/cap nhat `.env`.
- `Can't connect to MySQL`: MySQL chua chay, sai host/port/password, hoac database chua tao.
- `REFUSING_TO_RESET_NON_TEST_DATABASE`: test runner dang tro vao DB khong ket thuc bang `_test`.
- `perl/prove not recognized`: chua cai Perl hoac PATH chua co Perl.
