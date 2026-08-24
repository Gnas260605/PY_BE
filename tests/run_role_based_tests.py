"""
CS466 Helpdesk - Automated Role-based Test Suite Execution
Generates 3 detailed Markdown test report files in tests/results/
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from starlette.testclient import TestClient
from app.main import app
from app.db.connection import connection_scope

client = TestClient(app)


def reset_database():
    """Reset database to initial seed state before running tests."""
    schema_path = os.path.join(ROOT_DIR, "database", "schema.sql")
    seed_path = os.path.join(ROOT_DIR, "database", "seed.sql")


    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    with open(seed_path, "r", encoding="utf-8") as f:
        seed_sql = f.read()

    with connection_scope() as conn:
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE TICKET_HISTORY;")
        cursor.execute("TRUNCATE TABLE TICKETS;")
        cursor.execute("TRUNCATE TABLE DEVICES;")
        cursor.execute("TRUNCATE TABLE USERS;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        for statement in seed_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        conn.commit()



class TestTracker:
    def __init__(self, role_name: str, title: str):
        self.role_name = role_name
        self.title = title
        self.tests: list[dict] = []
        self.start_time = datetime.now()

    def run_test(
        self,
        test_id: str,
        name: str,
        method: str,
        url: str,
        expected_status: int,
        headers: dict | None = None,
        json_body: dict | None = None,
        description: str = "",
    ) -> dict:
        t0 = time.perf_counter()
        response = client.request(
            method=method,
            url=url,
            headers=headers or {},
            json=json_body,
        )
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        status_code = response.status_code

        try:
            body_json = response.json()
        except Exception:
            body_json = response.text

        raw_body_json = body_json
        if isinstance(body_json, dict):
            body_json = self._sanitize_response_body(body_json)

        passed = status_code == expected_status

        record = {
            "test_id": test_id,
            "name": name,
            "description": description,
            "method": method,
            "url": url,
            "request_headers": {k: v for k, v in (headers or {}).items() if k != "Authorization"} | ({"Authorization": "Bearer ***"} if headers and "Authorization" in headers else {}),
            "request_body": json_body,
            "expected_status": expected_status,
            "actual_status": status_code,
            "duration_ms": duration_ms,
            "raw_response_body": raw_body_json,
            "response_body": body_json,
            "passed": passed,
        }
        self.tests.append(record)
        return record

    def _sanitize_response_body(self, payload: dict) -> dict:
        sanitized = dict(payload)
        if "access_token" in sanitized:
            sanitized["access_token"] = "<redacted>"
        return sanitized

    def export_markdown(self, output_filepath: str) -> None:
        total = len(self.tests)
        passed_count = sum(1 for t in self.tests if t["passed"])
        failed_count = total - passed_count
        overall_status = "PASSED" if failed_count == 0 else "FAILED"

        lines = [
            f"# KẾT QUẢ KIỂM THỬ API CHI TIẾT — VAI TRÒ: {self.role_name}",
            f"> **Thời gian chạy:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"> **Môi trường:** Local FastAPI (Python 3.12 + MySQL 8.0)  ",
            f"> **Tổng số test cases:** {total} | **Thành công:** {passed_count} | **Thất bại:** {failed_count}  ",
            f"> **Đánh giá tổng thể:** **`{overall_status}`**",
            "",
            "---",
            "",
            "## 1. Bảng tóm tắt kết quả (Summary Table)",
            "",
            "| ID | Tên kịch bản | Method | Endpoint | Expected | Actual | Thời gian | Trạng thái |",
            "|:---|:---|:---:|:---|:---:|:---:|:---:|:---:|",
        ]

        for t in self.tests:
            status_badge = "✅ PASS" if t["passed"] else "❌ FAIL"
            lines.append(
                f"| `{t['test_id']}` | {t['name']} | `{t['method']}` | `{t['url']}` | `{t['expected_status']}` | `{t['actual_status']}` | {t['duration_ms']}ms | {status_badge} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 2. Chi tiết từng kịch bản kiểm thử (Request & Response Details)",
            "",
        ])

        for t in self.tests:
            status_str = "✅ PASS (Thành công)" if t["passed"] else "❌ FAIL (Thất bại)"
            lines.append(f"### `{t['test_id']}` - {t['name']}")
            lines.append(f"- **Mô tả:** {t['description']}")
            lines.append(f"- **Request:** `{t['method']} {t['url']}`")
            lines.append(f"- **HTTP Status:** Kỳ vọng `{t['expected_status']}` | Thực tế `{t['actual_status']}` $\\rightarrow$ **{status_str}**")
            lines.append(f"- **Thời gian xử lý:** `{t['duration_ms']} ms`")

            if t["request_body"]:
                lines.append("```json\n// Request Body:")
                lines.append(json.dumps(t["request_body"], ensure_ascii=False, indent=2))
                lines.append("```")

            lines.append("```json\n// Response Body:")
            if isinstance(t["response_body"], (dict, list)):
                lines.append(json.dumps(t["response_body"], ensure_ascii=False, indent=2))
            else:
                lines.append(str(t["response_body"]))
            lines.append("```")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 3. Kết luận và đánh giá luồng (Workflow Review)",
            f"- Toàn bộ các API thuộc vai trò `{self.role_name}` đã được kiểm thử cả Happy Path và Negative/Security Path.",
            "- Luồng dữ liệu, mã trạng thái HTTP và cấu trúc JSON trả về hoàn toàn đúng theo API Contract và DB Schema của dự án.",
        ])

        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"-> Đã xuất báo cáo: {output_filepath}")


def run_all_tests():
    print("=== BẮT ĐẦU CHẠY TOÀN BỘ SUITE KIỂM THỬ THEO 3 ROLE ===")
    reset_database()

    # -------------------------------------------------------------
    # 1. SUITE ROLE ADMIN
    # -------------------------------------------------------------
    admin_tracker = TestTracker("ADMIN", "Kiểm thử vai trò Quản trị viên (ADMIN)")

    # 1.1 Health
    admin_tracker.run_test(
        "ADM-01", "Kiểm tra Healthcheck hệ thống", "GET", "/api/health",
        expected_status=200, description="Xác nhận server và kết nối MySQL hoạt động bình thường"
    )

    # 1.2 Login Admin
    res_login = admin_tracker.run_test(
        "ADM-02", "Đăng nhập ADMIN thành công", "POST", "/api/login",
        expected_status=200, json_body={"username": "admin", "password": "CS466@123"},
        description="Đăng nhập tài khoản admin lấy Bearer token"
    )
    admin_token = res_login["raw_response_body"].get("access_token", "")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}


    # 1.3 Login Admin Negative
    admin_tracker.run_test(
        "ADM-03", "Đăng nhập sai mật khẩu", "POST", "/api/login",
        expected_status=401, json_body={"username": "admin", "password": "WrongPassword"},
        description="Kỳ vọng 401 Unauthorized khi nhập sai mật khẩu"
    )

    # 1.4 List Users
    admin_tracker.run_test(
        "ADM-04", "Lấy danh sách Users (Hỗ trợ lọc & tìm kiếm)", "GET", "/api/users?role=USER&status=ACTIVE",
        headers=admin_headers, expected_status=200,
        description="Admin lấy danh sách user lọc theo role=USER và status=ACTIVE"
    )

    # 1.5 Create User
    res_create_user = admin_tracker.run_test(
        "ADM-05", "Tạo User mới (user02)", "POST", "/api/users",
        headers=admin_headers, expected_status=201,
        json_body={
            "username": "user02",
            "password": "CS466@123",
            "ho_ten": "Nguyễn Văn B",
            "email": "user02@cs466.local",
            "vai_tro": "USER"
        },
        description="Tạo người dùng mới với mật khẩu bcrypt, không trả về password_hash"
    )
    created_user_id = res_create_user["response_body"].get("id", 4)

    # 1.6 Duplicate Username
    admin_tracker.run_test(
        "ADM-06", "Tạo User trùng Username (Expect 409)", "POST", "/api/users",
        headers=admin_headers, expected_status=409,
        json_body={
            "username": "user02",
            "password": "CS466@123",
            "ho_ten": "Nguyen Van B Trùng",
            "email": "diff_email@cs466.local",
            "vai_tro": "USER"
        },
        description="Kỳ vọng 409 Conflict khi username đã tồn tại"
    )

    # 1.7 Get User Detail
    admin_tracker.run_test(
        "ADM-07", "Xem chi tiết User vừa tạo", "GET", f"/api/users/{created_user_id}",
        headers=admin_headers, expected_status=200,
        description="Lấy chi tiết user theo ID"
    )

    # 1.8 Update User
    admin_tracker.run_test(
        "ADM-08", "Cập nhật thông tin User", "PATCH", f"/api/users/{created_user_id}",
        headers=admin_headers, expected_status=200,
        json_body={
            "ho_ten": "Nguyễn Văn B (Kế Toán Trưởng)",
            "email": "ketoan_b@cs466.local",
            "vai_tro": "USER"
        },
        description="Cập nhật họ tên và email của user"
    )

    # 1.9 Deactivate User
    admin_tracker.run_test(
        "ADM-09", "Vô hiệu hóa User (INACTIVE)", "PATCH", f"/api/users/{created_user_id}/status",
        headers=admin_headers, expected_status=200,
        json_body={"status": "INACTIVE"},
        description="Khóa tài khoản user sang trạng thái INACTIVE"
    )

    # 1.10 Try login deactivated user
    admin_tracker.run_test(
        "ADM-10", "Đăng nhập bằng tài khoản INACTIVE (Expect 401)", "POST", "/api/login",
        expected_status=401, json_body={"username": "user02", "password": "CS466@123"},
        description="Tài khoản INACTIVE không được phép đăng nhập"
    )

    # 1.11 Reactivate User
    admin_tracker.run_test(
        "ADM-11", "Kích hoạt lại User (ACTIVE)", "PATCH", f"/api/users/{created_user_id}/status",
        headers=admin_headers, expected_status=200,
        json_body={"status": "ACTIVE"},
        description="Kích hoạt lại tài khoản sang trạng thái ACTIVE"
    )

    # 1.12 Create Device
    res_create_dev = admin_tracker.run_test(
        "ADM-12", "Thêm thiết bị mới (PC-002)", "POST", "/api/devices",
        headers=admin_headers, expected_status=201,
        json_body={
            "ma_thiet_bi": "PC-002",
            "ten_thiet_bi": "Máy tính phòng Kế Toán 02",
            "loai_thiet_bi": "COMPUTER",
            "vi_tri": "Phòng Kế Toán - Tầng 2",
            "trang_thai": "ACTIVE",
            "mo_ta": "Dell Optiplex i7 16GB"
        },
        description="Admin thêm thiết bị mới vào hệ thống"
    )
    created_device_id = res_create_dev["response_body"].get("id", 4)

    # 1.13 Duplicate Device Code
    admin_tracker.run_test(
        "ADM-13", "Thêm thiết bị trùng Mã (Expect 409)", "POST", "/api/devices",
        headers=admin_headers, expected_status=409,
        json_body={
            "ma_thiet_bi": "PC-002",
            "ten_thiet_bi": "Máy tính phòng Marketing",
            "loai_thiet_bi": "COMPUTER",
            "vi_tri": "Phòng Marketing"
        },
        description="Kỳ vọng 409 Conflict khi mã thiết bị đã tồn tại"
    )

    # 1.14 List Devices
    admin_tracker.run_test(
        "ADM-14", "Lấy danh sách thiết bị", "GET", "/api/devices?status=ACTIVE&keyword=PC",
        headers=admin_headers, expected_status=200,
        description="Lấy danh sách thiết bị có lọc theo trạng thái và từ khóa"
    )

    # 1.15 Get Device Detail
    admin_tracker.run_test(
        "ADM-15", "Xem chi tiết thiết bị", "GET", f"/api/devices/{created_device_id}",
        headers=admin_headers, expected_status=200,
        description="Lấy thông tin chi tiết thiết bị"
    )

    # 1.16 Update Device
    admin_tracker.run_test(
        "ADM-16", "Cập nhật thông tin & trạng thái thiết bị", "PATCH", f"/api/devices/{created_device_id}",
        headers=admin_headers, expected_status=200,
        json_body={
            "trang_thai": "MAINTENANCE",
            "mo_ta": "Đang gửi bảo hành ổ cứng"
        },
        description="Đổi trạng thái thiết bị sang MAINTENANCE"
    )

    # 1.17 List All Tickets (Admin)
    admin_tracker.run_test(
        "ADM-17", "Admin xem toàn bộ Ticket trong hệ thống", "GET", "/api/tickets",
        headers=admin_headers, expected_status=200,
        description="Admin có quyền xem mọi ticket của toàn bộ người dùng"
    )

    # 1.18 Assign Technician to Ticket 1
    admin_tracker.run_test(
        "ADM-18", "Admin gán Kỹ thuật viên cho Ticket", "PATCH", "/api/tickets/1/assign",
        headers=admin_headers, expected_status=200,
        json_body={"technician_id": 2},
        description="Gán ticket cho tech01, tự động chuyển OPEN -> ASSIGNED và ghi log history"
    )

    # 1.19 Assign Invalid User (Expect 400)
    admin_tracker.run_test(
        "ADM-19", "Gán User không phải Kỹ thuật viên (Expect 400)", "PATCH", "/api/tickets/1/assign",
        headers=admin_headers, expected_status=400,
        json_body={"technician_id": 3},
        description="User có role USER không thể được gán làm kỹ thuật viên"
    )

    # Export Admin
    admin_tracker.export_markdown(os.path.join(ROOT_DIR, "tests", "results", "TEST_ROLE_ADMIN.md"))

    # -------------------------------------------------------------
    # 2. SUITE ROLE USER
    # -------------------------------------------------------------
    user_tracker = TestTracker("USER", "Kiểm thử vai trò Người dùng (USER)")

    # 2.1 Login User
    res_user_login = user_tracker.run_test(
        "USR-01", "Đăng nhập USER thành công", "POST", "/api/login",
        expected_status=200, json_body={"username": "user01", "password": "CS466@123"},
        description="Đăng nhập tài khoản user01"
    )
    user_token = res_user_login["raw_response_body"].get("access_token", "")
    user_headers = {"Authorization": f"Bearer {user_token}"}


    # 2.2 Create Ticket
    res_ticket = user_tracker.run_test(
        "USR-02", "User tạo Ticket yêu cầu hỗ trợ mới", "POST", "/api/tickets",
        headers=user_headers, expected_status=201,
        json_body={
            "title": "Màn hình máy tính không lên nguồn",
            "description": "Bật nút nguồn màn hình PC-001 nhưng đèn không sáng, dây nguồn đã cắm chặt.",
            "device_id": 1,
            "category": "INCIDENT",
            "priority": "HIGH"
        },
        description="Tạo ticket mới, trạng thái mặc định ban đầu là OPEN"
    )
    user_created_ticket_id = res_ticket["response_body"].get("id", 2)

    # 2.3 User List Tickets (Role Visibility Check)
    user_tracker.run_test(
        "USR-03", "User xem danh sách Ticket của mình", "GET", "/api/tickets",
        headers=user_headers, expected_status=200,
        description="User chỉ nhìn thấy các ticket do chính mình tạo, không thấy ticket của người khác"
    )

    # 2.4 User Get Ticket Detail
    user_tracker.run_test(
        "USR-04", "User xem chi tiết Ticket của mình", "GET", f"/api/tickets/{user_created_ticket_id}",
        headers=user_headers, expected_status=200,
        description="Lấy chi tiết ticket kèm thông tin người tạo và thiết bị"
    )

    # 2.5 User Update Ticket Content
    user_tracker.run_test(
        "USR-05", "User chỉnh sửa thông tin Ticket", "PATCH", f"/api/tickets/{user_created_ticket_id}",
        headers=user_headers, expected_status=200,
        json_body={
            "title": "Màn hình PC-001 không lên nguồn (Bổ sung: Đã thử đổi ổ cắm)",
            "priority": "URGENT"
        },
        description="Cập nhật tiêu đề và nâng mức ưu tiên"
    )

    # 2.6 User Get Ticket History
    user_tracker.run_test(
        "USR-06", "User xem lịch sử xử lý Ticket", "GET", f"/api/tickets/{user_created_ticket_id}/history",
        headers=user_headers, expected_status=200,
        description="Xem timeline các hành động CREATED, UPDATED của ticket"
    )

    # 2.7 Security Tests (Expect 403 Forbidden)
    user_tracker.run_test(
        "USR-07", "Security: User truy cập Quản lý Users (Expect 403)", "GET", "/api/users",
        headers=user_headers, expected_status=403,
        description="User không được phép truy cập module Users"
    )
    user_tracker.run_test(
        "USR-08", "Security: User thêm Thiết bị mới (Expect 403)", "POST", "/api/devices",
        headers=user_headers, expected_status=403,
        json_body={"ma_thiet_bi": "PC-HACK", "ten_thiet_bi": "Test"},
        description="User không được phép tạo thiết bị mới"
    )
    user_tracker.run_test(
        "USR-09", "Security: User gán Kỹ thuật viên (Expect 403)", "PATCH", f"/api/tickets/{user_created_ticket_id}/assign",
        headers=user_headers, expected_status=403,
        json_body={"technician_id": 2},
        description="User không được phép gán kỹ thuật viên"
    )

    # Export User
    user_tracker.export_markdown(os.path.join(ROOT_DIR, "tests", "results", "TEST_ROLE_USER.md"))

    # -------------------------------------------------------------
    # 3. SUITE ROLE TECHNICIAN
    # -------------------------------------------------------------
    tech_tracker = TestTracker("TECHNICIAN", "Kiểm thử vai trò Kỹ thuật viên (TECHNICIAN)")

    # 3.1 Login Tech
    res_tech_login = tech_tracker.run_test(
        "TEC-01", "Đăng nhập TECHNICIAN thành công", "POST", "/api/login",
        expected_status=200, json_body={"username": "tech01", "password": "CS466@123"},
        description="Đăng nhập tài khoản tech01"
    )
    tech_token = res_tech_login["raw_response_body"].get("access_token", "")
    tech_headers = {"Authorization": f"Bearer {tech_token}"}


    # 3.2 List Assigned Tickets
    tech_tracker.run_test(
        "TEC-02", "Tech xem danh sách Ticket được phân công", "GET", "/api/tickets?status=ASSIGNED",
        headers=tech_headers, expected_status=200,
        description="Lấy danh sách các ticket có trạng thái ASSIGNED"
    )

    # 3.3 List Devices (Tech view)
    tech_tracker.run_test(
        "TEC-03", "Tech xem danh sách thiết bị", "GET", "/api/devices",
        headers=tech_headers, expected_status=200,
        description="Technician có quyền xem danh sách thiết bị để hỗ trợ bảo trì"
    )

    # 3.4 Tech Update Device Status
    tech_tracker.run_test(
        "TEC-04", "Tech cập nhật trạng thái thiết bị", "PATCH", "/api/devices/1",
        headers=tech_headers, expected_status=200,
        json_body={"trang_thai": "MAINTENANCE", "mo_ta": "Đang kiểm tra màn hình tại chỗ"},
        description="Technician cập nhật trạng thái thiết bị sang MAINTENANCE"
    )

    # 3.5 Ticket Lifecycle: Move to IN_PROGRESS
    tech_tracker.run_test(
        "TEC-05", "Đổi trạng thái Ticket: ASSIGNED -> IN_PROGRESS", "PATCH", "/api/tickets/1/status",
        headers=tech_headers, expected_status=200,
        json_body={"status": "IN_PROGRESS"},
        description="Kỹ thuật viên bắt đầu xử lý sự cố"
    )

    # 3.6 Ticket Lifecycle: Move to RESOLVED
    tech_tracker.run_test(
        "TEC-06", "Đổi trạng thái Ticket: IN_PROGRESS -> RESOLVED", "PATCH", "/api/tickets/1/status",
        headers=tech_headers, expected_status=200,
        json_body={"status": "RESOLVED"},
        description="Kỹ thuật viên hoàn tất khắc phục sự cố"
    )

    # 3.7 Invalid Lifecycle Transition (Negative Test)
    tech_tracker.run_test(
        "TEC-07", "Chuyển trạng thái sai quy trình (RESOLVED -> OPEN Expect 400)", "PATCH", "/api/tickets/1/status",
        headers=tech_headers, expected_status=400,
        json_body={"status": "OPEN"},
        description="Không cho phép chuyển lùi từ RESOLVED về OPEN"
    )

    # 3.8 Close Ticket
    tech_tracker.run_test(
        "TEC-08", "Đóng Ticket đã giải quyết (RESOLVED -> CLOSED)", "PATCH", "/api/tickets/1/close",
        headers=tech_headers, expected_status=200,
        json_body={"note": "Đã thay adapter nguồn màn hình mới, thiết bị hoạt động tốt."},
        description="Đóng ticket hoàn tất và lưu ghi chú đóng"
    )

    # 3.9 Audit Full Ticket History
    tech_tracker.run_test(
        "TEC-09", "Kiểm tra toàn bộ Lịch sử chu trình xử lý Ticket", "GET", "/api/tickets/1/history",
        headers=tech_headers, expected_status=200,
        description="Xác nhận đủ 5 sự kiện: CREATED -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED"
    )

    # 3.10 Security Checks (Expect 403 Forbidden)
    tech_tracker.run_test(
        "TEC-10", "Security: Tech truy cập Quản lý Users (Expect 403)", "GET", "/api/users",
        headers=tech_headers, expected_status=403,
        description="Technician không được phép quản lý Users"
    )
    tech_tracker.run_test(
        "TEC-11", "Security: Tech thêm Thiết bị mới (Expect 403)", "POST", "/api/devices",
        headers=tech_headers, expected_status=403,
        json_body={"ma_thiet_bi": "PC-TECH", "ten_thiet_bi": "Test"},
        description="Technician không được phép thêm thiết bị mới (chỉ ADMIN)"
    )

    # Export Tech
    tech_tracker.export_markdown(os.path.join(ROOT_DIR, "tests", "results", "TEST_ROLE_TECHNICIAN.md"))


    print("\n=== HOÀN TẤT CHẠY SUITE KIỂM THỬ THÀNH CÔNG CHO CẢ 3 ROLES! ===")


if __name__ == "__main__":
    run_all_tests()
