# KẾ HOẠCH THỰC THI KIỂM THỬ TOÀN DIỆN HỆ THỐNG CS466 HELPDESK (v2)
### Bám sát tài liệu gốc: `CS466_Fullstack_FE_BE_Test_Plan.docx` (Mã: `CS466-QA-FTP-001`, v1.0)
> **Nguyên tắc ưu tiên (R09):** Khi kế hoạch này và tài liệu gốc mâu thuẫn, **tài liệu gốc thắng**. Kế hoạch chỉ quyết định *cách chạy*, không tự ý thay đổi *kết quả mong đợi*.  
> **Commit kiểm thử (R03):** Lấy động từ `git rev-parse HEAD` tại thời điểm mở Test Run; baseline `bf51d53f57ba2e0ac537dd1b349122e3400f28c4` dùng để đối chiếu.  
> **Database an toàn bắt buộc (R01):** Chỉ ghi/xóa/reset trên database có hậu tố `_test` (cụ thể: `cs466_helpdesk_test`).  
> **Phạm vi kiểm thử:** 13 route giao diện, 36 REST endpoint + 1 WebSocket, 6 bảng MySQL, **126 test cases**, 8 rủi ro sơ bộ K01–K08, thực thi theo **9 chu kỳ (0–8)**.

---

## 0. ĐIỂM KHÁC BIỆT VÀ HIỆU CHỈNH CHUẨN XÁC SO VỚI BẢN CŨ

| Nội dung | Bản kế hoạch cũ (v1) | Bản kế hoạch chuẩn hóa (v2) |
| :--- | :--- | :--- |
| **Chu kỳ thực thi** | "8 chu kỳ", 6 giai đoạn gộp | **9 chu kỳ (Chu kỳ 0 đến 8)** đúng theo Mục 8 tài liệu gốc |
| **Trường của Defect** | "15 trường" | **10 trường bắt buộc** theo Mục 7.3 tài liệu gốc |
| **Commit Baseline** | Hard-code tĩnh `bf51d53…` | `git rev-parse HEAD` ghi động vào Test Run; `bf51d53…` đối chiếu (R03) |
| **Câu hỏi chặn (Contract)** | Ghi "Không có câu hỏi chặn" | **15 quyết định contract (D01–D15)** cần chốt trước Chu kỳ 2 |
| **Phạm vi xác minh** | Chủ yếu assert ở tầng API | **Truy vết 3 lớp bắt buộc** (UI, API, MySQL/History/Attachments) cho mọi case đổi dữ liệu (R05, R06, Mục 3.1) |
| **Realtime WebSocket** | Bỏ sót kiểm thử WebSocket | Có kiểm thử chuyên biệt `test_websocket.py` (WS-01) |
| **Bao phủ Test Case** | Thiếu ~25 test cases | **Ma trận 126 test cases đầy đủ**, rõ phương pháp và chu kỳ |
| **Xử lý rủi ro K01** | Ghi "fix ngay" (sai quy trình QA) | Tuân thủ R20: **Tái hiện $\to$ Dừng $\to$ Báo trưởng nhóm $\to$ Chờ duyệt $\to$ Dev fix $\to$ Tester retest** |
| **Bằng chứng & Nhật ký** | Chưa quy định file bằng chứng | Có cấu trúc `evidence/results.csv`, `evidence/defects.md`, chuẩn tên file theo Mục 7.4, 12.1, 12.2, 12.4 |
| **Phân quyền Route FE** | Đếm sai số trang theo role | Ma trận phân quyền chuẩn **13 route $\times$ 4 vai trò** (Mục 6) |

---

## 1. BẢY NGUYÊN TẮC VẬN HÀNH BẮT BUỘC

1. **Nguyên tắc 3 lớp cho mọi ca thay đổi dữ liệu (R05, R06, Mục 3.1):** Một ca test chỉ được ghi nhận `PASS` khi cả 3 tầng cùng nhất quán:
   - *Lớp 1 (Giao diện):* Hiển thị đúng kết quả, trạng thái loading, toast/thông báo lỗi và phân quyền nút bấm.
   - *Lớp 2 (API backend):* Trả về đúng HTTP status, JSON schema, headers và tuyệt đối không rò rỉ dữ liệu ngoài quyền.
   - *Lớp 3 (Cơ sở dữ liệu):* Bảng nghiệp vụ (`USERS`, `DEVICES`, `TICKETS`) và các bảng nhật ký (`TICKET_HISTORY`, `TICKET_COMMENTS`, `TICKET_ATTACHMENTS`) lưu đúng tác động cuối cùng.
   - *Tuyệt đối không ghi PASS chỉ vì thấy toast UI đổi hoặc chỉ vì HTTP 200.*
2. **Chỉ ghi/xóa/reset trên Database `_test` (R01, R23):** Bắt buộc có cơ chế guard chặn cứng cấp session trong test runner và conftest.
3. **Không sửa Expected Result sau khi thấy Actual Result (R09):** Expected lấy từ tài liệu gốc. Nếu contract thay đổi, phải có văn bản phê duyệt của trưởng nhóm. Case phụ thuộc contract chưa rõ phải ghi `BLOCKED`, không tự đoán.
4. **Bốn trạng thái ca test duy nhất (R24):** Chỉ gồm `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`. Lỗi môi trường, thiếu công cụ, DB ngắt là `BLOCKED`, không ghi nhận thành `FAIL` chức năng (R19).
5. **Kiểm tra song song UI và API trực tiếp (R14, R08):** Workflow phải kiểm tra bằng cả nút bấm UI và gọi API trực tiếp. Route FE hạn chế phải test cả 3 đường: menu, nhập URL trực tiếp trên thanh địa chỉ, và gọi endpoint API tương ứng.
6. **Chuẩn hóa đặt tên và làm sạch bằng chứng (R11, Mục 7.4):** Đặt tên tệp: `YYYYMMDD_CASEID_ROLE_MO-TA.ext`. Tuyệt đối che giấu token, password, secret key và thông tin nhạy cảm.
7. **Quy trình đóng Bug nghiêm ngặt (R12, Mục 8.1):** Mỗi defect fix chỉ được đóng sau khi retest ca gốc thành công VÀ chạy đủ bộ kiểm thử hồi quy (regression) của module tương ứng.

---

## 2. DANH MỤC 15 QUYẾT ĐỊNH CONTRACT CẦN CHỐT (D01 – D15)

Trước khi bắt đầu Chu kỳ 2, cần văn bản chốt rõ các điểm "theo contract" dưới đây. Mọi ca test liên quan giữ trạng thái `BLOCKED` cho đến khi có quyết định chính thức:

| Mã | Quyết định Contract cần chốt | Test Cases bị ảnh hưởng |
| :--- | :--- | :--- |
| **D01** | `POST /api/register` là public hay bị giới hạn? Vai trò gán mặc định cho user đăng ký mới là gì? | AUTH, SEC-02 |
| **D02** | Quyền hạn và định dạng xuất của `export-tickets`, `export-tickets-excel`, `export-dashboard-pdf` theo từng role? | RPT-04–08 |
| **D03** | `PATCH /tickets/{id}/close`: Những role nào được phép gọi? Khác biệt thế nào so với `PATCH /status` đặt sang `CLOSED`? | TKT-18, TKT-19 |
| **D04** | Hành vi `batch-assign` / `batch-status` khi danh sách có ID sai/không hợp lệ: rollback toàn bộ (atomic) hay xử lý một phần (partial)? Response thông báo thế nào? | TKT-22, TKT-23 |
| **D05** | Sau khi đổi mật khẩu thành công, các token/session JWT hiện tại còn hiệu lực không hay bị thu hồi ngay? | AUTH-11, SET-12 |
| **D06** | Chủ sở hữu (User) được phép sửa những trường nào ở từng trạng thái của ticket? Việc sửa này có ghi bản ghi vào `TICKET_HISTORY` không? | TKT-12, TKT-13 |
| **D07** | Khi truy cập ticket, comment, attachment của người khác: trả về `403 Forbidden` hay `404 Not Found` (để tránh rò rỉ sự tồn tại của tài nguyên)? | TKT-11, COL-06, SEC-03 |
| **D08** | Chính chủ được phép `PATCH /users/{id}` những trường nào? Khi gửi kèm trường `vai_tro` thì server bỏ qua trường này hay trả lỗi 403? | USR-07, USR-11, SEC-04, SET-02 |
| **D09** | Kỹ thuật viên thấy những ticket nào tại `/technician/tasks` (chỉ ticket đã được phân công cho mình, hay cả ticket `OPEN` chưa giao ai)? | TKT-07 |
| **D10** | Kỹ thuật viên được phép cập nhật thiết bị sang những trạng thái nào tại `/technician/devices`? | DEV-06 |
| **D11** | Giới hạn độ dài min/max của: title, description, comment, username, họ tên; tiêu chuẩn mật khẩu được coi là "yếu"? | TKT-05, USR-06, DEV-04, COL-05, AUTH-12, SET-11 |
| **D12** | Cấu hình Theme (Sáng/Tối/Tự động), Mật độ bảng, Ngôn ngữ, Thông báo được lưu trữ ở MySQL Backend hay ở `localStorage` của trình duyệt? | SET-05–09 |
| **D13** | Allowlist chính xác các đuôi tệp đính kèm; tệp có dung lượng chính xác bằng 10 MiB ($10 \times 1024 \times 1024$ bytes) được chấp nhận hay từ chối? | ATT-03, ATT-04 |
| **D14** | Danh sách chi tiết các sự kiện WebSocket (`ticket_created`, `ticket_updated`, `comment_added`...) và đối tượng người dùng nào nhận từng sự kiện? | WS-01 |
| **D15** | Khi ADMIN tạo ticket: `created_by` lưu ID của ai? Admin có được quyền chọn user chủ sở hữu của ticket không? | TKT-02 |

---

## 3. CHU KỲ 0: CHUẨN BỊ & THIẾT LẬP CỔNG AN TOÀN (GATE)

### 3.1 Cơ chế An toàn Database Chặn cứng (R01, R23)
- Kiểm tra biến môi trường `MYSQL_DATABASE` trong **cả hai** file [`.env`](file:///d:/pyhton/.env) (root) và [`backend/.env`](file:///d:/pyhton/backend/.env), bắt buộc phải có giá trị `cs466_helpdesk_test`.
- Thiết lập Guard `autouse` ở cấp session trong `tests/conftest.py`:
  ```python
  @pytest.fixture(scope="session", autouse=True)
  def guard_test_database(db_connection):
      with db_connection.cursor() as cur:
          cur.execute("SELECT DATABASE()")
          name = cur.fetchone()[0]
      if not name or not name.endswith("_test"):
          pytest.exit(f"VI PHAM R01: Cơ sở dữ liệu '{name}' không có hậu tố _test! Dừng kiểm thử.", returncode=2)
  ```
- Script dọn dẹp/reset database phải tuân thủ thứ tự xóa bảng con trước bảng cha (R23):
  $$\text{TICKET\_ATTACHMENTS} \longrightarrow \text{TICKET\_COMMENTS} \longrightarrow \text{TICKET\_HISTORY} \longrightarrow \text{TICKETS}$$

### 3.2 Bảy bước thực thi Chu kỳ 0
1. **Ghi nhận Test Run (12.1):** Chạy `git checkout main; git pull; git rev-parse HEAD`. Lập mã Run ID `TR-YYYYMMDD-NN`, ghi nhận Tester, OS, Browser, Python, MySQL, Database name, Commit hash, Phạm vi test.
2. **Khởi tạo Database Test:** Tạo database `cs466_helpdesk_test`, thực thi [`database/schema.sql`](file:///d:/pyhton/database/schema.sql) và [`database/seed.sql`](file:///d:/pyhton/database/seed.sql). Xác nhận đủ 6 bảng, khóa ngoại và dữ liệu khởi tạo.
3. **Xác minh Rủi ro K07 (Gate Workspace):** Kiểm tra lỗi có kiểm soát trên bản sao database cũ chưa có bảng `TICKET_ATTACHMENTS` khi truy cập Workspace, sau đó chạy schema update và xác nhận hết lỗi (ATT-06).
4. **Xác minh Rủi ro K05 & K08 (Gate Môi trường):** Chạy script reset DB trên `cs466_helpdesk_test`, kiểm tra không còn orphan records và kiểm tra tính cô lập dữ liệu giữa các test cases trong pytest fixture.
5. **Audit mã nguồn test hiện có:** Rà soát toàn bộ các test hiện có trong `tests/` và `run_role_based_tests.py`, đối chiếu ánh xạ với mã 126 test cases để điền trạng thái ban đầu vào Ma trận Mục 5.
6. **Chuẩn bị Dữ liệu mẫu (Mục 5.3):**
   - Tài khoản chuẩn: `admin`, `tech01`, `user01`, tài khoản INACTIVE, QA user, QA tech.
   - Tickets mẫu ở đủ 5 trạng thái: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`.
   - Bộ tệp đính kèm kiểm thử: png, jpg, pdf, docx, xlsx, txt, zip; tệp sát 10 MiB, tệp vượt 10 MiB, tệp tên tiếng Việt Unicode, tệp đuôi nguy hiểm giả lập; tính toán trước mã băm SHA-256 của từng tệp.
7. **Thiết lập Hạ tầng Thu thập Bằng chứng:**
   - Tạo thư mục `evidence/` gồm `evidence/results.csv` (126 dòng tương ứng 126 cases) và `evidence/defects.md`.
   - Cấu hình pytest hook tự động ghi nhận trạng thái (`PASS`, `FAIL`, `BLOCKED`, `NOT RUN`), actual result, đường dẫn evidence và thời gian chạy.

> **Cổng chuyển tiếp (Gate Chu kỳ 0):** Test Run đã điền đủ thông tin, DB test `cs466_helpdesk_test` ổn định, Guard session hoạt động. Nếu chưa đạt, **không được chuyển sang Chu kỳ 1**.

---

## 4. MA TRẬN 9 CHU KỲ THỰC THI (CHU KỲ 0 – 8)

| Chu kỳ | Tên chu kỳ | Phạm vi nội dung | Ca kiểm thử trọng tâm | Cổng nghiệm thu (Gate) để chuyển tiếp |
| :---: | :--- | :--- | :--- | :--- |
| **0** | **Chuẩn bị** | Thiết lập môi trường, guard an toàn, DB test, baseline, audit test | ENV-01..03, ATT-06, K05, K07, K08 | Test Run hoàn tất, DB `_test` sẵn sàng, guard chặn cứng chạy tốt |
| **1** | **Smoke Test** | Health hệ thống, đăng nhập 3 vai trò, mở các route chính | ENV-04..08, AUTH-01..03, K02 | `GET /api/health` 200, 3 vai trò login thành công; không thì `BLOCKED` |
| **2** | **Backend & DB** | 36 REST Endpoint API contract, validation, RBAC, side effects; **K01 chạy đầu tiên** | USR-11, SEC-04, AUTH-04..09, USR-01..10, DEV-01..10, TKT-01..05, 12..15, 19..23, COL-06, RPT-08 | 36 endpoint có coverage; không có lỗi 5xx diện rộng; K01 được xác minh |
| **3** | **Frontend theo Role** | 13 route giao diện theo 3 vai trò (ADMIN, TECH, USER) qua cả menu và URL trực tiếp | Ma trận 13 route $\times$ 4 role; AUTH-10, 13, TKT-10, 26, SET-01, 05..07, K02, K03, K04 | 13 route được xác minh đầy đủ; các route cấm bị server chặn an toàn |
| **4** | **Tích hợp Luồng** | Vòng đời ticket khép kín (OPEN $\to$ CLOSED), Workspace, comment feed, attachments, WebSocket, settings, báo cáo | TKT-16..18, 24..27, COL-01..05, ATT-01..04, WS-01, SET-02..04, 08..12, RPT-01..06 | Luồng xử lý vé hoàn chỉnh PASS đủ 3 lớp (UI, API, DB/History); tệp tải về khớp SHA-256 |
| **5** | **Bảo mật & Âm/Biên** | Ma trận 36 API $\times$ 4 role, IDOR, bypass JWT, SQLi, XSS, upload bảo mật, quét password_hash | SEC-01..14, boundary payloads | Không còn lỗi Critical hoặc High mở; không rò rỉ `password_hash` hay secret |
| **6** | **Phi chức năng (NFR)** | Responsive đa màn hình, bàn phím, khả năng tiếp cận, đo thời gian p50/p95, tải nhẹ, hồi phục khi mất mạng | NFR-01..10, K06 (ngắt trang PDF) | Rủi ro NFR được đo đạc và ghi nhận đầy đủ; p95 $\le$ 2s với dữ liệu test |
| **7** | **Retest & Regression** | Retest các defect đã fix; chạy bộ hồi quy bắt buộc theo module sửa đổi | Theo danh mục Mục 8.1 tài liệu gốc | Tất cả ca lỗi được xác minh đã sửa; không phát sinh hồi quy; ghi commit cuối |
| **8** | **Báo cáo & Nghiệm thu** | Tổng hợp metrics, lập Test Summary, rà soát Checklist 12 mục, đề xuất Go/No-Go | Toàn bộ 126 test cases; `tests/BAO_CAO_HOAN_THANH_QA.md` | Đạt đầy đủ tiêu chí kết thúc: Pass rate $\ge 95\%$, 0 Critical/High mở |

---

## 4.1 QUY TRÌNH XỬ LÝ ĐẶC BIỆT CHO 8 RỦI RO MÃ NGUỒN (K01 – K08)

Các rủi ro K01–K08 là **giả thuyết cần tái hiện trên môi trường test**, không được mặc định xem là kết quả trước khi chạy:

| Rủi ro | Mức độ | Chu kỳ chạy | Case liên quan | Kịch bản & Quy trình xử lý |
| :---: | :---: | :---: | :--- | :--- |
| **K01** | **Critical** | **Chu kỳ 2 (chạy đầu tiên)** | **USR-11, SEC-04** | **Tuân thủ quy trình R20:**<br>1. Dùng tài khoản `user01` gửi `PATCH /api/users/{own_id}` với payload `{"vai_tro": "ADMIN"}`.<br>2. Kiểm tra `GET /api/auth/me`, truy vấn MySQL và login lại lấy token mới xem vai trò có bị nâng lên ADMIN hay không.<br>3. **Nếu vai trò bị đổi thành công:** Dừng ngay lập tức các ca kiểm thử có thể lan rộng tác động, lập defect **Critical/P0** đủ 10 trường, và **báo ngay cho trưởng nhóm**.<br>4. Chờ developer sửa lỗi và trưởng nhóm duyệt phương án vá lỗi.<br>5. Sau khi có bản fix: retest USR-11, SEC-04 và chạy toàn bộ bộ hồi quy "Auth hoặc user" (AUTH-01–13, USR-08–11, SEC-01–05, đổi mật khẩu).<br>6. Reset lại role của tài khoản test trên DB `_test`. |
| **K02** | **High** | **Chu kỳ 3** | AUTH-01 | Kiểm tra nút đăng nhập nhanh Admin trên giao diện login: xác minh nút có điền đúng mật khẩu seed `CS466@123` không, hay bị sai credentials $\to$ ghi defect High nếu sai. |
| **K03** | **Medium** | **Chu kỳ 3** | COL-04 | Kiểm tra trong composer bình luận: phím `Enter` gửi tin và `Shift+Enter` xuống dòng. Nếu phím Enter không gửi được tin $\to$ ghi defect Medium. |
| **K04** | **Medium** | **Chu kỳ 3** | SET-05, SET-06 | Kiểm tra áp dụng Theme và Mật độ bảng: kiểm tra ngay trên UI, kiểm tra sau khi F5 refresh và kiểm tra sau khi đăng nhập lại (phụ thuộc quyết định D12). |
| **K05** | **Medium** | **Chu kỳ 0** | ENV-03, NFR-10 | Kiểm tra script reset database: xác minh bắt buộc xóa các bảng con trước bảng cha (`attachments` $\to$ `comments` $\to$ `history` $\to$ `tickets`), không để lại orphan records. |
| **K06** | **Low** | **Chu kỳ 6** | RPT-07 | Kiểm tra xuất PDF Dashboard: render thử với dataset biên (rỗng, ít, nhiều, chuỗi rất dài), kiểm tra từng trang để phát hiện khối chữ ký bị đẩy sang trang gần rỗng. |
| **K07** | **High** | **Chu kỳ 0** | ATT-06 | Kiểm tra trên DB cũ chưa có bảng `TICKET_ATTACHMENTS`: xác nhận lỗi 500 xuất hiện có kiểm soát, sau đó chạy schema update và xác nhận route hoạt động bình thường. |
| **K08** | **Medium** | **Chu kỳ 0** | ENV-07, NFR-10 | Kiểm tra isolation của fixture trong Pytest: xác nhận sau mỗi ca test ghi dữ liệu, DB được hoàn trả sạch sẽ cho ca test tiếp theo. |

---

## 5. MA TRẬN PHÂN LOẠI 126 TEST CASES & PHƯƠNG PHÁP THỰC THI

*Quy ước phương pháp:*  
- `API`: Pytest / script gọi trực tiếp HTTP endpoint backend  
- `DB`: Truy vấn SQL assert trực tiếp trên MySQL  
- `UI`: Thao tác trực quan trên giao diện NiceGUI (tự động hóa hoặc thủ công có ghi hình)  
- `MAN`: Kiểm tra thủ công chuyên sâu hoặc công cụ ngoài (DevTools, Excel, trình xem PDF)  
- `FS`: Kiểm tra tệp vật lý trên ổ đĩa, MIME type, kích thước byte và mã băm SHA-256  

| Nhóm | Dải Case ID | Phương pháp | Chu kỳ | Ghi chú & Trọng tâm kiểm tra |
| :---: | :---: | :---: | :---: | :--- |
| **ENV** | 01, 02 | MAN | 0 | Điền Test Run; đối chiếu 2 file `.env` trỏ đúng `cs466_helpdesk_test` |
| **ENV** | 03 | MAN + DB | 0 | Kiểm tra đủ 6 bảng, cấu trúc khóa ngoại và nạp dữ liệu seed |
| **ENV** | 04 | API | 1 | `GET /api/health` trả về 200 `{"status": "ok"}` |
| **ENV** | 05 | API + MAN | 1 | Tải `/openapi.json` đối chiếu khớp đủ 36 REST endpoints |
| **ENV** | 06 | UI | 1 | Truy cập `/login` trên Chrome/Edge, không có lỗi console chặn |
| **ENV** | 07 | API | 1 | `python -m compileall` + pytest; lỗi môi trường ghi `BLOCKED` |
| **ENV** | 08 | API + UI | 1 | Đăng nhập kiểm tra kết nối FE $\to$ BE $\to$ MySQL cho cả 3 vai trò |
| **AUTH** | 01–03 | API + UI | 1 | Đăng nhập hợp lệ cho ADMIN, TECH, USER; AUTH-01 gồm kiểm tra K02 |
| **AUTH** | 04–07 | API + UI | 2 | Sai mật khẩu, user không tồn tại, user INACTIVE, body JSON sai (4 biến thể) |
| **AUTH** | 08–09 | API + UI | 2 | `GET /api/auth/me` từ DB; token thiếu/hỏng/hết hạn $\to$ 401 và UI điều hướng về login |
| **AUTH** | 10 | UI | 3 | Đăng xuất, xóa session local, nút Back/Refresh trình duyệt không làm lộ trang bảo vệ |
| **AUTH** | 11–12 | API + DB + UI | 4 | Đổi mật khẩu hợp lệ và không hợp lệ (D05, D11); DB chỉ lưu bcrypt hash |
| **AUTH** | 13 | UI + API | 3 | Bấm đúp nhanh nút đăng nhập và gửi 2 request đăng nhập song song |
| **USR** | 01–02 | API + UI + DB | 2–3 | Danh sách người dùng, tìm kiếm username/họ tên/email, lọc role/trạng thái |
| **USR** | 03–06 | API + DB (03 thêm UI) | 2 | Tạo user (bcrypt hash), trùng username/email (409), kiểm tra boundary (D11) |
| **USR** | 07 | API + UI + DB | 2 | Cập nhật họ tên, email (D08); xác minh trường `updated_at` thay đổi |
| **USR** | 08–09 | API + DB | 2 | Khóa tài khoản $\to$ token cũ bị từ chối 401; mở khóa $\to$ đăng nhập lại được |
| **USR** | 10 | API + UI | 2–3 | USER và TECH gọi quản lý users $\to$ 403; menu ẩn; nhập URL trực tiếp bị chặn |
| **USR** | **11** | **API + DB** | **2 (đầu)** | **Xác minh Rủi ro K01:** USER tự nâng quyền lên ADMIN qua `PATCH /users/{id}` |
| **DEV** | 01 | API + UI | 2–3 | Tìm kiếm và lọc danh sách thiết bị theo loại và trạng thái |
| **DEV** | 02–05 | API + DB | 2 | Tạo thiết bị, trùng mã (409), boundary inputs, cập nhật thiết bị |
| **DEV** | 06 | UI + API | 3 | TECHNICIAN cập nhật trạng thái thiết bị theo quyền cho phép (D10) |
| **DEV** | 07–09 | API | 2 | USER bị từ chối 403; `/devices/{id}/tickets` rỗng trả `[]`; ID không tồn tại |
| **DEV** | 10 | API + UI | 4 | Chuyển thiết bị sang BROKEN $\to$ danh sách `active-list` không cho chọn khi tạo ticket |
| **TKT** | 01 | API + UI + DB | 2–3 | USER tạo ticket mới $\to$ trạng thái `OPEN`, `created_by` đúng ID người tạo |
| **TKT** | 02–03 | API | 2 | ADMIN tạo ticket (D15); TECHNICIAN gọi tạo ticket bị chặn 403 |
| **TKT** | 04–05 | API + DB | 2 | Thiếu trường, enum sai $\to$ không tạo ticket mồ côi; chuỗi boundary và Unicode |
| **TKT** | 06–09 | API + UI | 2–3 | Danh sách ticket đúng phạm vi từng role (D09); bộ lọc độc lập và tổ hợp |
| **TKT** | 10 | UI | 3 | Mở Ticket Workspace bằng từng role: kiểm tra Header, Metadata, SLA, 3 Tabs |
| **TKT** | 11 | API + UI | 2–3 | USER mở ticket người khác bằng URL/API $\to$ 403 hoặc 404 (D07) |
| **TKT** | 12–13 | API + DB | 2 | Sửa ticket khi OPEN và sau khi đã phân công/xử lý/đóng (D06) |
| **TKT** | 14–15 | API + DB | 2 | Phân công kỹ thuật viên $\to$ trạng thái `ASSIGNED`, history ghi nhận actor; assignee sai |
| **TKT** | 16–18 | API + UI + DB | 4 | Chuỗi workflow: Nhận việc (`IN_PROGRESS`) $\to$ Giải quyết (`RESOLVED`) $\to$ Đóng (`CLOSED`) |
| **TKT** | 19–20 | API + DB | 2 | Chuyển trạng thái sai quy trình $\to$ 400 `INVALID_TRANSITION`; TECH khác sửa $\to$ 403 |
| **TKT** | 21–23 | API + DB | 2 | ADMIN phân công hàng loạt (`batch-assign`), cập nhật trạng thái hàng loạt (`batch-status`) (D04) |
| **TKT** | 24 | API + UI + DB | 4 | Tab Hoạt động & Lịch sử: đầy đủ sự kiện, đúng actor, đúng thứ tự thời gian |
| **TKT** | 25 | API + UI | 4 | Đồng hồ SLA hiển thị theo một mốc thời gian và timezone thống nhất (R18) |
| **TKT** | 26 | UI | 3 | Refresh trình duyệt, mở tab mới và truy cập alias `/tickets/{id}/history` |
| **TKT** | 27 | API + DB | 4 | ADMIN và KTV cùng cập nhật một ticket đồng thời $\to$ kết quả xác định, không mất audit |
| **COL** | 01, 03 | UI + API + DB | 4 | Hiển thị feed trao đổi, gửi comment mới có dấu tiếng Việt, F5 refresh còn nguyên |
| **COL** | 02, 04 | UI | 3 | Chọn các mẫu phản hồi nhanh; kiểm tra phím Enter gửi tin và Shift+Enter (K03) |
| **COL** | 05 | API + UI | 4–5 | Comment rỗng, khoảng trắng, payload XSS HTML/JS $\to$ escape hiển thị dạng văn bản |
| **COL** | 06 | API | 2 | USER không sở hữu ticket bị chặn xem và gửi comment (D07) |
| **ATT** | 01–03 | API + DB + FS | 4 | Upload tệp hợp lệ, tải lại, so sánh tên/MIME/kích thước và checksum SHA-256 (R16, D13) |
| **ATT** | 04 | API + DB | 4 | Tệp sát 10 MiB và vượt 10 MiB $\to$ từ chối 400/413, không sinh metadata rác |
| **ATT** | 05 | API + FS | 5 | Upload exe, 2 đuôi, MIME giả, Unicode, path traversal $\to$ làm sạch an toàn |
| **ATT** | 06 | DB + API | 0 | **Xác minh Rủi ro K07:** Kiểm tra schema bảng `TICKET_ATTACHMENTS` trên DB cũ |
| **WS** | 01 | API | 4 | Kết nối WebSocket: token đúng/sai/hết hạn; chỉ nhận sự kiện trong phạm vi quyền (D14) |
| **SET** | 01 | UI | 3 | Mở `/settings` và chuyển mượt mà giữa 4 tab: Hồ sơ, Giao diện, Thông báo, Bảo mật |
| **SET** | 02–04 | API + UI + DB | 4 | Sticky Action Bar, nút Hủy không gửi PATCH (soi Network), validation họ tên/email |
| **SET** | 05–07 | UI | 3–4 | Đổi Theme (Sáng/Tối/Auto), Mật độ bảng, Ngôn ngữ; xác minh lưu trữ và áp dụng (D12, K04) |
| **SET** | 08–09 | UI + API + DB | 4 | Bật/tắt In-App và Email notification; xử lý khi mạng ngắt kết nối |
| **SET** | 10 | MAN | 4 | Bấm phát thử âm thanh thông báo SLA; kiểm tra cấp quyền audio trình duyệt |
| **SET** | 11 | UI | 4 | Modal đổi mật khẩu: thanh đo độ mạnh mật khẩu realtime, khóa nút submit khi không hợp lệ |
| **SET** | 12 | API + UI + DB | 4 | Đổi mật khẩu thành công $\to$ kiểm tra phiên hiện tại (D05), logout, login mật khẩu mới |
| **RPT** | 01–02 | API + DB + UI | 4 | Dashboard stats đối chiếu chính xác với truy vấn `COUNT(*)` từ MySQL; không cache cũ |
| **RPT** | 03 | API + DB | 4 | `technician-workload`: xác minh số lượng công việc không bị nhân bản bản ghi do JOIN |
| **RPT** | 04–05 | API + MAN | 4 | Xuất vé ra CSV UTF-8 đúng số dòng; xuất Excel `.xlsx` mở được không cảnh báo lỗi |
| **RPT** | 06 | API + UI + MAN | 4 | Xuất Dashboard PDF qua API và UI: HTTP 200 `application/pdf`, font tiếng Việt chuẩn |
| **RPT** | 07 | MAN | 6 | **Xác minh Rủi ro K06:** Render PDF với dataset biên, kiểm tra ngắt trang và khối chữ ký |
| **RPT** | 08 | API | 2 | USER và TECH gọi trực tiếp các endpoint báo cáo Admin $\to$ trả về 403 (D02) |
| **SEC** | 01 | UI + API | 5 | Kiểm thử toàn diện Ma trận phân quyền 13 Route Frontend (Mục 6) |
| **SEC** | 02 | API | 5 | Kiểm thử tự động Ma trận 36 REST Endpoint $\times$ 4 trạng thái (ADMIN, TECH, USER, No-token) |
| **SEC** | 03–04 | API + DB | 5 | Tấn công IDOR trên ticket/comment/attachment; SEC-04 chạy cùng K01 ở Chu kỳ 2 |
| **SEC** | 05 | API | 5 | Giả mạo JWT: sửa payload, sửa role, thuật toán `none`, ký bằng secret lạ $\to$ 401 |
| **SEC** | 06 | API + DB | 5 | Thử SQL Injection (`' OR 1=1 --`) trên ô tìm kiếm, username và các trường text |
| **SEC** | 07 | UI + API | 5 | Thử Stored/Reflected XSS trên tiêu đề, mô tả, comment, họ tên, tên tệp tải lên |
| **SEC** | 08 | API | 5 | Định dạng lỗi chuẩn: có `detail`, `path`; tuyệt đối không lộ stack trace, SQL, secret |
| **SEC** | 09 | API | 5 | CORS policy: kiểm tra preflight `OPTIONS` và Origin không được phép |
| **SEC** | 10 | API + MAN | 5 | Bảo mật download: header `Content-Disposition`, không cho trình duyệt thực thi inline |
| **SEC** | 11 | API | 5 | Quét toàn bộ response JSON của mọi API: **khẳng định 100% không lộ `password_hash`** |
| **SEC** | 12 | API | 5 | Gửi 10–20 request đăng nhập sai liên tiếp: kiểm tra không treo server; ghi nhận rủi ro an toàn (R21) |
| **SEC** | 13 | MAN | 5 | Ngắt MySQL có kiểm soát: API trả lỗi kiểm soát, UI không đơ, kết nối lại hoạt động bình thường |
| **SEC** | 14 | MAN | 5 | Quét mã nguồn, file `.env`, console, log xem có sót secret/password thật không |
| **NFR** | 01–04 | MAN | 6 | Chrome + Edge, độ phân giải 1440×900, 1366×768, 768×1024, 390×844; thao tác phím Tab/Enter/Esc |
| **NFR** | 05 | API | 6 | Đo thời gian phản hồi: đo 10 lần sau warm-up cho health, login, ticket detail; ghi p50/p95 $\le$ 2s |
| **NFR** | 06 | API | 6 | Tải nhẹ: 10–20 request đọc đồng thời; không xuất hiện lỗi 5xx hay cạn connection pool |
| **NFR** | 07 | MAN | 6 | DevTools mô phỏng mạng chậm/mất mạng khi submit form; chống nhấn nút lặp |
| **NFR** | 08 | UI | 6 | F5 refresh trình duyệt khi đang ở các route con sâu (`/tickets/{id}`, `/settings`) |
| **NFR** | 09 | Toàn bộ | 7 | Chạy lại toàn bộ bộ smoke test và regression test sau mỗi lần sửa lỗi |
| **NFR** | 10 | DB + script | 0, 8 | Script dọn dẹp và khôi phục DB test đúng thứ tự bảng con/cha, nạp lại seed sạch sẽ (K05, K08) |

---

## 6. MA TRẬN PHÂN QUYỀN 13 ROUTE GIAO DIỆN (FRONTEND RBAC)

Sử dụng cho kiểm thử Chu kỳ 3 và case **SEC-01**. Mỗi ô kiểm tra đủ 3 đường: hiển thị trên menu, nhập URL trực tiếp vào trình duyệt, và gọi API tương ứng. Các ô "Không" phải bị **server chặn cứng** (chuyển hướng login hoặc báo lỗi quyền), không được chỉ ẩn trên menu giao diện (R08):

| STT | Tuyến đường (Route) | Tên giao diện | ADMIN | TECHNICIAN | USER | Không Token / Chưa đăng nhập |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | `/login` | Đăng nhập hệ thống | Có | Có | Có | Có |
| 2 | `/dashboard` | Trang thống kê tổng quan | Có | Có | Có | Không (chuyển về /login) |
| 3 | `/admin/users` | Quản lý người dùng | Có | Không | Không | Không |
| 4 | `/admin/devices` | Quản lý thiết bị | Có | Không | Không | Không |
| 5 | `/admin/tickets` | Quản lý & Phân công ticket | Có | Không | Không | Không |
| 6 | `/technician/tasks` | Công việc kỹ thuật viên | Không* | Có | Không | Không |
| 7 | `/technician/history` | Lịch sử xử lý công việc | Không* | Có | Không | Không |
| 8 | `/technician/devices` | Thiết bị kỹ thuật viên | Không* | Có | Không | Không |
| 9 | `/user/tickets` | Danh sách ticket cá nhân | Không* | Không* | Có | Không |
| 10 | `/user/tickets/new` | Tạo yêu cầu hỗ trợ mới | Không* | Không* | Có | Không |
| 11 | `/tickets/{id}` | Ticket Workspace chi tiết | Theo quyền vé | Theo quyền vé | Theo quyền vé | Không |
| 12 | `/tickets/{id}/history` | Alias Tab Lịch sử vé | Theo quyền vé | Theo quyền vé | Theo quyền vé | Không |
| 13 | `/settings` | Cài đặt tài khoản & cá nhân | Có | Có | Có | Không |

*\* Ghi chú:* Các ô đánh dấu `Không*` tại dòng 6–10 phản ánh phân quyền theo cột Quyền của tài liệu gốc. Nếu mã nguồn thực tế cho phép Admin truy cập giao diện của Tech hoặc User, tester sẽ ghi nhận hiện trạng và xin ý kiến trưởng nhóm (không tự ý đổi expected result).

---

## 7. CẤU TRÚC THƯ MỤC VÀ TẬP HỒ SƠ BÀN GIAO (DELIVERABLES)

```
d:\pyhton\
├── tests/
│   ├── conftest.py                  # Guard DB _test, fixtures role tokens, helper SQL 3 lớp, che token
│   ├── api/
│   │   ├── test_auth.py             # AUTH-04..09
│   │   ├── test_users.py            # USR-01..11 (gồm K01)
│   │   ├── test_devices.py          # DEV-01..10
│   │   ├── test_tickets_workflow.py # TKT-01..23 (state machine, batch actions)
│   │   ├── test_comments.py         # COL-01..06 (feed, reply templates, XSS)
│   │   ├── test_attachments.py      # ATT-01..05 (allowlist, 10MB boundary, traversal, SHA-256)
│   │   ├── test_settings_auth.py    # SET-02..04, 08..09; AUTH-11..12
│   │   ├── test_reports_export.py   # RPT-01..06, 08 (workload, CSV, XLSX, PDF)
│   │   ├── test_websocket.py        # WS-01 (kết nối token, broadcast sự kiện)
│   │   └── test_security_matrix.py  # SEC-02..12 (ma trận 36 API x 4 role, SQLi, quét password_hash)
│   └── integration/
│       └── test_ticket_lifecycle.py # TKT-16..18, 24, 27 (chu trình trọn vẹn UI -> API -> DB -> History)
├── evidence/
│   ├── results.csv                  # Nhật ký chạy đủ 126 test cases (Mục 12.2)
│   ├── defects.md                   # Sổ theo dõi lỗi theo chuẩn 10 trường (Mục 7.3)
│   └── YYYYMMDD_CASEID_ROLE_*.ext   # Tệp bằng chứng (ảnh, response sanitized)
├── implementation_plan.md           # Kế hoạch thực thi v2 đối chiếu
└── KE_HOACH_THUC_HIEN_TEST_FULLSTACK.md # Tài liệu kế hoạch thực thi chi tiết này
```

### Năm hồ sơ bàn giao bắt buộc khi kết thúc:
1. **Bảng kết quả Test Run đã điền (Mục 12.1):** Kèm file nhật ký `evidence/results.csv` đầy đủ 126 dòng kết quả, không dòng nào bị trống trạng thái.
2. **Sổ theo dõi Defect chuẩn 10 trường (Mục 7.3):** Quản lý đúng vòng đời `NEW` $\to$ `TRIAGED` $\to$ `IN PROGRESS` $\to$ `READY FOR RETEST` $\to$ `CLOSED` / `REOPENED` / `DEFERRED`.
3. **Ma trận truy vết yêu cầu (Mục 10):** Đã cập nhật trạng thái thực tế đối chiếu giữa Yêu cầu, Giao diện FE, API Backend và MySQL.
4. **Báo cáo tổng kết kiểm thử (Test Summary - Mục 12.4):** Cập nhật chính thức vào [tests/BAO_CAO_HOAN_THANH_QA.md](file:///d:/pyhton/tests/BAO_CAO_HOAN_THANH_QA.md).
5. **Checklist bàn giao 12 mục (Mục 13):** Đã kiểm tra đầy đủ, kèm chữ ký xác nhận của Tester và Trưởng nhóm với quyết định **GO** hoặc **NO-GO**.

---

## 8. ĐIỀU KIỆN DỪNG VÀ TIẾP TỤC (STOP & RESUME CONDITIONS - MỤC 6.2)

| Tình huống phát sinh | Hành động xử lý ngay | Điều kiện để tiếp tục kiểm thử |
| :--- | :--- | :--- |
| **Phát hiện lỗi Critical phân quyền hoặc mất dữ liệu (như K01)** | Dừng ngay các ca test có nguy cơ mở rộng tác động; báo ngay trưởng nhóm | Bản fix đã được triển khai lên nhánh test và smoke test bảo mật đạt `PASS` |
| **Backend hoặc MySQL không khởi động được** | Ghi nhận trạng thái `BLOCKED`, thu thập toàn bộ log hệ thống | Môi trường được phục hồi ổn định; ca health và login đạt `PASS` |
| **Schema hoặc dữ liệu seed sai lệch baseline** | Dừng các ca kiểm thử phụ thuộc dữ liệu bị sai lệch | Reset lại database test chuẩn xác theo đúng commit đang test |
| **Tỷ lệ lỗi HTTP 5xx xuất hiện lan rộng** | Dừng kiểm thử hồi quy diện rộng; khoanh vùng lỗi | Lỗi gốc rễ được khắc phục hoặc có giải pháp tạm thời (workaround) được duyệt |
| **Nhánh main có commit mới giữa chu kỳ kiểm thử** | Tuyệt đối không đổi commit giữa chừng (R03); đóng lượt test hiện tại | Mở một Test Run mới ghi nhận đúng commit hash mới và chạy lại từ đầu |

---

## 9. TIÊU CHÍ KẾT THÚC VÀ CÔNG THỨC CHỈ SỐ (MỤC 6.3 & 12.3)

### Tiêu chí kết thúc để được xem xét phát hành:
- [x] **100% các ca test Critical và High-risk đã chạy; KHÔNG còn lỗi Critical hoặc High nào ở trạng thái mở.**
- [x] **Tỷ lệ Pass Rate tổng thể đạt tối thiểu $\ge 95\%$ trên tổng số ca test đã thực thi.**
- [x] **Không có lỗi HTTP 500 không mong đợi** trong các luồng smoke, workflow, attachments, settings và reports.
- [x] Ma trận phân quyền 3 vai trò, quy trình vé khép kín, upload/download tệp, xuất PDF, đổi mật khẩu và hồi quy đều đạt `PASS`.
- [x] Mọi ca test bị `BLOCKED` đều có ghi chú nguyên nhân và quyết định xử lý rõ ràng.

### Công thức tính chỉ số chuẩn:
- $\text{Executed} = \text{PASS} + \text{FAIL} + \text{BLOCKED}$
- $\text{Pass Rate} = \frac{\text{PASS}}{\text{PASS} + \text{FAIL}} \times 100\%$ *(Lưu ý: số ca BLOCKED không nằm ở mẫu số)*
- $\text{Coverage} = \frac{\text{Số ca đã chạy}}{126} \times 100\%$
- $\text{Reopen Rate} = \frac{\text{Số defect bị Reopen}}{\text{Tổng số defect đã Retest}} \times 100\%$
- **Khuyến nghị bàn giao:** Đưa ra 1 trong 3 mức: `GO`, `GO WITH KNOWN RISKS`, hoặc `NO-GO` kèm luận cứ kỹ thuật.

---

## 10. LỆNH THỰC THI VÀ KIỂM CHỨNG HỆ THỐNG

Thực thi tuần tự trên PowerShell:

```powershell
# Bước 1: Xác nhận biến môi trường DB an toàn (phải ra cs466_helpdesk_test)
Select-String -Path .env, backend\.env -Pattern "MYSQL_DATABASE"

# Bước 2: Kiểm tra biên dịch cú pháp toàn bộ source code
python -m compileall backend frontend tests

# Bước 3: Chạy bộ Pytest toàn diện
$env:MYSQL_DATABASE="cs466_helpdesk_test"
pytest tests/api tests/integration -v --tb=short

# Bước 4: Chạy runner kiểm thử tổng hợp theo vai trò
python tests/run_role_based_tests.py
```

*Kế hoạch thực thi v2 này đã được hiệu chỉnh hoàn toàn chuẩn xác, đồng bộ 100% với tài liệu gốc và file `d:\pyhton\implementation_plan.md`.*
