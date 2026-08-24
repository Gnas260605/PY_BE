# CS466 - Nhóm 1: Hệ Thống Quản Lý Bảo Trì & Yêu Cầu Dịch Vụ CNTT

Repository chính thức chứa toàn bộ mã nguồn Backend, Cơ sở dữ liệu, Frontend, Kịch bản kiểm thử (Tests), Postman Collection và Tài liệu tích hợp của Nhóm 1 - Môn CS466.

📖 **Tài liệu hướng dẫn chi tiết:** Xem file **[HUONG_DAN_CHAY_DU_AN.md](file:///d:/Individua_Project/Python_Project/HUONG_DAN_CHAY_DU_AN.md)** để biết cách cấu hình database, đổi mật khẩu MySQL và chạy dự án cho từng vai trò.

---

## 📁 Cấu trúc Thư mục Dự án

- `backend/`: Mã nguồn Backend Python FastAPI (19 RESTful APIs chuẩn, xác thực JWT, RBAC).
- `database/`: Cấu trúc bảng (`schema.sql`), dữ liệu mẫu (`seed.sql`), và tài liệu đặc tả DB.
- `frontend/`: Giao diện web người dùng, mã nguồn JavaScript ([api.js](file:///d:/Individua_Project/Python_Project/frontend/js/api.js)), và tài liệu [API_INTEGRATION_GUIDE.md](file:///d:/Individua_Project/Python_Project/frontend/API_INTEGRATION_GUIDE.md).
- `tests/`: Kịch bản kiểm thử tự động toàn bộ 19 API theo 3 vai trò ([run_role_based_tests.py](file:///d:/Individua_Project/Python_Project/tests/run_role_based_tests.py)) và báo cáo kết quả ([tests/results/](file:///d:/Individua_Project/Python_Project/tests/results/)).
- `postman/`: Bộ sưu tập [CS466_Helpdesk_Postman_Collection.json](file:///d:/Individua_Project/Python_Project/postman/CS466_Helpdesk_Postman_Collection.json) và hướng dẫn test [POSTMAN_TEST_GUIDE.md](file:///d:/Individua_Project/Python_Project/postman/POSTMAN_TEST_GUIDE.md).
- `perl/`: Scripts và báo cáo phân tích Log định dạng chuẩn.
- `docs/`: Đặc tả hợp đồng API (`api-contract.md`), kiến trúc (`architecture.md`), định dạng log (`log-format.md`).

---

## ⚡ Khởi chạy nhanh Backend (Quick Start)

### 1. Cấu hình file `.env`
Tạo file `.env` từ `.env.example` và điền mật khẩu MySQL của bạn:
```powershell
Copy-Item .env.example .env
Copy-Item .env.example backend/.env
```

### 2. Khởi tạo Cơ sở dữ liệu
Nạp 2 file SQL vào MySQL:
```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cs466_helpdesk;"
mysql -u root -p cs466_helpdesk < database/schema.sql
mysql -u root -p cs466_helpdesk < database/seed.sql
```

### 3. Chạy Backend Server
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Health check:** `http://127.0.0.1:8000/api/health`
- **Tài liệu Swagger UI tương tác:** `http://127.0.0.1:8000/docs`

---

## 🎨 Dành cho Lập trình viên Frontend (FE)
- **Tài liệu API chi tiết:** Xem [frontend/API_INTEGRATION_GUIDE.md](file:///d:/Individua_Project/Python_Project/frontend/API_INTEGRATION_GUIDE.md)
- **Tài khoản demo:**
  - Quản trị viên: `admin` / `CS466@123` (Role: `ADMIN`)
  - Kỹ thuật viên: `tech01` / `CS466@123` (Role: `TECHNICIAN`)
  - Người dùng: `user01` / `CS466@123` (Role: `USER`)
- **Module JavaScript có sẵn:** `frontend/js/api.js`
