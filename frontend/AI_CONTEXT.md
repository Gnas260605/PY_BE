# 📘 Frontend Architecture & AI Development Guide (CS466 Helpdesk)

Tài liệu hướng dẫn phát triển và chuẩn hóa mã nguồn dành cho Kỹ sư Frontend và AI Assistant khi xây dựng giao diện NiceGUI trong dự án **CS466 Helpdesk**.

---

## 🏗️ 1. Cấu trúc Thư mục Chuẩn (`frontend/`)

```
frontend/
├── core/                       # Cấu hình, API client, Constants, Cache TTL
│   ├── config.py               # Host, Port, Backend API URL, Storage Secret
│   ├── constants.py            # Enums: Role, TicketStatus, TicketPriority, Category
│   └── http_client.py          # HTTPX Async Client tích hợp Bearer Token
├── common/                     # Design System & Components dùng chung
│   ├── styles/
│   │   ├── theme.py            # Design tokens, Typography, UI constants, Quasar CSS
│   │   └── breakpoints.py      # Responsive classes (RESPONSIVE_PAGE, RESPONSIVE_GRID)
│   └── components/             # Reusable UI Blocks
│       ├── layout.py           # app_shell (Auth check, Sidebar, Navbar, Mobile Nav)
│       ├── navbar.py           # Top Header with User profile & Logout
│       ├── sidebar.py          # Role-based left drawer navigation
│       ├── bottom_nav.py       # Mobile bottom navigation bar
│       ├── status_badge.py     # Priority, Status & Role badge pills
│       ├── stat_card.py        # KPI Metric cards
│       ├── empty_state.py      # Zero-data illustration & CTA button
│       ├── loading.py          # Skeleton loaders & async spinners
│       ├── timeline.py         # Ticket audit history stepper
│       ├── comments_thread.py  # Real-time 2-way chat with technicians
│       └── toast.py            # Toast notifications & Modal Popups (`show_popup`)
├── services/                   # Business Services & API Integration
│   ├── auth_service.py         # Login, Logout, Session & Role storage
│   ├── ticket_service.py       # CRUD Tickets, History, Comments, Stats
│   ├── user_service.py         # User management, Technician lists
│   └── device_service.py       # Device inventory & lookup
├── views/                      # Role-Scoped Page Views
│   ├── auth/login_view.py      # Clean Login page with quick demo buttons
│   ├── dashboard_view.py       # Admin & Tech Operations Analytics Dashboard
│   ├── admin/                  # ADMIN only views
│   │   ├── ticket_dispatch_view.py  # Incident Dispatch Control Deck
│   │   ├── device_mgmt_view.py      # Device inventory CRUD
│   │   └── user_mgmt_view.py        # User account & status toggles
│   ├── technician/             # TECHNICIAN only views
│   │   ├── task_board_view.py       # 4-column Kanban Board & 1-click claim
│   │   └── device_lookup_view.py    # Device & ticket history lookup
│   ├── user/                   # USER only views
│   │   ├── my_tickets_view.py       # "Yêu cầu của tôi" (User ticket desk)
│   │   └── create_ticket_view.py    # Ticket creation form with device association
│   └── tickets/
│       └── ticket_detail_view.py    # 2-column ticket workspace & live chat
└── app.py                      # NiceGUI Entrypoint & Route declarations
```

---

## 🎨 2. Design System Tokens (`common/styles/theme.py`)

Khi viết view mới, **BẮT BUỘC** sử dụng các hằng số phong cách có sẵn thay vì hardcode class Tailwind rời rạc:

| Hằng số | Giá trị Utility | Mục đích sử dụng |
| :--- | :--- | :--- |
| `STYLE_CARD` | `p-5 rounded-2xl bg-white border border-slate-200/90 shadow-2xs hover:shadow-xs transition-all` | Khối card chính, bề mặt trắng cao cấp |
| `STYLE_CARD_COMPACT` | `p-3.5 rounded-xl bg-white border border-slate-200/90 shadow-2xs` | Card tóm tắt / thẻ danh sách gọn |
| `STYLE_CARD_MUTED` | `p-4 rounded-xl bg-slate-50/70 border border-slate-200/70` | Khối nền phụ, form hướng dẫn |
| `STYLE_PAGE_HEADER` | `w-full justify-between items-center py-2 border-b border-slate-200/80 mb-4` | Tiêu đề đầu trang |
| `STYLE_TITLE_LG` | `text-xl font-bold text-slate-900 tracking-tight leading-snug` | Tiêu đề chính trang (H1) |
| `STYLE_TITLE_MD` | `text-base font-bold text-slate-900 leading-snug` | Tiêu đề phân mục / tên sự cố |
| `STYLE_SUBTITLE` | `text-xs text-slate-500 leading-normal` | Mô tả phụ bên dưới tiêu đề |
| `STYLE_TAG_LABEL` | `text-[10px] font-bold text-slate-400 uppercase tracking-wider` | Nhãn phân loại in hoa |

---

## ⚡ 3. Quy chuẩn Kỹ thuật Bắt buộc (Rules for AI & Developers)

1. **Sử dụng `app_shell(page_title, content_func)`**:
   Tất cả các trang nội bộ (ngoại trừ Login) phải được bọc trong `app_shell` để tự động kiểm tra đăng nhập, nạp Sidebar và Topbar theo đúng `role`.
2. **Xử lý 3 Trạng thái Async (Loading - Success - Error)**:
   - **Loading**: Luôn hiển thị `skeleton_loader()` hoặc `loading_spinner()` trong lúc chờ API phản hồi.
   - **Success**: Kích hoạt `toast.success(...)` hoặc `toast.show_popup(...)` đối với các hành động quan trọng (tạo ticket, phân công).
   - **Error**: Bắt ngoại lệ và hiển thị `toast.show_popup(..., type="error", detail=str(exc))` để người dùng và tester biết chính xác lỗi.
3. **Tránh Lag & Giật màn hình**:
   - Sử dụng `@ui.refreshable` cho các danh sách động thay vì gọi `container.clear()` liên tục.
4. **Phân quyền Nghiệp vụ Nghiêm ngặt**:
   - `USER`: Chỉ được xem và tạo ticket của chính mình (`user_id == current_user.id`), chat với KTV. Không thấy nút phân công hay chuyển trạng thái kỹ thuật.
   - `TECHNICIAN`: Được nhận ticket `OPEN`, chuyển trạng thái ticket được giao (`IN_PROGRESS`, `RESOLVED`), tra cứu thiết bị.
   - `ADMIN`: Quản lý toàn quyền, phân công KTV cho các ticket, quản lý tài khoản và thiết bị.

---

## 🤖 4. AI Prompt Template Chuẩn

### 📝 Prompt 1: Tạo View Mới
```markdown
Vai trò: Bạn là Senior Frontend Engineer chuyên về Python NiceGUI.
Nhiệm vụ: Tạo view cho [Tên chức năng, VD: "Màn hình Báo cáo Thống kê Sự cố cho Admin"].
Yêu cầu kỹ thuật bắt buộc:
1. Bọc trong app_shell(title, content) từ `common/components/layout.py`.
2. Áp dụng Design Tokens từ `common/styles/theme.py` (STYLE_CARD, STYLE_PAGE_HEADER, v.v.).
3. Xử lý đầy đủ 3 trạng thái: Loading (dùng skeleton_loader), Success (toast), Error (toast.show_popup).
4. Sử dụng @ui.refreshable cho các khối dữ liệu động.
5. Code có Type Hinting rõ ràng và tuân thủ strict role access.
```

### 🔧 Prompt 2: Refactor View Hiện tại
```markdown
Vai trò: Senior Frontend Engineer chuyên NiceGUI.
Nhiệm vụ: Refactor file `[tên_file.py]` hiện tại.
Vấn đề cần giải quyết: [VD: Thay thế hardcode styles, thêm skeleton loading, bổ sung modal popup xác nhận].
Yêu cầu:
1. Thay thế CSS bằng theme.py constants.
2. Thêm skeleton loading khi tải API.
3. Sử dụng show_popup cho các thao tác CRUD.
4. Giữ nguyên 100% logic nghiệp vụ và tương thích API Contract.
```
