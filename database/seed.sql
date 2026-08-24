-- ============================================================
-- CS466 - Group 1
-- Demo seed data for cs466_helpdesk
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
    (1, 'admin',  @demo_password_hash, 'Quản trị hệ thống',
        'admin@cs466.local', 'ADMIN', 'ACTIVE'),
    (2, 'tech01', @demo_password_hash, 'Kỹ thuật viên 01',
        'tech01@cs466.local', 'TECHNICIAN', 'ACTIVE'),
    (3, 'user01', @demo_password_hash, 'Người dùng 01',
        'user01@cs466.local', 'USER', 'ACTIVE')
ON DUPLICATE KEY UPDATE
    password_hash = VALUES(password_hash),
    ho_ten = VALUES(ho_ten),
    vai_tro = VALUES(vai_tro),
    trang_thai = VALUES(trang_thai);

-- ------------------------------------------------------------
-- 2. SEED DEVICES (Thiết bị mẫu phục vụ demo)
-- ------------------------------------------------------------
INSERT INTO DEVICES
    (id, ma_thiet_bi, ten_thiet_bi, loai_thiet_bi, vi_tri, trang_thai, mo_ta)
VALUES
    (1, 'PC-001', 'Máy tính phòng Kế toán', 'COMPUTER',
        'Phòng Kế toán', 'ACTIVE', 'Máy tính để bàn'),
    (2, 'PRN-001', 'Máy in văn phòng', 'PRINTER',
        'Văn phòng', 'MAINTENANCE', 'Máy in dùng chung'),
    (3, 'RTR-001', 'Router tầng 2', 'ROUTER',
        'Tầng 2', 'ACTIVE', 'Thiết bị mạng')
ON DUPLICATE KEY UPDATE
    ten_thiet_bi = VALUES(ten_thiet_bi),
    vi_tri = VALUES(vi_tri),
    trang_thai = VALUES(trang_thai);

-- ------------------------------------------------------------
-- 3. SEED SAMPLE TICKET & HISTORY
-- ------------------------------------------------------------
INSERT INTO TICKETS
    (id, tieu_de, mo_ta, loai_yeu_cau, muc_do_uu_tien,
     trang_thai, user_id, device_id, technician_id)
VALUES
    (1,
     'Máy in không in được',
     'Người dùng gửi lệnh in nhưng máy không phản hồi.',
     'INCIDENT',
     'MEDIUM',
     'OPEN',
     3,
     2,
     NULL)
ON DUPLICATE KEY UPDATE
    tieu_de = VALUES(tieu_de),
    mo_ta = VALUES(mo_ta);

INSERT INTO TICKET_HISTORY
    (ticket_id, nguoi_thuc_hien_id, hanh_dong,
     trang_thai_cu, trang_thai_moi, chi_tiet_cap_nhat)
SELECT
    1, 3, 'CREATED', NULL, 'OPEN', 'Ticket mẫu được tạo'
WHERE NOT EXISTS (
    SELECT 1
    FROM TICKET_HISTORY
    WHERE ticket_id = 1 AND hanh_dong = 'CREATED'
);