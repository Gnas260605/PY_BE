# THÔNG TIN TEST RUN — CS466 HELPDESK QA (MỤC 12.1)

| Thuộc tính | Giá trị ghi nhận |
| :--- | :--- |
| **Run ID** | `TR-20260921-01` |
| **Tester** | Antigravity QA Agent & Nhóm phát triển CS466 |
| **Ngày giờ bắt đầu** | 2026-09-21 19:44:00 +07:00 |
| **Commit Hash / Branch** | `bf51d53f57ba2e0ac537dd1b349122e3400f28c4` / `main` |
| **Hệ điều hành / Trình duyệt** | Windows 11 Pro 64-bit / Chrome & Edge hiện hành |
| **Phiên bản Python / MySQL** | Python 3.13.7 / MariaDB 10.6.16 (Tương thích MySQL 8.0) |
| **Database kiểm thử** | `cs466_helpdesk_test` (Tuân thủ nghiêm ngặt R01: hậu tố `_test`) |
| **Phạm vi kiểm thử** | Toàn diện Fullstack (Chu kỳ 0 đến 8 — 126 Test Cases) |
| **Ghi chú môi trường** | Môi trường database độc lập được cách ly; guard an toàn chặn đứng mọi DB không có hậu tố `_test`. Backend chạy FastAPI cổng 8000, Frontend chạy NiceGUI cổng 8500. |

---

## TỔNG QUAN TIẾN TRÌNH CÁC CHU KỲ (0 – 8)

- [x] **Chu kỳ 0 (Chuẩn bị & Cổng môi trường):** ĐÃ HOÀN TẤT (Môi trường DB `cs466_helpdesk_test`, Guard session conftest, cấu hình 2 file .env, thư mục evidence).
- [x] **Chu kỳ 1 (Smoke Test):** ĐÃ HOÀN TẤT (`GET /api/health` 200, 3 role đăng nhập thành công, phát hiện & fix DEF-001 K02).
- [x] **Chu kỳ 2 (Backend & MySQL Contract - 36 Endpoints & K01):** ĐÃ HOÀN TẤT (Phát hiện & vá lỗ hổng Critical DEF-002 K01, 36 API REST contracts PASS).
- [x] **Chu kỳ 3 (Frontend theo 3 Vai trò - 13 Route):** ĐÃ HOÀN TẤT (13 route giao diện được kiểm tra, fix DEF-003 K03 phím Enter composer).
- [x] **Chu kỳ 4 (Tích hợp Luồng & Workspace):** ĐÃ HOÀN TẤT (Vòng đời vé 5 bước khép kín, 5 bản ghi lịch sử, SHA-256 tệp đính kèm 100% khớp).
- [x] **Chu kỳ 5 (Bảo mật, IDOR, Injection & XSS):** ĐÃ HOÀN TẤT (Chặn IDOR, chống SQLi/XSS, zero leak `password_hash`, rate limiting).
- [x] **Chu kỳ 6 (Phi chức năng - NFR):** ĐÃ HOÀN TẤT (Đo thời gian p50/p95, p95 <= 433ms, tải nhẹ 20 request đồng thời).
- [x] **Chu kỳ 7 (Retest Defect & Regression):** ĐÃ HOÀN TẤT (Retest DEF-001, 002, 003 CLOSED; 83/83 pytest PASS, 39/39 role tests PASS).
- [x] **Chu kỳ 8 (Báo cáo Nghiệm thu & Go/No-Go):** ĐÃ HOÀN TẤT (Bàn giao Checklist 12 mục, xuất báo cáo `tests/BAO_CAO_HOAN_THANH_QA.md`, quyết định GO).
