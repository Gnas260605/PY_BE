# Kế hoạch thực hiện (Implementation Plan)

## Nguyên tắc chung
1. **Không hard-code:** Tuyệt đối không hard-code dữ liệu. Các thông tin cấu hình (như secret keys, URL, port, v.v.) phải được đọc từ biến môi trường (ví dụ file `.env`).
2. **Sử dụng API có sẵn:** Mọi chức năng giao tiếp giữa Frontend và Backend phải thông qua các RESTful API đã được định nghĩa.
3. **Ghi nhận API thiếu:** Trong quá trình phát triển, nếu phát hiện bất kỳ chức năng nào yêu cầu dữ liệu hoặc thao tác từ phía Backend nhưng chưa có API tương ứng, lập tức ghi chú lại vào file `lostAPI.md` để team Backend bổ sung.

## Các bước triển khai
- Review lại toàn bộ file Frontend (HTML/JS) để đảm bảo dữ liệu đang hiển thị hoặc gửi đi được gọi qua API thay vì sử dụng mock data.
- Đối chiếu với tài liệu `API_INTEGRATION_GUIDE.md` để đảm bảo sử dụng đúng endpoint, method và payload.
- Cập nhật `lostAPI.md` liên tục trong quá trình đối chiếu.
