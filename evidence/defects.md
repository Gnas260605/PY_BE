# SỔ THEO DÕI KHIẾM KHUYẾT (DEFECT LOG) — CS466 HELPDESK
### Tuân thủ chuẩn 10 trường bắt buộc (Mục 7.3 tài liệu gốc)
> **Vòng đời Defect (Mục 7.2):** `NEW` $\to$ `TRIAGED` $\to$ `IN PROGRESS` $\to$ `READY FOR RETEST` $\to$ `CLOSED` / `REOPENED` / `DEFERRED`  
> **Quy tắc che bằng chứng (R11):** Không ghi mật khẩu, raw JWT, secret hoặc thông tin nhạy cảm vào bằng chứng.

---

## DANH SÁCH DEFECTS

### [DEF-001] [AUTH][High] Nút đăng nhập nhanh Admin (1-Click Demo) dùng sai mật khẩu Admin@123 thay vì CS466@123
1. **Tiêu đề:** `[AUTH][High]` Nút đăng nhập nhanh Admin (1-Click Demo) điền sai mật khẩu `Admin@123` dẫn đến đăng nhập thất bại 401
2. **Baseline:** Commit `bf51d53f57ba2e0ac537dd1b349122e3400f28c4`, nhánh `main`, 2026-09-21, Windows 11, Chrome/Edge, DB `cs466_helpdesk_test`
3. **Precondition:** Đang ở màn hình đăng nhập `/login`, tài khoản `admin` trong seed database có mật khẩu là `CS466@123`
4. **Steps to Reproduce:**
   1. Truy cập giao diện đăng nhập tại `http://127.0.0.1:8500/login`
   2. Tại khu vực "TÀI KHOẢN TRẢI NGHIỆM DEMO (1-CLICK)", bấm nút "Admin"
   3. Quan sát ô mật khẩu tự động điền `Admin@123`
   4. Bấm nút "Đăng nhập"
5. **Expected:** Nút 1-click điền đúng mật khẩu seed `CS466@123`, đăng nhập thành công vào vai trò ADMIN và điều hướng tới `/dashboard`
6. **Actual:** Đăng nhập thất bại với mã lỗi HTTP 401 `INVALID_CREDENTIALS` do mật khẩu được gán cứng là `Admin@123`
7. **Evidence:** `frontend/views/auth/login_view.py:331` (`demo_configs` khai báo `("Admin", "admin", "Admin@123", ...)`)
8. **Frequency:** 3/3 lần thử (100% tái hiện)
9. **Severity / Priority:** High / P1 (Xác minh chính xác Rủi ro mã nguồn K02)
10. **Links:** Case ID `AUTH-01`, Risk `K02`, file [frontend/views/auth/login_view.py:331](file:///d:/pyhton/frontend/views/auth/login_view.py#L331)
* **Trạng thái xử lý:** `CLOSED` (Đã sửa giá trị mật khẩu thành `CS466@123`, retest thành công đăng nhập Admin HTTP 200).

---

### [DEF-002] [USR/SEC][Critical] Lỗ hổng Leo Quyền (Privilege Escalation): User thường có thể tự đổi vai trò thành ADMIN qua PATCH /api/users/{id}
1. **Tiêu đề:** `[USR/SEC][Critical]` Lỗ hổng Leo Quyền Nghiêm trọng: Tài khoản USER tự nâng quyền thành ADMIN thông qua endpoint `PATCH /api/users/{id}`
2. **Baseline:** Commit `bf51d53f57ba2e0ac537dd1b349122e3400f28c4`, nhánh `main`, 2026-09-21, Windows 11, Chrome/Edge, DB `cs466_helpdesk_test`
3. **Precondition:** Tài khoản `user01` có vai trò `USER` (`id=3`), trạng thái `ACTIVE`, sở hữu JWT token hợp lệ
4. **Steps to Reproduce:**
   1. Sử dụng JWT token của `user01` gắn vào header `Authorization: Bearer <token>`
   2. Gửi request `PATCH http://127.0.0.1:8000/api/users/3` với body JSON: `{"vai_tro": "ADMIN"}`
   3. Quan sát HTTP response status và body trả về
   4. Kiểm tra trực tiếp bảng `USERS` trong MySQL: `SELECT id, username, vai_tro FROM USERS WHERE id=3;`
5. **Expected:** Backend bắt buộc phải từ chối `403 FORBIDDEN` hoặc loại bỏ trường `vai_tro` khỏi payload cập nhật của người dùng không phải ADMIN. Vai trò của tài khoản trong MySQL phải được giữ nguyên là `USER` (theo USR-11, SEC-04)
6. **Actual:** Backend trả về HTTP `200 OK`, log ghi nhận `USER_UPDATED user_id=3 fields=vai_tro`, bảng `USERS` trong MySQL bị cập nhật `vai_tro = 'ADMIN'`. Người dùng chiếm toàn quyền quản trị hệ thống.
7. **Evidence:** 
   - Backend log: `INFO app.users.service USER_UPDATED user_id=3 fields=vai_tro`
   - Response: `HTTP 200 OK`, JSON trả về `{"id": 3, "username": "user01", "vai_tro": "ADMIN", ...}`
   - MySQL state: Record `(3, 'user01', 'ADMIN')`
8. **Frequency:** 3/3 lần thử (100% tái hiện)
9. **Severity / Priority:** **Critical / P0 (CHẶN PHÁT HÀNH — QUY TẮC R20)**
10. **Links:** Case ID `USR-11`, `SEC-04`, Risk `K01`, files [backend/app/users/routes.py:55](file:///d:/pyhton/backend/app/users/routes.py#L55), [backend/app/users/schemas.py:116](file:///d:/pyhton/backend/app/users/schemas.py#L116), [backend/app/users/service.py:127](file:///d:/pyhton/backend/app/users/service.py#L127)
* **Trạng thái xử lý:** `CLOSED` (Đã thêm kiểm tra chặn người dùng không phải ADMIN gửi trường `vai_tro`, trả về `403 FORBIDDEN`; đã retest thành công và chạy đầy đủ bộ regression Auth/User).

---

### [DEF-003] [COL][Medium] Composer bình luận thiếu xử lý phím Enter gửi tin và Shift+Enter xuống dòng
1. **Tiêu đề:** `[COL][Medium]` Composer bình luận hiển thị hướng dẫn "(Enter để gửi, Shift+Enter xuống dòng)" nhưng thiếu event handler phím Enter
2. **Baseline:** Commit `bf51d53f57ba2e0ac537dd1b349122e3400f28c4`, nhánh `main`, 2026-09-21, Windows 11, Chrome/Edge, DB `cs466_helpdesk_test`
3. **Precondition:** Đang mở Ticket Workspace bất kỳ (`/tickets/{id}`), có khu vực trao đổi `comments_thread`
4. **Steps to Reproduce:**
   1. Nhập văn bản vào ô "Nhập nội dung trao đổi..."
   2. Bấm phím `Enter` trên bàn phím
5. **Expected:** Phím `Enter` gửi bình luận ngay lập tức; phím `Shift+Enter` tạo dòng mới (theo COL-04, K03).
6. **Actual:** Phím `Enter` chỉ tạo dòng mới (xuống dòng), không gửi tin nhắn. Người dùng bắt buộc phải dùng chuột bấm nút "Gửi".
7. **Evidence:** `frontend/common/components/comments_thread.py:100` (`ui.textarea` không có handler `.on("keydown.enter.exact.prevent", ...)`)
8. **Frequency:** 3/3 lần thử (100% tái hiện)
9. **Severity / Priority:** Medium / P2 (Xác minh chính xác Rủi ro mã nguồn K03)
10. **Links:** Case ID `COL-04`, Risk `K03`, file [frontend/common/components/comments_thread.py](file:///d:/pyhton/frontend/common/components/comments_thread.py)
* **Trạng thái xử lý:** `CLOSED` (Đã gắn listener `.on("keydown.enter.exact.prevent", send_comment)` vào `ui.textarea`, retest hoạt động chính xác).

---

### [DEF-004] [SET][Low] Tùy chọn Theme và Mật độ bảng trong Settings chưa được lưu trữ bền vững (Persistent Storage)
1. **Tiêu đề:** `[SET][Low]` Thay đổi Theme (Light/Dark/Auto) và Mật độ bảng (Density) chỉ lưu trong state bộ nhớ phiên làm việc, bị reset sau khi F5 refresh
2. **Baseline:** Commit `bf51d53f57ba2e0ac537dd1b349122e3400f28c4`, nhánh `main`, 2026-09-21, Windows 11, Chrome/Edge, DB `cs466_helpdesk_test`
3. **Precondition:** Người dùng đăng nhập hệ thống, truy cập màn hình Cài đặt `/settings`
4. **Steps to Reproduce:**
   1. Vào tab "Giao diện & Hiển thị"
   2. Chọn theme "Giao diện Tối (Dark)" hoặc đổi Mật độ bảng
   3. Nhấn F5 làm mới trình duyệt (Browser Refresh)
5. **Expected:** Cấu hình theme/mật độ được duy trì qua các lần tải lại trang hoặc đăng nhập lại.
6. **Actual:** Giao diện quay trở lại giá trị mặc định (Light theme) do state chỉ nằm trong in-memory dict của phiên NiceGUI.
7. **Evidence:** `frontend/views/user/settings_view.py:33` (khởi tạo `state["selected_theme"] = "light"`, không đọc từ `app.storage.user`)
8. **Frequency:** 3/3 lần thử (100% tái hiện)
9. **Severity / Priority:** Low / P3 (Xác minh chính xác Rủi ro mã nguồn K04, Quyết định D12)
10. **Links:** Case ID `SET-05`, `SET-06`, Risk `K04`, Decision `D12`, file [frontend/views/user/settings_view.py](file:///d:/pyhton/frontend/views/user/settings_view.py)
* **Trạng thái xử lý:** `DEFERRED` (Tuân theo Quyết định D12: Chấp nhận lưu in-memory cho phiên bản v1.0, đưa vào backlog cải tiến lưu trữ persistent `app.storage.user` ở Sprint tiếp theo).
