# 📋 KẾ HOẠCH PHÁT TRIỂN & NÂNG CẤP HỆ THỐNG CHI TIẾT (ASSIGNED TO: NGUYÊN PHẠM THIỆN ÂN)

> **Mục tiêu:** Nâng cấp toàn diện giao diện Helpdesk Portal từ bản khung sơ khởi lên phiên bản hoàn thiện chuẩn **Production-Ready**, bổ sung đầy đủ tính năng tương tác chuyên sâu, biểu đồ trực quan, hệ thống trao đổi (comment/timeline) và hoàn thiện tài liệu tích hợp toàn dự án.

---

## 🏗️ I. TỔNG QUAN KIẾN TRÚC & QUY CHUẨN KỸ THUẬT

1. **Frontend Stack:** Python `nicegui` (v2.x), CSS Tailwind/Quasar, Material Icons, Typography `Plus Jakarta Sans`.
2. **Backend Stack:** FastAPI, MySQL Connector (Raw SQL + Transaction scopes), Pydantic v2, JWT RBAC.
3. **Nguyên tắc cốt lõi:**
   - **Tuyệt đối không hard-code dữ liệu:** Mọi dữ liệu phải thông qua `frontend/services/` kết nối REST API.
   - **Tương thích 3 Vai trò (RBAC):** `ADMIN` (toàn quyền), `TECHNICIAN` (quản lý công việc & thiết bị), `USER` (tạo & theo dõi ticket của mình).
   - **Xử lý lỗi mượt mà:** Mọi thao tác API phải có thông báo `toast.success` hoặc `toast.error`, không để crash giao diện.

---

## 🎯 II. CHI TIẾT CÁC MODULE CẦN THỰC THI

### 📦 MODULE 1: MÀN HÌNH CHI TIẾT TICKET, TIMELINE & BÌNH LUẬN (TICKET DETAIL & COMMENTS)
* **Vị trí file:** `frontend/views/user/ticket_timeline_view.py` hoặc tạo mới `frontend/views/tickets/ticket_detail_view.py`
* **Route:** `/tickets/{ticket_id}` hoặc `/tickets/{ticket_id}/history`

#### 1.1. Giao diện Header & Thông tin Ticket:
- [ ] Hiển thị Mã Ticket `#TCK-{id}`, Tiêu đề lớn, Chip trạng thái (`status_badge`), Chip độ ưu tiên có màu sắc đặc trưng:
  - `URGENT`: Đỏ rực (`bg-red-100 text-red-700 border-red-200`)
  - `HIGH`: Cam (`bg-orange-100 text-orange-700 border-orange-200`)
  - `MEDIUM`: Vàng (`bg-amber-100 text-amber-700 border-amber-200`)
  - `LOW`: Xanh lá/lam (`bg-slate-100 text-slate-700 border-slate-200`)
- [ ] Card thông tin tóm tắt: Người tạo, Thiết bị liên quan (Mã TB, Loại TB, Vị trí), Kỹ thuật viên phụ trách, Thời gian tạo, Thời gian cập nhật gần nhất.

#### 1.2. Dòng thời gian lịch sử xử lý (Audit Timeline):
- [ ] Gọi API `GET /api/tickets/{ticket_id}/history` qua `ticket_service.get_history(ticket_id)`.
- [ ] Hiển thị dạng Timeline dọc có icon trực quan:
  - Điểm mốc: Thay đổi trạng thái (`OPEN` $\rightarrow$ `ASSIGNED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `RESOLVED` $\rightarrow$ `CLOSED`).
  - Hiển thị ai đã thực hiện thao tác và lúc mấy giờ kèm ghi chú đóng/xử lý.

#### 1.3. Khung trao đổi phản hồi (Comments / Discussion Thread):
- [ ] Giao diện danh sách tin nhắn/bình luận 2 bên (Người dùng bên trái, Kỹ thuật viên/Admin bên phải).
- [ ] Form nhập bình luận mới gồm `ui.textarea` và nút `Gửi phản hồi`.
- [ ] Kết nối API bình luận (khi Backend có sẵn) hoặc chuẩn bị sẵn hàm trong `ticket_service.py`.

#### 1.4. Thanh công cụ tác vụ nhanh (Quick Actions Toolbar):
- [ ] **Dành cho ADMIN:** Nút "Phân công kỹ thuật viên" (mở Modal chọn KTV).
- [ ] **Dành cho TECHNICIAN:** Nút chuyển trạng thái nhanh (`Bắt đầu xử lý`, `Đã khắc phục`).
- [ ] **Dành cho ADMIN / TECHNICIAN:** Nút "Đóng sự cố" (mở Modal nhập giải pháp xử lý).

---

### 📦 MODULE 2: BẢNG CÔNG VIỆC KANBAN BOARD CHO KỸ THUẬT VIÊN
* **Vị trí file:** `frontend/views/technician/task_board_view.py`
* **Route:** `/technician/tasks`

#### 2.1. Thiết kế 4 Cột Trạng thái Kanban:
- [ ] Cột 1: **CHỜ TIẾP NHẬN / PHÂN CÔNG** (`OPEN` / `ASSIGNED`)
- [ ] Cột 2: **ĐANG XỬ LÝ** (`IN_PROGRESS`)
- [ ] Cột 3: **ĐÃ KHẮC PHỤC** (`RESOLVED`)
- [ ] Cột 4: **ĐÃ ĐÓNG / HOÀN TẤT** (`CLOSED`)

#### 2.2. Thẻ Ticket Card trên Kanban:
- [ ] Thiết kế Card nhỏ gọn, bo góc mềm mại, hover lift:
  - Mã Ticket, Tiêu đề ngắn gọn (line-clamp-2).
  - Tên thiết bị + Vị trí phòng ban.
  - Chip độ ưu tiên.
  - Avatar / Tên người gửi yêu cầu.
  - Nút chuyển trạng thái nhanh 1-click sang bước tiếp theo (VD: từ `ASSIGNED` bấm 1 nút chuyển ngay sang `IN_PROGRESS`).

---

### 📦 MODULE 3: NÂNG CẤP DASHBOARD VỚI BIỂU ĐỒ TRỰC QUAN (CHARTS & ANALYTICS)
* **Vị trí file:** `frontend/views/dashboard_view.py`
* **Route:** `/dashboard`

#### 3.1. Tích hợp Biểu đồ ECharts qua NiceGUI (`ui.echart`):
- [ ] **Biểu đồ tròn (Doughnut Chart):** Cơ cấu trạng thái Ticket (Tỷ lệ phần trăm giữa Open, In Progress, Resolved, Closed) với màu sắc bắt mắt.
- [ ] **Biểu đồ cột (Bar Chart):** Phân bố sự cố theo danh mục (`HARDWARE`, `SOFTWARE`, `NETWORK`, `ACCOUNT`, `OTHER`).
- [ ] **Biểu đồ mức độ ưu tiên:** Thể hiện số lượng ticket `URGENT` và `HIGH` đang tồn đọng.

#### 3.2. Widget Sự cố khẩn cấp (Urgent Incident Feed):
- [ ] Bảng danh sách 5 sự cố ưu tiên cao nhất chưa xử lý kèm nút "Xem ngay" dẫn thẳng tới chi tiết ticket.

---

### 📦 MODULE 4: HOÀN THIỆN CÁC DIALOG & MODAL CRUD
* **Vị trí file:** `frontend/views/admin/user_mgmt_view.py`, `frontend/views/admin/device_mgmt_view.py`, `frontend/views/user/create_ticket_view.py`

#### 4.1. Modal Quản lý Người dùng:
- [ ] **Modal Thêm người dùng:** Nhập `Username`, `Họ tên`, `Email`, `Mật khẩu ban đầu`, `Vai trò` (Dropdown: `ADMIN`, `TECHNICIAN`, `USER`). Validate email hợp lệ và mật khẩu tối thiểu 6 ký tự.
- [ ] **Dialog Khóa/Mở khóa:** Nút bật/tắt trạng thái `ACTIVE` / `INACTIVE` với Dialog xác nhận "Bạn có chắc chắn muốn khóa tài khoản này?".

#### 4.2. Modal Quản lý Thiết bị:
- [ ] **Modal Thêm thiết bị:** `Mã thiết bị` (VD: `PC-003`), `Tên thiết bị`, `Loại thiết bị` (`COMPUTER`, `PRINTER`, `ROUTER`, `SERVER`, `OTHER`), `Vị trí`, `Mô tả`.
- [ ] **Modal Sửa thiết bị:** Cho phép cập nhật Tên, Vị trí, Trạng thái hoạt động (`ACTIVE`, `MAINTENANCE`, `DECOMMISSIONED`).

#### 4.3. Wizard Tạo Ticket cho User (`/user/tickets/new`):
- [ ] Dropdown chọn thiết bị (tự động load danh sách thiết bị `ACTIVE` từ API).
- [ ] Chọn Loại sự cố, Mức độ ưu tiên.
- [ ] Nhập Tiêu đề và Mô tả chi tiết vấn đề đang gặp phải.
- [ ] Nút gửi với hiệu ứng loading và tự động chuyển về trang danh sách ticket khi tạo thành công.

---

### 📦 MODULE 5: ĐỒNG BỘ TÀI LIỆU TOÀN DỰ ÁN & HƯỚNG DẪN BÀN GIAO
* **Vị trí file:** `docs/api-contract.md`, `README.md`, `HUONG_DAN_CHAY_DU_AN.md`

- [ ] Cập nhật tài liệu `docs/api-contract.md` đầy đủ 19+ APIs kèm payload request/response mẫu.
- [ ] Cập nhật file `README.md` & `HUONG_DAN_CHAY_DU_AN.md` hướng dẫn chi tiết cách chạy đồng thời Backend (port 8000) và NiceGUI Frontend (port 8500).
- [ ] Viết tài liệu bàn giao `docs/USER_GUIDE_PORTAL.md` hướng dẫn sử dụng cho từng vai trò Admin, Kỹ thuật viên, Người dùng.

---

## 📅 III. LỘ TRÌNH THỰC HIỆN & TIÊU CHUẨN NGHIỆM THU

| Giai đoạn | Nội dung trọng tâm | Tiêu chuẩn nghiệm thu (Definition of Done) |
|---|---|---|
| **Sprint 2A** | Module 1 (Ticket Detail & Timeline) & Module 4 (CRUD Modals) | • Tạo/sửa user, thiết bị hoạt động 100% qua API.<br>• Xem được chi tiết và timeline lịch sử của từng ticket. |
| **Sprint 2B** | Module 2 (Kanban Board) & Module 3 (Dashboard Charts) | • KTV thao tác chuyển trạng thái ticket mượt mà trên Kanban.<br>• Dashboard hiển thị biểu đồ ECharts phân tích sống động. |
| **Sprint 2C** | Module 5 (Docs & User Guide) & Polish UI toàn diện | • Kiểm thử toàn bộ 3 vai trò không có lỗi phát sinh.<br>• Tài liệu đầy đủ, hình ảnh minh họa rõ ràng. |

---

*Tài liệu được lập ngày 13/09/2026 bởi Team Lead.*
