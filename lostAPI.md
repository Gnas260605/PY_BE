# Danh sách các API còn thiếu (Lost APIs)

> **Lưu ý:** Ghi chú lại tất cả các chức năng/màn hình trên Frontend cần lấy dữ liệu hoặc thao tác nhưng Backend chưa cung cấp API tương ứng tại đây.

| STT | Chức năng / Màn hình | Yêu cầu dữ liệu / Thao tác | Mô tả chi tiết | Trạng thái |
|---|---|---|---|---|
| 1 | Chi tiết Ticket (Comment) | Lấy danh sách bình luận | `GET /tickets/{id}/comments` - Lấy danh sách trao đổi/phản hồi trong 1 ticket | ✅ Đã hoàn thành (200 OK) |
| 2 | Chi tiết Ticket (Comment) | Đăng bình luận mới | `POST /tickets/{id}/comments` - Gửi bình luận mới vào ticket | ✅ Đã hoàn thành (201 Created) |

*(Đã giải quyết 100% danh sách API còn thiếu)*
