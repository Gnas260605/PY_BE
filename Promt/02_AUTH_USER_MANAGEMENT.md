# PROMPT 02 – AUTH + USER MANAGEMENT

Đọc Master Prompt + API Contract + DB schema. Chỉ sửa `/backend/**`.

## Login – POST /api/login
1. parse/validate body;
2. query USERS bằng identifier contract;
3. user không có → 401;
4. inactive → chặn;
5. bcrypt verify password_hash;
6. sai → 401;
7. đúng → user/role/auth state theo contract;
8. không trả password_hash;
9. log success/fail nhưng không log password.
Không tự invent JWT/session.

## GET /api/users
ADMIN only. Hỗ trợ role/status/keyword nếu contract có. Empty → 200 []. Không trả hash.

## POST /api/users
ADMIN only. Validate username/password/ho_ten/role; duplicate username/email → 409; bcrypt hash; INSERT; 201.

## GET /api/users/{id}
ADMIN only. 200/404. Không trả hash.

## PATCH /api/users/{id}
ADMIN only. Chỉ allowed fields. Duplicate → 409. Không reset password qua endpoint này nếu contract không khóa.

## PATCH /api/users/{id}/status
ADMIN only. ACTIVE/INACTIVE. Không xóa vật lý user.

Verify thật: login valid/wrong/inactive; create; duplicate; list; detail; update; disable; login disabled; enable.
