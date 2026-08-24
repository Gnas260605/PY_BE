# 🚀 HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY DỰ ÁN CS466 HELPDESK
> **Dành cho:** Thành viên nhóm CS466 (Backend, Frontend, Database, Tester)  
> **Repository:** `https://github.com/Gnas260605/PY_BE.git`  
> **Tech Stack:** Python 3.12 (FastAPI), MySQL 8.0, HTML/CSS/Vanilla JS

---

## 📌 MỤC LỤC
1. [Bước 1: Cấu hình Mật khẩu MySQL & Biến môi trường (.env)](#-bước-1-cấu-hình-mật-khẩu-mysql--biến-môi-trường-env)
2. [Bước 2: Khởi tạo Cơ sở dữ liệu MySQL](#-bước-2-khởi-tạo-cơ-sở-dữ-liệu-mysql)
3. [Bước 3: Cài đặt & Khởi chạy Backend Server](#-bước-3-cài-đặt--khởi-chạy-backend-server)
4. [Bước 4: Hướng dẫn dành riêng cho người Code Frontend (FE)](#-bước-4-hướng-dẫn-dành-riêng-cho-người-code-frontend-fe)
5. [Bước 5: Chạy Test tự động & Kiểm thử Postman](#-bước-5-chạy-test-tự-động--kiểm-thử-postman)
6. [Xử lý các lỗi thường gặp (Troubleshooting)](#-xử-lý-các-lỗi-thường-gặp-troubleshooting)

---

## 🔑 BƯỚC 1: CẤU HÌNH MẬT KHẨU MYSQL & BIẾN MÔI TRƯỜNG (.env)

Khi clone dự án về máy, file `.env` không được đẩy lên Git vì lý do bảo mật. Bạn cần tạo file `.env` từ file mẫu `.env.example`.

### 1.1. Tạo file `.env`
Trong thư mục gốc của dự án (hoặc thư mục `backend/`), tạo file có tên **`.env`** (hoặc copy từ `.env.example`):

```powershell
# Trên PowerShell / CMD:
Copy-Item .env.example .env
Copy-Item .env.example backend/.env
```

### 1.2. Đổi mật khẩu Database và thông tin kết nối
Mở file `.env` và `backend/.env` vừa tạo, chỉnh sửa dòng **`MYSQL_PASSWORD`** thành mật khẩu MySQL trên máy của bạn:

```env
APP_NAME=cs466-service-desk
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
LOG_LEVEL=INFO

# ========================================================
# ⬇️ CẤU HÌNH DATABASE MYSQL (ĐIỀN PASSWORD CỦA MÁY BẠN)
# ========================================================
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=cs466_helpdesk
MYSQL_USER=root
MYSQL_PASSWORD=Mật_Khẩu_MySQL_Của_Bạn_Ở_Đây

# ========================================================
# ⬇️ CẤU HÌNH JWT AUTHENTICATION
# ========================================================
JWT_SECRET_KEY=change-me-jwt-secret-key-cs466
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480
```

> ⚠️ **Lưu ý bảo mật quan trọng:**
> 1. Luôn sao chép từ `.env.example` sang `.env` và `backend/.env`.
> 2. Tự đặt mật khẩu MySQL cá nhân (`MYSQL_PASSWORD`).
> 3. Tự đổi `JWT_SECRET_KEY` thành chuỗi bí mật an toàn trên môi trường của bạn.
> 4. Tuyệt đối **KHÔNG commit file `.env`** lên Git repository.
> 5. Giữ nguyên thuật toán `JWT_ALGORITHM=HS256` và thời gian sống `JWT_EXPIRE_MINUTES=480` (8 tiếng).


---

## 🗄️ BƯỚC 2: KHỞI TẠO CƠ SỞ DỮ LIỆU MYSQL

Hệ thống cần database có tên `cs466_helpdesk` và dữ liệu ban đầu.

### Cách 1: Sử dụng MySQL Workbench / DBeaver / Navicat (Khuyên dùng)
1. Mở công cụ quản lý MySQL của bạn.
2. Tạo database mới:
   ```sql
   CREATE DATABASE IF NOT EXISTS cs466_helpdesk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Mở và thực thi (Execute) lần lượt 2 file SQL:
   - **`database/schema.sql`** *(Tạo 4 bảng: USERS, DEVICES, TICKETS, TICKET_HISTORY)*.
   - **`database/seed.sql`** *(Tạo sẵn 3 tài khoản mẫu demo: admin, tech01, user01)*.

### Cách 2: Sử dụng Command Line (PowerShell)
```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cs466_helpdesk;"
mysql -u root -p cs466_helpdesk < database/schema.sql
mysql -u root -p cs466_helpdesk < database/seed.sql
```

### Cách 3: Sử dụng Docker Compose (Nếu có cài Docker)
```powershell
docker-compose up -d mysql
```

---

## 💻 BƯỚC 3: CÀI ĐẶT & KHỞI CHẠY BACKEND SERVER

### 3.1. Tạo môi trường ảo Python & Cài đặt thư viện
Mở Terminal / PowerShell tại thư mục dự án:

```powershell
# Di chuyển vào thư mục backend
cd backend

# Tạo môi trường ảo .venv
python -m venv .venv

# Kích hoạt môi trường ảo (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Cài đặt toàn bộ thư viện cần thiết
pip install -r requirements.txt
```

> **Lưu ý trên Windows:** Nếu gặp lỗi `execution of scripts is disabled on this system`, hãy chạy PowerShell với quyền Administrator và gõ: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.

### 3.2. Khởi động Backend Server
Chạy lệnh sau:
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Server sẽ khởi động tại: **`http://127.0.0.1:8000`**

### 3.3. Kiểm tra Server hoạt động
- **Health check API:** Truy cập trình duyệt `http://127.0.0.1:8000/api/health` $\to$ Trả về `{"status":"ok"}`.
- **Tài liệu Swagger UI tương tác:** Truy cập `http://127.0.0.1:8000/docs` để xem và test thử trực tiếp toàn bộ 19 API trên giao diện web Swagger!

---

## 🎨 BƯỚC 4: HƯỚNG DẪN DÀNH RIÊNG CHO NGƯỜI CODE FRONTEND (FE)

Dành cho bạn làm giao diện (HTML/CSS/JS) để tích hợp mượt mà với Backend:

### 4.1. Thông tin kết nối Backend
- **Base URL:** `http://127.0.0.1:8000/api`
- **Cơ chế xác thực:** Gửi Header `Authorization: Bearer <access_token>` sau khi đăng nhập.
- **Tài liệu đặc tả đầy đủ:** Xem chi tiết 19 endpoint tại [frontend/API_INTEGRATION_GUIDE.md](file:///d:/Individua_Project/Python_Project/frontend/API_INTEGRATION_GUIDE.md).

### 4.2. Tài khoản mẫu để đăng nhập trên giao diện
Mật khẩu chung cho tất cả tài khoản demo: **`CS466@123`**

| Tài khoản | Mật khẩu | Vai trò | Chức năng giao diện cần hiển thị |
|:---|:---:|:---:|:---|
| **`admin`** | `CS466@123` | `ADMIN` | Quản lý Users, Quản lý Thiết bị, Gán Kỹ thuật viên, Xem toàn bộ Tickets |
| **`tech01`** | `CS466@123` | `TECHNICIAN` | Xem thiết bị, cập nhật trạng thái (`IN_PROGRESS` $\to$ `RESOLVED` $\to$ `CLOSED`) |
| **`user01`** | `CS466@123` | `USER` | Tạo Ticket hỗ trợ, xem/sửa Ticket của chính mình, xem lịch sử xử lý |

### 4.3. Cách gọi API bằng JavaScript (Đã xây dựng sẵn)
Bạn có thể import trực tiếp module [frontend/js/api.js](file:///d:/Individua_Project/Python_Project/frontend/js/api.js):

```javascript
import { authApi, usersApi, devicesApi, ticketsApi } from "../js/api.js";

// 1. Đăng nhập
async function onLoginClick() {
  try {
    const res = await authApi.login("user01", "CS466@123");
    console.log("Đăng nhập thành công, Token:", res.access_token);
    console.log("Thông tin user:", res.user);
    // Tự động lưu token vào localStorage và chuyển trang
    window.location.href = "dashboard.html";
  } catch (err) {
    alert("Đăng nhập thất bại: " + err.message);
  }
}

// 2. Lấy danh sách ticket
async function loadTickets() {
  try {
    const tickets = await ticketsApi.listTickets();
    console.log("Danh sách tickets:", tickets);
    // Render tickets ra bảng/giao diện HTML
  } catch (err) {
    console.error("Lỗi:", err);
  }
}
```

### 4.4. Cách chạy giao diện Frontend cục bộ
- **Cách 1 (VS Code):** Cài extension **Live Server**, click chuột phải vào file `frontend/pages/index.html` chọn **Open with Live Server**.
- **Cách 2 (Python built-in server):**
  ```powershell
  cd frontend
  python -m http.server 3000
  ```
  Truy cập trình duyệt: `http://127.0.0.1:3000/pages/`

---

## 🧪 BƯỚC 5: CHẠY TEST TỰ ĐỘNG & KIỂM THỬ POSTMAN

### 5.1. Chạy Suite kiểm thử tự động toàn bộ 19 API theo 3 Roles
Từ thư mục gốc dự án, chạy lệnh:
```powershell
python tests/run_role_based_tests.py
```
Script sẽ tự động kiểm tra 39 test cases trên 3 vai trò và cập nhật báo cáo vào thư mục `tests/results/`.

### 5.2. Chạy với Postman
1. Mở Postman $\to$ Chọn **Import** $\to$ Chọn file [postman/CS466_Helpdesk_Postman_Collection.json](file:///d:/Individua_Project/Python_Project/postman/CS466_Helpdesk_Postman_Collection.json).
2. Đọc hướng dẫn test chi tiết từng bước tại [postman/POSTMAN_TEST_GUIDE.md](file:///d:/Individua_Project/Python_Project/postman/POSTMAN_TEST_GUIDE.md).

---

## 🛠️ XỬ LÝ CÁC LỖI THƯỜNG GẶP (TROUBLESHOOTING)

| Hiện tượng / Báo lỗi | Nguyên nhân | Cách khắc phục |
|:---|:---|:---|
| `Access denied for user 'root'@'localhost'` | Sai mật khẩu MySQL trong file `.env` | Mở file `.env` và `backend/.env`, kiểm tra và điền đúng `MYSQL_PASSWORD` của máy bạn. |
| `Can't connect to MySQL server on '127.0.0.1'` | Dịch vụ MySQL chưa khởi động | Bật MySQL service trong `Services.msc` hoặc khởi động XAMPP / MySQL Workbench. |
| `Unknown database 'cs466_helpdesk'` | Chưa tạo database | Chạy lệnh `CREATE DATABASE cs466_helpdesk;` và nạp `schema.sql` + `seed.sql`. |
| `Cannot find module 'fastapi'` | Chưa kích hoạt `.venv` | Chạy `.venv\Scripts\activate` rồi gõ `pip install -r requirements.txt`. |
| `Address already in use (Port 8000)` | Đang có server uvicorn chạy nền | Tắt tiến trình cũ hoặc chạy với port khác: `python -m uvicorn app.main:app --port 8080`. |

---
*Chúc các thành viên nhóm CS466 phát triển và tích hợp dự án thành công! 🎉*
