# PROMPT 03 – DEVICE MANAGEMENT

Đọc Master Prompt + API Contract + DB schema. Chỉ sửa `/backend/**`.

## GET /api/devices
List/filter theo contract: status/type/keyword. Empty → 200 [].

## POST /api/devices
ADMIN only. Validate `ma_thiet_bi`, `ten_thiet_bi`, optional type/location/description/status. Duplicate code → 409. 201.

## GET /api/devices/{id}
200/404.

## PATCH /api/devices/{id}
Chỉ allowed fields. Status phải lấy từ schema thật. Nếu schema đang dùng baseline: ACTIVE, MAINTENANCE, BROKEN, INACTIVE. Invalid → 400. Log nếu log contract yêu cầu.

Authorization ưu tiên API Contract. Không tự mở quyền rộng hơn.

Verify: create, duplicate, list, filter, detail, update info, update status, invalid status, missing id.
