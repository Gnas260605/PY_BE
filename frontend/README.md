# Frontend Python - CS466 Helpdesk

Frontend đã được tái cấu trúc theo `FRONTEND_PYTHON_DEVELOPMENT_GUIDE.md`, dùng NiceGUI + httpx và bám `docs/api-contract.md`.
NiceGUI được pin `2.24.2` để tương thích với backend đang pin `fastapi==0.116.1`.

## Cấu trúc chính

- `app.py`: entrypoint NiceGUI.
- `core/`: config, auth context, HTTP client, enum contract, TTL cache.
- `common/`: style, formatter, validator, component UI dùng chung.
- `services/`: service layer cho Auth, Users, Devices, Tickets.
- `views/`: màn hình chia theo role `auth`, `admin`, `technician`, `user`.
- `index.html`, `pages/`, `js/`, `assets/css/`: UI HTML/JS legacy, được giữ lại để không mất phần đang có.

## Chạy frontend Python

```powershell
cd D:\Individua_Project\Python_Project\frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Mặc định app chạy tại `http://127.0.0.1:8500` và gọi backend `http://127.0.0.1:8000/api`.

Có thể đổi cấu hình bằng biến môi trường:

- `API_BASE_URL`
- `FRONTEND_HOST`
- `FRONTEND_PORT`
- `FRONTEND_CACHE_TTL_SECONDS`
- `FRONTEND_STORAGE_SECRET`

