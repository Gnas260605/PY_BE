-- ============================================================
-- CS466 - Group 1
-- Comprehensive Demo Seed Data for cs466_helpdesk
--
-- Password mặc định cho TẤT CẢ tài khoản seed: CS466@123
-- Định dạng hash: bcrypt $2b$ (chuẩn Python bcrypt / passlib)
-- ============================================================

USE cs466_helpdesk;

-- Hash Bcrypt chuẩn của mật khẩu CS466@123
SET @demo_password_hash = '$2b$12$2Vl80yHohx8BrNS84SA/ueHoQ7SmXw276VW7OHiITT2TXMaPe.ZUC';

-- ------------------------------------------------------------
-- 1. SEED USERS (Đủ 3 vai trò: ADMIN, TECHNICIAN, USER)
-- ------------------------------------------------------------
INSERT INTO USERS
    (id, username, password_hash, ho_ten, email, vai_tro, trang_thai)
VALUES
    (1, 'admin',   @demo_password_hash, 'Quản trị hệ thống', 'admin@cs466.local', 'ADMIN', 'ACTIVE'),
    (2, 'tech01',  @demo_password_hash, 'Kỹ thuật viên 01', 'tech01@cs466.local', 'TECHNICIAN', 'ACTIVE'),
    (3, 'user01',  @demo_password_hash, 'Người dùng 01', 'user01@cs466.local', 'USER', 'ACTIVE'),
    (4, 'user02',  @demo_password_hash, 'Nguyễn Văn B (Kế toán)', 'ketoan_b@cs466.local', 'USER', 'ACTIVE'),
    (5, 'tech02',  @demo_password_hash, 'Kỹ thuật viên 02', 'tech02@cs466.local', 'TECHNICIAN', 'ACTIVE'),
    (6, 'user03',  @demo_password_hash, 'Trần Thị C (Nhân sự)', 'nhansu_c@cs466.local', 'USER', 'ACTIVE'),
    (7, 'user04',  @demo_password_hash, 'Lê Văn D (Kinh doanh)', 'kinhdoanh_d@cs466.local', 'USER', 'INACTIVE')
ON DUPLICATE KEY UPDATE
    password_hash = VALUES(password_hash),
    ho_ten = VALUES(ho_ten),
    email = VALUES(email),
    vai_tro = VALUES(vai_tro),
    trang_thai = VALUES(trang_thai);

-- ------------------------------------------------------------
-- 2. SEED DEVICES (Đa dạng danh mục & vị trí)
-- ------------------------------------------------------------
INSERT INTO DEVICES
    (id, ma_thiet_bi, ten_thiet_bi, loai_thiet_bi, vi_tri, trang_thai, mo_ta)
VALUES
    (1, 'PC-001',  'Máy tính phòng Kế toán 01', 'COMPUTER', 'Phòng Kế toán - Tầng 2', 'ACTIVE', 'Dell Optiplex 7090 i7 16GB'),
    (2, 'PRN-001', 'Máy in laser văn phòng',    'PRINTER',  'Hành lang Tầng 2',        'MAINTENANCE', 'Canon LBP 2900 đa năng'),
    (3, 'RTR-001', 'Router Cisco Core Tầng 2',  'ROUTER',   'Phòng Server Tầng 2',     'ACTIVE', 'Cisco RV340 Dual WAN VPN'),
    (4, 'PC-002',  'Máy tính phòng Nhân sự',    'COMPUTER', 'Phòng Nhân sự - Tầng 3',  'ACTIVE', 'HP EliteDesk 800 G6'),
    (5, 'SRV-001', 'Máy chủ Database Chính',   'SERVER',   'Phòng Server Tầng 2',     'ACTIVE', 'Dell PowerEdge R740 64GB RAM'),
    (6, 'PRN-002', 'Máy in màu phòng Thiết kế', 'PRINTER',  'Phòng Design - Tầng 4',   'ACTIVE', 'Epson L8056 Wifi'),
    (7, 'SW-001',  'Switch mạng tầng 3',        'SWITCH',   'Hộp kỹ thuật Tầng 3',     'ACTIVE', 'TP-Link 24-Port Gigabit Switch')
ON DUPLICATE KEY UPDATE
    ten_thiet_bi = VALUES(ten_thiet_bi),
    loai_thiet_bi = VALUES(loai_thiet_bi),
    vi_tri = VALUES(vi_tri),
    trang_thai = VALUES(trang_thai),
    mo_ta = VALUES(mo_ta);

-- ------------------------------------------------------------
-- 3. SEED TICKETS (Đầy đủ mọi trạng thái, danh mục và độ ưu tiên)
-- ------------------------------------------------------------
INSERT INTO TICKETS
    (id, tieu_de, mo_ta, loai_yeu_cau, muc_do_uu_tien, trang_thai, user_id, device_id, technician_id, created_at, resolved_at, closed_at)
VALUES
    (1, 'Máy in không in được từ máy tính kế toán', 'Người dùng gửi lệnh in từ PC-001 nhưng máy in Canon không phản hồi, đèn báo nháy đỏ.', 'INCIDENT', 'MEDIUM', 'CLOSED', 3, 2, 2, '2026-08-24 08:30:00', '2026-08-24 11:00:00', '2026-08-24 13:59:00'),
    (2, 'Màn hình PC-001 không lên nguồn', 'Màn hình bật không lên tín hiệu, quạt máy tính vẫn quay. Đã thử đổi ổ cắm.', 'INCIDENT', 'URGENT', 'OPEN', 4, 1, NULL, '2026-08-24 09:15:00', NULL, NULL),
    (3, 'Mất kết nối mạng toàn bộ phòng Nhân sự', 'Toàn bộ máy tính tầng 3 không thể truy cập internet và mạng nội bộ.', 'INCIDENT', 'URGENT', 'IN_PROGRESS', 6, 7, 2, '2026-08-24 10:00:00', NULL, NULL),
    (4, 'Cài đặt phần mềm kế toán MISA mới', 'Cần cài đặt bản quyền phần mềm MISA 2026 cho máy tính kế toán viên mới.', 'SERVICE_REQUEST', 'HIGH', 'ASSIGNED', 4, 1, 5, '2026-08-24 10:45:00', NULL, NULL),
    (5, 'Bảo trì định kỳ máy chủ cơ sở dữ liệu', 'Thực hiện hút bụi, kiểm tra dung lượng ổ cứng và sao lưu database tháng 8.', 'MAINTENANCE', 'MEDIUM', 'RESOLVED', 3, 5, 2, '2026-08-24 11:30:00', '2026-08-24 16:00:00', NULL),
    (6, 'Thay hộp mực máy in màu phòng Thiết kế', 'Máy in màu Epson L8056 báo cạn mực vàng và xanh, bản in bị sọc.', 'SERVICE_REQUEST', 'LOW', 'OPEN', 3, 6, NULL, '2026-08-24 14:00:00', NULL, NULL),
    (7, 'Cấp quyền truy cập thư mục chung phòng Kế toán', 'Nhân viên mới cần quyền truy cập thư mục Z:\\Accounting trên File Server.', 'SERVICE_REQUEST', 'MEDIUM', 'RESOLVED', 4, 5, 5, '2026-08-24 14:30:00', '2026-08-24 15:45:00', NULL),
    (8, 'Bảo trì nâng cấp Firmware Router Tầng 2', 'Cập nhật bản vá bảo mật CVE-2026 cho Router Cisco phòng Server.', 'MAINTENANCE', 'HIGH', 'IN_PROGRESS', 3, 3, 5, '2026-08-24 15:00:00', NULL, NULL)
ON DUPLICATE KEY UPDATE
    tieu_de = VALUES(tieu_de),
    mo_ta = VALUES(mo_ta),
    loai_yeu_cau = VALUES(loai_yeu_cau),
    muc_do_uu_tien = VALUES(muc_do_uu_tien),
    trang_thai = VALUES(trang_thai),
    user_id = VALUES(user_id),
    device_id = VALUES(device_id),
    technician_id = VALUES(technician_id),
    resolved_at = VALUES(resolved_at),
    closed_at = VALUES(closed_at);

-- ------------------------------------------------------------
-- 4. SEED TICKET_HISTORY
-- ------------------------------------------------------------
INSERT INTO TICKET_HISTORY
    (id, ticket_id, nguoi_thuc_hien_id, hanh_dong, trang_thai_cu, trang_thai_moi, chi_tiet_cap_nhat, thoi_gian)
VALUES
    (1, 1, 3, 'CREATED', NULL, 'OPEN', 'Khởi tạo sự cố máy in', '2026-08-24 08:30:00'),
    (2, 1, 1, 'ASSIGNED', 'OPEN', 'ASSIGNED', 'Phân công xử lý cho tech01', '2026-08-24 09:00:00'),
    (3, 1, 2, 'STATUS_CHANGED', 'ASSIGNED', 'IN_PROGRESS', 'Kỹ thuật viên bắt đầu kiểm tra', '2026-08-24 09:30:00'),
    (4, 1, 2, 'STATUS_CHANGED', 'IN_PROGRESS', 'RESOLVED', 'Đã xử lý kẹt giấy và vệ sinh trục lăn', '2026-08-24 11:00:00'),
    (5, 1, 2, 'CLOSED', 'RESOLVED', 'CLOSED', 'Người dùng xác nhận máy in chạy tốt', '2026-08-24 13:59:00'),
    (6, 2, 4, 'CREATED', NULL, 'OPEN', 'Khởi tạo sự cố màn hình không nguồn', '2026-08-24 09:15:00'),
    (7, 3, 6, 'CREATED', NULL, 'OPEN', 'Báo cáo mất mạng tầng 3', '2026-08-24 10:00:00'),
    (8, 3, 1, 'ASSIGNED', 'OPEN', 'ASSIGNED', 'Giao việc cho tech01', '2026-08-24 10:10:00'),
    (9, 3, 2, 'STATUS_CHANGED', 'ASSIGNED', 'IN_PROGRESS', 'Đang kiểm tra Switch mạng tầng 3', '2026-08-24 10:20:00')
ON DUPLICATE KEY UPDATE
    chi_tiet_cap_nhat = VALUES(chi_tiet_cap_nhat);

-- ------------------------------------------------------------
-- 5. SEED TICKET_COMMENTS
-- ------------------------------------------------------------
INSERT INTO TICKET_COMMENTS
    (id, ticket_id, user_id, noi_dung, created_at)
VALUES
    (1, 1, 2, 'Kỹ thuật viên đã kiểm tra, máy in bị kẹt giấy vụn bên trong cartridge.', '2026-08-24 09:45:00'),
    (2, 1, 3, 'Cảm ơn anh, phòng kế toán đã in lại hóa đơn bình thường rồi ạ.', '2026-08-24 11:15:00'),
    (3, 3, 6, 'Các máy phòng nhân sự vẫn chưa có mạng, mong IT hỗ trợ gấp giúp bên em.', '2026-08-24 10:15:00'),
    (4, 3, 2, 'KTV đang reset lại cổng switch phòng kỹ thuật tầng 3, dự kiến 10 phút nữa có lại.', '2026-08-24 10:25:00')
ON DUPLICATE KEY UPDATE
    noi_dung = VALUES(noi_dung);