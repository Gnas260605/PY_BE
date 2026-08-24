-- ============================================================
-- CS466 - Group 1
-- Project: Hệ thống quản lý bảo trì và yêu cầu dịch vụ CNTT
-- Database: cs466_helpdesk
-- MySQL: 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS cs466_helpdesk
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE cs466_helpdesk;

-- ------------------------------------------------------------
-- 1. BẢNG USERS (Quản lý tài khoản & phân quyền)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS USERS (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    ho_ten VARCHAR(100) NOT NULL,
    email VARCHAR(120) NULL,
    vai_tro ENUM('USER', 'TECHNICIAN', 'ADMIN') NOT NULL DEFAULT 'USER',
    trang_thai ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_role_status (vai_tro, trang_thai)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. BẢNG DEVICES (Quản lý thiết bị CNTT)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DEVICES (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    ma_thiet_bi VARCHAR(50) NOT NULL,
    ten_thiet_bi VARCHAR(150) NOT NULL,
    loai_thiet_bi VARCHAR(100) NULL,
    vi_tri VARCHAR(150) NULL,
    trang_thai ENUM(
        'ACTIVE',
        'MAINTENANCE',
        'BROKEN',
        'INACTIVE'
    ) NOT NULL DEFAULT 'ACTIVE',
    mo_ta TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_devices_code (ma_thiet_bi),
    KEY idx_devices_status (trang_thai),
    KEY idx_devices_type (loai_thiet_bi)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. BẢNG TICKETS (Quản lý yêu cầu dịch vụ / sự cố / bảo trì)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS TICKETS (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    tieu_de VARCHAR(200) NOT NULL,
    mo_ta TEXT NOT NULL,

    loai_yeu_cau ENUM(
        'INCIDENT',
        'SERVICE_REQUEST',
        'MAINTENANCE'
    ) NOT NULL DEFAULT 'INCIDENT',

    muc_do_uu_tien ENUM(
        'LOW',
        'MEDIUM',
        'HIGH',
        'URGENT'
    ) NOT NULL DEFAULT 'MEDIUM',

    trang_thai ENUM(
        'OPEN',
        'ASSIGNED',
        'IN_PROGRESS',
        'RESOLVED',
        'CLOSED'
    ) NOT NULL DEFAULT 'OPEN',

    user_id BIGINT UNSIGNED NOT NULL,
    device_id BIGINT UNSIGNED NULL,
    technician_id BIGINT UNSIGNED NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    closed_at DATETIME NULL,

    PRIMARY KEY (id),

    CONSTRAINT fk_tickets_user
        FOREIGN KEY (user_id)
        REFERENCES USERS(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_tickets_device
        FOREIGN KEY (device_id)
        REFERENCES DEVICES(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_tickets_technician
        FOREIGN KEY (technician_id)
        REFERENCES USERS(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    KEY idx_tickets_status (trang_thai),
    KEY idx_tickets_creator (user_id),
    KEY idx_tickets_device (device_id),
    KEY idx_tickets_technician (technician_id),
    KEY idx_tickets_created_at (created_at),
    KEY idx_tickets_priority_status (muc_do_uu_tien, trang_thai)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. BẢNG TICKET_HISTORY (Lịch sử xử lý & audit log)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS TICKET_HISTORY (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    ticket_id BIGINT UNSIGNED NOT NULL,
    nguoi_thuc_hien_id BIGINT UNSIGNED NULL,

    -- Đã bổ sung giá trị CLASSIFIED
    hanh_dong ENUM(
        'CREATED',
        'UPDATED',
        'CLASSIFIED',
        'ASSIGNED',
        'STATUS_CHANGED',
        'CLOSED'
    ) NOT NULL,

    trang_thai_cu ENUM(
        'OPEN',
        'ASSIGNED',
        'IN_PROGRESS',
        'RESOLVED',
        'CLOSED'
    ) NULL,

    trang_thai_moi ENUM(
        'OPEN',
        'ASSIGNED',
        'IN_PROGRESS',
        'RESOLVED',
        'CLOSED'
    ) NULL,

    chi_tiet_cap_nhat VARCHAR(500) NULL,
    thoi_gian TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    -- Đã đổi sang ON DELETE RESTRICT để bảo toàn dữ liệu lịch sử
    CONSTRAINT fk_history_ticket
        FOREIGN KEY (ticket_id)
        REFERENCES TICKETS(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_history_actor
        FOREIGN KEY (nguoi_thuc_hien_id)
        REFERENCES USERS(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    KEY idx_history_ticket_time (ticket_id, thoi_gian),
    KEY idx_history_actor (nguoi_thuc_hien_id),
    KEY idx_history_action (hanh_dong)
) ENGINE=InnoDB;