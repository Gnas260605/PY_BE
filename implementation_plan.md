# Kế hoạch thực thi kiểm thử CS466 Helpdesk (v2)

Bản viết lại của kế hoạch thực thi, bám sát **CS466_Fullstack_FE_BE_Test_Plan.docx** (mã `CS466-QA-FTP-001`, v1.0). Khi kế hoạch này và tài liệu gốc mâu thuẫn, **tài liệu gốc thắng** (R09). Kế hoạch chỉ quyết định *cách chạy*, không đổi *kết quả mong đợi*.

Phạm vi: 13 route giao diện, 36 REST endpoint + 1 WebSocket, 6 bảng MySQL, **126 test case** (ENV 8, AUTH 13, USR 11, DEV 10, TKT 27, COL 6, ATT 6, WS 1, SET 12, RPT 8, SEC 14, NFR 10), 8 rủi ro sơ bộ K01–K08, thực thi theo **9 chu kỳ (0–8)**.

---

## 0. Những điểm khác so với bản kế hoạch cũ

| Bản cũ | Bản này |
| --- | --- |
| "8 chu kỳ", 6 giai đoạn | 9 chu kỳ (0–8) đúng mục 8 của tài liệu gốc |
| Defect "15 trường" | 10 trường bắt buộc theo mục 7.3 |
| Hard-code commit `bf51d53…` | `git rev-parse HEAD` ghi vào Test Run; baseline `bf51d53…` chỉ để đối chiếu (R03) |
| "Không có câu hỏi chặn" | Có danh sách quyết định contract cần chốt trước khi chạy (mục 2) |
| Chỉ assert ở API | Mỗi case đổi dữ liệu đối chiếu đủ 3 lớp UI, API, MySQL (R05, R06, mục 3.1) |
| Không có WebSocket test | Có `test_websocket.py` (WS-01) |
| Thiếu ~25 case | Ma trận đủ 126 case có phương pháp và chu kỳ (mục 5) |
| K01: "fix ngay" | K01: tái hiện, dừng, báo trưởng nhóm, chờ duyệt, retest (R20) |
| Không có evidence, Test Run, log kết quả | Có đủ, theo mục 7.4, 12.1, 12.2, 12.4 |
| Trang theo role đếm sai | Ma trận role × route đúng 13 route (mục 6) |

---

## 1. Nguyên tắc vận hành

1. **Ba lớp cho mọi case đổi dữ liệu** (R05, R06): giao diện đúng, API đúng status/body/quyền, MySQL và bảng history/comments/attachments đúng. Không PASS vì toast hoặc HTTP 200.
2. **Chỉ ghi/xóa trên DB `_test`** (R01, R23). Có cơ chế chặn cứng ở mục 3.1.
3. **Không sửa expected sau khi thấy actual** (R09). Expected lấy từ tài liệu gốc, không viết theo hành vi code hiện tại. Case phụ thuộc quyết định chưa chốt ghi `BLOCKED` kèm lý do, không đoán.
4. **Trạng thái duy nhất:** `PASS`, `FAIL`, `BLOCKED`, `NOT RUN` (R24). Lỗi môi trường/công cụ là `BLOCKED`, không phải `FAIL` (R19).
5. **Workflow test bằng cả UI và API trực tiếp** (R14); route hạn chế test bằng menu, URL trực tiếp và API trực tiếp (R08).
6. **Bằng chứng** đặt tên `YYYYMMDD_CASEID_ROLE_MO-TA.ext`, che token/password/secret (R11, mục 7.4).
7. **Fix chỉ đóng khi retest case gốc + regression module liên quan** (R12, mục 8.1 của tài liệu gốc).

---

## 2. Quyết định contract cần chốt trước khi chạy (thay cho "Open Questions")

Tài liệu gốc ghi "theo contract" ở các chỗ dưới đây. Trước Chu kỳ 2 phải có câu trả lời bằng văn bản (từ trưởng nhóm/developer/OpenAPI), ghi nguồn phê duyệt. Case liên quan là `BLOCKED` cho đến khi chốt.

| ID | Câu hỏi cần chốt | Case bị ảnh hưởng |
| --- | --- | --- |
| D01 | `POST /api/register` public hay bị giới hạn? Role mặc định là gì? | AUTH, SEC-02 |
| D02 | Quyền và định dạng của `export-tickets`, `export-tickets-excel`, `export-dashboard-pdf` theo từng role | RPT-04–08 |
| D03 | `PATCH /tickets/{id}/close`: ai được gọi, khác gì `status=CLOSED` | TKT-18, TKT-19 |
| D04 | `batch-assign`/`batch-status` khi có ID sai: atomic hay partial? Response ghi kết quả thế nào? | TKT-22, TKT-23 |
| D05 | Sau đổi mật khẩu, token hiện tại còn hiệu lực không? | AUTH-11, SET-12 |
| D06 | Chủ sở hữu được sửa trường nào ở từng trạng thái; sửa ticket có sinh history không? | TKT-12, TKT-13 |
| D07 | Ticket của người khác trả 403 hay 404? (chính sách thống nhất cho ticket/comment/attachment) | TKT-11, COL-06, SEC-03 |
| D08 | Trường nào chính chủ được `PATCH /users/{id}`; trường `vai_tro` bị loại hay trả 403? | USR-07, USR-11, SEC-04, SET-02 |
| D09 | TECHNICIAN thấy ticket nào ở `/technician/tasks` (chỉ được giao, hay cả OPEN chưa giao)? | TKT-07 |
| D10 | TECHNICIAN được đặt thiết bị sang trạng thái nào? | DEV-06 |
| D11 | Giới hạn min/max: title, description, comment, username, họ tên; chính sách mật khẩu "yếu" | TKT-05, USR-06, DEV-04, COL-05, AUTH-12, SET-11 |
| D12 | Theme, mật độ, ngôn ngữ, thông báo lưu ở server hay localStorage? | SET-05–09 |
| D13 | Allowlist đuôi tệp chính xác; đúng 10 MiB được nhận hay bị từ chối? | ATT-03, ATT-04 |
| D14 | Danh sách sự kiện WebSocket và ai nhận từng loại | WS-01 |
| D15 | ADMIN tạo ticket: `created_by` là ai, có chọn được chủ sở hữu không? | TKT-02 |

---

## 3. Chu kỳ 0: Chuẩn bị (gate của mọi chu kỳ sau)

### 3.1 Cơ chế an toàn database (làm trước mọi thứ)

- Kiểm tra `MYSQL_DATABASE` trong **cả hai** `.env` (root và `backend/`) đều là `cs466_helpdesk_test`. `pytest` không được ghi đè chỉ bằng biến môi trường trong shell.
- Thêm guard vào `tests/conftest.py` (`autouse`, phạm vi session): hỏi DB thật của kết nối test bằng `SELECT DATABASE()`, và nếu tên không kết thúc `_test` thì `pytest.exit` ngay, trước khi có test nào chạy. Phác thảo:

```python
@pytest.fixture(scope="session", autouse=True)
def guard_test_database(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT DATABASE()")
        name = cur.fetchone()[0]
    if not name or not name.endswith("_test"):
        pytest.exit(f"R01: '{name}' không có hậu tố _test", returncode=2)
```
- Script reset/cleanup cũng phải tự kiểm tra tên DB (K05) và xóa theo thứ tự `ATTACHMENTS → COMMENTS → HISTORY → TICKETS` (R23).

### 3.2 Việc cần làm

1. **Baseline:** `git checkout main; git pull; git rev-parse HEAD`. Điền Test Run (mục 12.1 tài liệu gốc): Run ID `TR-YYYYMMDD-NN`, tester, OS/browser, Python/MySQL, DB name, commit, phạm vi.
2. **DB test:** tạo `cs466_helpdesk_test`, chạy `database/schema.sql` rồi `seed.sql`. Xác nhận đủ 6 bảng gồm `TICKET_ATTACHMENTS`, có khóa ngoại và seed.
3. **K07 (gate môi trường):** thử mở Ticket Workspace trên DB *cũ chưa có* `TICKET_ATTACHMENTS` (bản sao riêng), ghi nhận lỗi có kiểm soát, rồi chạy lại schema và xác nhận hết lỗi (ATT-06). Đây là điều kiện tiên quyết cho toàn bộ test workspace.
4. **K05, K08 (gate môi trường):** chạy script reset trên DB `_test`, kiểm tra không còn orphan (comments/attachments), kiểm tra fixture cô lập dữ liệu giữa các test. Nếu chưa đạt, ghi defect và dùng script reset thủ công đúng thứ tự trong lúc chờ.
5. **Audit test hiện có:** liệt kê `tests/` hiện có (kể cả `run_role_based_tests.py`) và gắn từng test vào mã case. Kết quả là cột "Hiện trạng" trong ma trận mục 5 (đã có / cần bổ sung / chưa có). Không viết test mới trước khi biết đã có gì.
6. **Dữ liệu chuẩn (mục 5.3 tài liệu gốc):** tài khoản `admin`, `tech01`, `user01`, tài khoản INACTIVE, thêm QA user/QA technician; ticket ở đủ 5 trạng thái; bộ tệp png/jpg/pdf/docx/xlsx/txt/zip, tệp sát 10 MiB và vượt 10 MiB, tên Unicode, tên nguy hiểm giả lập; SHA-256 của từng tệp.
7. **Hạ tầng ghi kết quả:** thêm marker `@pytest.mark.case("TKT-19")` và một hook ghi `evidence/results.csv` gồm `case, status, actual, evidence, time`. Skip do lỗi môi trường ánh xạ sang `BLOCKED`. Helper truy vấn DB dùng chung cho các assert lớp 3, helper che token khi lưu request/response.

**Gate:** Test Run đã điền, DB ổn định, guard chạy được. Chưa đạt thì không sang Chu kỳ 1.

---

## 4. Các chu kỳ thực thi

| Chu kỳ | Nội dung | Case chính | Gate chuyển tiếp |
| --- | --- | --- | --- |
| **0** | Chuẩn bị (mục 3) | ENV-01–03, ATT-06 | Test Run đủ, DB `_test` ổn định, K05/K07/K08 xử lý |
| **1** | Smoke | ENV-04–08, AUTH-01–03 | health OK, 3 role đăng nhập được, route chính mở được; không thì `BLOCKED` |
| **2** | Backend + DB | Toàn bộ case API/DB trong mục 5; **K01 chạy đầu tiên** | 36 endpoint có coverage; không 5xx lan rộng |
| **3** | Frontend theo role | Case UI theo ma trận mục 6; K02, K03, K04 | 13 route × role đã kiểm tra, cả menu lẫn URL trực tiếp |
| **4** | Tích hợp | TKT-24–27, COL, ATT, WS-01, SET, RPT | Luồng OPEN→ASSIGNED→IN_PROGRESS→RESOLVED→CLOSED PASS đủ 3 lớp |
| **5** | Bảo mật + âm/biên | SEC-01–14, boundary còn lại | Không Critical/High mở |
| **6** | Phi chức năng | NFR-01–10, K06 | Rủi ro NFR được ghi |
| **7** | Retest + regression | Theo bảng 8.1 tài liệu gốc | Không tái phát; ghi commit cuối |
| **8** | Báo cáo | Metrics, Test Summary, Go/No-Go | Xem tiêu chí kết thúc (mục 9) |

### 4.1 Cách xử lý 8 rủi ro K01–K08

| Rủi ro | Mức | Chạy ở | Case | Ghi chú |
| --- | --- | --- | --- | --- |
| K01 | Critical | Chu kỳ 2 (đầu tiên) | USR-11, SEC-04 | Xem quy trình dừng bên dưới |
| K02 | High | Chu kỳ 3 | AUTH-01 | Nút đăng nhập nhanh Admin: đúng mật khẩu seed hoặc phải bị loại bỏ |
| K03 | Medium | Chu kỳ 3 | COL-04 | So sánh nút Gửi, Enter, Shift+Enter |
| K04 | Medium | Chu kỳ 3 | SET-05, SET-06 | Kiểm tra ngay, sau refresh, sau đăng nhập lại (phụ thuộc D12) |
| K05 | Medium | Chu kỳ 0 | ENV-03, NFR-10 | Xem 3.2 mục 4 |
| K06 | Low | Chu kỳ 6 | RPT-07 | Render PDF với dữ liệu ít, nhiều, rỗng, chuỗi dài; xem từng trang |
| K07 | High | Chu kỳ 0 | ATT-06 | Xem 3.2 mục 3 |
| K08 | Medium | Chu kỳ 0 | ENV-07, NFR-10 | Xem 3.2 mục 4 |

Các mục K là **giả thuyết cần tái hiện**, không phải kết quả (mục 11 tài liệu gốc). Chỉ lập defect khi tái hiện được trên môi trường test.

**Quy trình K01 (R20):**
1. Dùng `user01` gọi `PATCH /api/users/{own_id}` với `vai_tro=ADMIN`, sau đó kiểm tra `GET /auth/me`, DB, và đăng nhập lại để xem token mới.
2. Nếu role đổi thành công: **dừng** các case có thể mở rộng thiệt hại, lập defect Critical/P0 đủ 10 trường, **báo trưởng nhóm ngay**.
3. Fix do developer phụ trách thực hiện và được trưởng nhóm duyệt (nếu cùng một người đảm nhiệm cả hai vai trò thì vẫn phải có duyệt bằng văn bản). Tester không tự sửa code rồi tự đóng defect.
4. Sau fix: retest USR-11, SEC-04 và regression "Auth hoặc user" (AUTH-01–13, USR-08–11, SEC-01–05, settings đổi mật khẩu).
5. Khôi phục role của tài khoản test bằng script trên DB `_test`.

---

## 5. Ma trận 126 case và phương pháp thực thi

**Ký hiệu:** `API` pytest gọi HTTP trực tiếp · `DB` assert trực tiếp trên MySQL · `UI` giao diện (Playwright/`nicegui.testing` nếu dựng được, nếu không thì thủ công) · `MAN` chỉ thủ công hoặc công cụ ngoài (DevTools, Excel, mắt thường) · `FS` đối chiếu tệp vật lý/checksum.

Cột "Hiện trạng" điền sau audit ở Chu kỳ 0.

| Nhóm | Case | Phương pháp | Chu kỳ | Ghi chú |
| --- | --- | --- | --- | --- |
| ENV | 01, 02 | MAN | 0 | Ghi Test Run; đối chiếu hai `.env` |
| ENV | 03 | MAN + DB | 0 | Đếm 6 bảng, FK, seed |
| ENV | 04 | API | 1 | `GET /api/health` |
| ENV | 05 | API + MAN | 1 | So `/openapi.json` với danh mục 36 endpoint |
| ENV | 06 | UI | 1 | `/login`, console không lỗi chặn |
| ENV | 07 | API | 1 | `compileall` + pytest; lỗi môi trường → BLOCKED |
| ENV | 08 | API + UI | 1 | Đăng nhập 3 role |
| AUTH | 01–03 | API + UI | 1 | AUTH-01 gồm K02 |
| AUTH | 04–07 | API + UI | 2 | Sai mật khẩu, user lạ, INACTIVE, body sai (4 biến thể) |
| AUTH | 08–09 | API + UI | 2 | `auth/me` từ DB; token thiếu/hỏng/hết hạn, UI về login |
| AUTH | 10 | UI | 3 | Đăng xuất, Back/refresh không lộ trang |
| AUTH | 11–12 | API + DB + UI | 4 | Phụ thuộc D05, D11; DB chỉ lưu hash |
| AUTH | 13 | UI + API | 3 | Bấm đúp và hai request song song |
| USR | 01–02 | API + UI + DB | 2–3 | Danh sách, tìm kiếm, lọc kết hợp |
| USR | 03–06 | API + DB (03 thêm UI) | 2 | bcrypt hash, trùng username/email (409), boundary (D11) |
| USR | 07 | API + UI + DB | 2 | Phụ thuộc D08; `updated_at` đổi |
| USR | 08–09 | API + DB | 2 | Token cũ bị 401 sau khi khóa (DB reload trạng thái) |
| USR | 10 | API + UI | 2–3 | 403 cho USER/TECH; menu ẩn; URL trực tiếp bị chặn |
| USR | **11** | API + DB | **2 (đầu tiên)** | **K01** |
| DEV | 01 | API + UI | 2–3 | Tìm/lọc trạng thái và loại |
| DEV | 02–05 | API + DB | 2 | Tạo, trùng mã (409), boundary, cập nhật |
| DEV | 06 | UI + API | 3 | Phụ thuộc D10 |
| DEV | 07–09 | API | 2 | USER bị 403; `/devices/{id}/tickets` rỗng trả `[]`; ID lạ, sai kiểu |
| DEV | 10 | API + UI | 4 | `active-list` loại thiết bị không ACTIVE |
| TKT | 01 | API + UI + DB | 2–3 | OPEN, `created_by` đúng |
| TKT | 02–03 | API | 2 | TKT-02 phụ thuộc D15; TECH bị 403 |
| TKT | 04–05 | API + DB | 2 | Không có ticket mồ côi; Unicode |
| TKT | 06–09 | API + UI | 2–3 | Đúng phạm vi từng role (D09); lọc từng tiêu chí và tổ hợp |
| TKT | 10 | UI | 3 | Header, metadata, SLA, ba tab |
| TKT | 11 | API + UI | 2–3 | Phụ thuộc D07 |
| TKT | 12–13 | API + DB | 2 | Phụ thuộc D06; bốn trạng thái |
| TKT | 14–15 | API + DB | 2 | Assign; history có old/new và actor; assignee sai |
| TKT | 16–18 | API + UI + DB | 4 | Chuỗi workflow, action bar, history |
| TKT | 19–20 | API + DB | 2 | Bước nhảy sai → 400 `INVALID_TRANSITION`; TECH khác → 403; DB/history không đổi |
| TKT | 21–23 | API + DB | 2 | Phụ thuộc D04 |
| TKT | 24 | API + UI + DB | 4 | End-to-end đủ sự kiện, actor, thứ tự |
| TKT | 25 | API + UI | 4 | SLA theo một mốc thời gian và timezone thống nhất (R18) |
| TKT | 26 | UI | 3 | Refresh, tab mới, alias `/tickets/{id}/history` |
| TKT | 27 | API + DB | 4 | Song song ADMIN và TECH; không mất history |
| COL | 01, 03 | UI + API + DB | 4 | Đúng tác giả, thời gian; refresh còn |
| COL | 02, 04 | UI | 3 | Mẫu phản hồi; Enter/Shift+Enter (K03) |
| COL | 05 | API + UI | 4–5 | Rỗng, khoảng trắng, quá dài, HTML là text |
| COL | 06 | API | 2 | Phụ thuộc D07 |
| ATT | 01–03 | API + DB + FS | 4 | Upload, tải lại, so tên/MIME/size/SHA-256 (R16); D13 |
| ATT | 04 | API + DB | 4 | Sát và vượt 10 MiB (D13); không metadata rác |
| ATT | 05 | API + FS | 5 | exe, hai đuôi, MIME giả, Unicode, path traversal |
| ATT | 06 | DB + API | 0 | K07 |
| WS | 01 | API | 4 | Client WebSocket: token hợp lệ/thiếu/hỏng/hết hạn; chỉ nhận sự kiện có quyền (D14) |
| SET | 01 | UI | 3 | Bốn tab |
| SET | 02–04 | API + UI + DB | 4 | Action bar, Hủy không gọi PATCH (kiểm tra qua Network), validation |
| SET | 05–07 | UI | 3–4 | Theme, mật độ, ngôn ngữ; áp dụng + persist (D12; K04) |
| SET | 08–09 | UI + API + DB | 4 | Lưu thông báo; lỗi mạng rollback hoặc báo rõ |
| SET | 10 | MAN | 4 | Âm thanh SLA, quyền âm thanh của trình duyệt |
| SET | 11 | UI | 4 | Thanh độ mạnh, submit bị khóa |
| SET | 12 | API + UI + DB | 4 | Phụ thuộc D05 |
| RPT | 01–02 | API + DB + UI | 4 | Đối chiếu với truy vấn DB; không cache cũ |
| RPT | 03 | API + DB | 4 | Workload không nhân bản do JOIN |
| RPT | 04–05 | API + MAN | 4 | CSV UTF-8, số dòng; XLSX mở được (openpyxl, và mở tay bằng Excel) |
| RPT | 06 | API + UI + MAN | 4 | 200 `application/pdf`; font tiếng Việt |
| RPT | 07 | MAN | 6 | K06; render từng trang ra ảnh, dataset biên |
| RPT | 08 | API | 2 | Phụ thuộc D02 |
| SEC | 01 | UI + API | 5 | Ma trận role × route (mục 6) |
| SEC | 02 | API | 5 | 36 endpoint × ADMIN/TECH/USER/no-token, sinh tự động từ `/openapi.json` |
| SEC | 03–04 | API + DB | 5 | IDOR; SEC-04 chạy cùng K01 ở Chu kỳ 2 |
| SEC | 05 | API | 5 | JWT sửa payload, `alg=none`, secret khác |
| SEC | 06 | API + DB | 5 | SQLi ở keyword/login/text |
| SEC | 07 | UI + API | 5 | Stored/reflected XSS ở title, description, comment, name, filename |
| SEC | 08 | API | 5 | Envelope lỗi, không lộ stack/SQL/path |
| SEC | 09 | API | 5 | OPTIONS + Origin lạ |
| SEC | 10 | API + MAN | 5 | `Content-Disposition`, không inline thực thi |
| SEC | 11 | API | 5 | Quét mọi response tìm `password_hash`, secret, token |
| SEC | 12 | API | 5 | 10–20 request an toàn; nếu chưa có rate-limit thì **ghi rủi ro**, không assert cứng, không DoS (R21) |
| SEC | 13 | MAN | 5 | Ngắt MySQL trên môi trường kiểm soát |
| SEC | 14 | MAN | 5 | Quét secret trong repo, `.env`, console, network log, file export |
| NFR | 01–04 | MAN | 6 | Chrome + Edge, 1440×900, 1366×768, 768×1024, 390×844, bàn phím, accessibility, zoom 200% |
| NFR | 05 | API | 6 | 10 lần sau warm-up, ghi p50/p95 |
| NFR | 06 | API | 6 | 10–20 request đọc đồng thời; không 5xx |
| NFR | 07 | MAN | 6 | Mạng chậm/timeout/mất mạng (DevTools); chống submit lặp |
| NFR | 08 | UI | 6 | Refresh ở route sâu |
| NFR | 09 | (toàn bộ) | 7 | Smoke + regression sau mỗi fix |
| NFR | 10 | DB + script | 0, 8 | Reset đúng thứ tự, seed khôi phục được (K05, K08) |

**Về automation frontend:** dựng Playwright (hoặc fixture `nicegui.testing` của NiceGUI) là lựa chọn, không bắt buộc. Nếu chưa dựng được thì case `UI` chạy thủ công và vẫn phải có ảnh/video làm bằng chứng. Nên tự động hóa tối thiểu: đăng nhập 3 role, ma trận role × route (SEC-01), luồng workflow chính. Quyết định này cần chốt ở Chu kỳ 0.

---

## 6. Ma trận role × route FE (13 route)

Dùng cho Chu kỳ 3 và SEC-01. Mỗi ô kiểm tra ba đường vào: menu, URL trực tiếp, API tương ứng. Ô "không" phải bị chặn ở **server** chứ không chỉ ẩn ở frontend (R08).

| Route | ADMIN | TECHNICIAN | USER | No-token |
| --- | --- | --- | --- | --- |
| `/login` | có | có | có | có |
| `/dashboard` | có | có | có | không |
| `/admin/users` | có | không | không | không |
| `/admin/devices` | có | không | không | không |
| `/admin/tickets` | có | không | không | không |
| `/technician/tasks` | không | có | không | không |
| `/technician/history` | không | có | không | không |
| `/technician/devices` | không | có | không | không |
| `/user/tickets` | không | không | có | không |
| `/user/tickets/new` | không | không | có | không |
| `/tickets/{id}` | theo quyền ticket | theo quyền ticket | theo quyền ticket | không |
| `/tickets/{id}/history` | theo quyền ticket | theo quyền ticket | theo quyền ticket | không |
| `/settings` | có | có | có | không |

Các ô "không" ở dòng 6–10 (ví dụ ADMIN vào `/technician/tasks`) là **giả định từ cột Quyền của tài liệu gốc**. Nếu code cho phép, ghi nhận và hỏi trưởng nhóm đó là lỗi hay chủ ý, không tự đổi expected.

---

## 7. Cấu trúc test và deliverable

Đường dẫn dưới đây là đề xuất, xác nhận lại sau audit ở Chu kỳ 0 để không trùng file hiện có.

```
tests/
  conftest.py                  # guard _test, fixture role token, helper DB, che token, hook ghi results.csv
  api/
    test_auth.py               # AUTH-04–09
    test_users.py              # USR-01–11
    test_devices.py            # DEV-01–10
    test_tickets_workflow.py   # TKT-01–23 (gồm state machine, batch)
    test_comments.py           # COL-01, 03, 05, 06
    test_attachments.py        # ATT-01–05 (checksum, allowlist, boundary, traversal)
    test_settings_auth.py      # SET-02, 04, 08, 09; AUTH-11, 12
    test_reports_export.py     # RPT-01–06, 08
    test_websocket.py          # WS-01
    test_security_matrix.py    # SEC-02, 03, 05, 06, 08, 09, 11, 12
  integration/
    test_ticket_lifecycle.py   # TKT-16–18, 24, 27 (UI → API → DB → history)
  ui/                          # tùy chọn (Playwright/nicegui.testing): SEC-01, AUTH-10, luồng workflow
evidence/
  results.csv                  # nhật ký case (mục 12.2)
  defects.md                   # defect log (10 trường)
  YYYYMMDD_CASEID_ROLE_*.ext   # ảnh, request/response đã che token
```

**Deliverable cuối chu kỳ:**
1. Test Run đã điền (12.1), `results.csv` đủ 126 dòng.
2. Defect log theo 10 trường (7.3) và vòng đời NEW → TRIAGED → IN PROGRESS → READY FOR RETEST → CLOSED / REOPENED / DEFERRED (7.2).
3. Ma trận truy vết mục 10 tài liệu gốc, cập nhật cột trạng thái.
4. Test Summary (12.4) và `tests/BAO_CAO_HOAN_THANH_QA.md`.
5. Checklist bàn giao 12 mục (mục 13) và biên bản Go/No-Go có chữ ký tester và trưởng nhóm.

---

## 8. Điều kiện dừng và tiếp tục (mục 6.2)

| Tình huống | Hành động | Điều kiện tiếp tục |
| --- | --- | --- |
| Critical phân quyền hoặc mất dữ liệu (K01…) | Dừng các case có thể mở rộng thiệt hại; báo ngay | Fix triển khai + smoke bảo mật PASS |
| Backend hoặc DB không khởi động | BLOCKED, thu log | Môi trường ổn định; health + login PASS |
| Schema/seed sai baseline | Dừng case phụ thuộc dữ liệu | Reset DB test đúng commit |
| Tỷ lệ 5xx lan rộng | Dừng regression sâu, khoanh vùng | Sửa nguyên nhân hoặc workaround được duyệt |
| Commit `main` thay đổi giữa chu kỳ | Không đổi giữa chừng; mở Test Run mới (R03) | Ghi commit mới |

---

## 9. Tiêu chí kết thúc và chỉ số (mục 6.3, 12.3)

**Đạt khi tất cả điều kiện sau đúng:**
- 100% case Critical và High-risk đã chạy; không còn Critical/High mở.
- Pass rate ≥ 95% trên các case đã chạy.
- Không có 500 không mong đợi trong smoke, workflow, attachments, settings, reports.
- Role matrix, full workflow, upload/download, PDF, đổi mật khẩu, regression đều PASS.
- Mọi BLOCKED có quyết định rõ; mọi lỗi đã có retest; Test Summary ghi commit cuối và khuyến nghị.

**Công thức (theo tài liệu gốc):**
- Executed = PASS + FAIL + BLOCKED
- Pass rate = PASS / (PASS + FAIL) × 100% (BLOCKED **không** nằm ở mẫu số)
- Coverage = số case đã chạy / 126 × 100%
- Reopen rate = defect reopened / defect đã retest × 100%
- Khuyến nghị: `GO`, `GO WITH KNOWN RISKS` hoặc `NO-GO` kèm lý do

---

## 10. Kiểm chứng

```powershell
# Trước tiên: xác nhận DB đang trỏ vào _test (guard trong conftest cũng chặn cứng)
Select-String -Path .env, backend\.env -Pattern "MYSQL_DATABASE"

python -m compileall backend frontend tests
pytest tests/api tests/integration -v --tb=short
python tests/run_role_based_tests.py
```

Sau khi chạy: đối chiếu `evidence/results.csv` với ma trận mục 5 (đủ 126 dòng, không case nào thiếu trạng thái), mở PDF/XLSX xuất ra bằng tay, và hoàn thành checklist bàn giao trước khi ký Go/No-Go.
