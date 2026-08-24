/**
 * CS466 Helpdesk - Frontend API Service Client
 * Base URL: http://127.0.0.1:8000/api
 */

const API_BASE_URL = "http://127.0.0.1:8000/api";

/**
 * Generic Fetch Wrapper with Bearer Token Injection and Error Handling
 */
async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMessage = data.detail || `HTTP Error ${response.status}`;
    const error = new Error(errorMessage);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const authApi = {
  /**
   * POST /api/login - Đăng nhập hệ thống
   */
  async login(username, password) {
    const data = await apiFetch("/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    const token = data.access_token;
    if (token) {
      localStorage.setItem("access_token", token);
      localStorage.setItem("current_user", JSON.stringify(data.user));
    }
    return data;
  },


  /**
   * Đăng xuất xóa token
   */
  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("current_user");
  },

  /**
   * Lấy thông tin user hiện tại từ local storage
   */
  getCurrentUser() {
    const userStr = localStorage.getItem("current_user");
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Kiểm tra đã đăng nhập chưa
   */
  isAuthenticated() {
    return !!localStorage.getItem("access_token");
  },
};

export const usersApi = {
  /**
   * GET /api/users - Lấy danh sách users (Admin only)
   * @param {Object} params { role, status, keyword }
   */
  async listUsers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`/users${query ? `?${query}` : ""}`);
  },

  /**
   * POST /api/users - Tạo user mới (Admin only)
   * @param {Object} userData { username, password, ho_ten, email, vai_tro }
   */
  async createUser(userData) {
    return apiFetch("/users", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  /**
   * GET /api/users/:id - Lấy chi tiết user (Admin only)
   */
  async getUser(userId) {
    return apiFetch(`/users/${userId}`);
  },

  /**
   * PATCH /api/users/:id - Cập nhật user (Admin only)
   * @param {Object} updates { ho_ten, email, vai_tro }
   */
  async updateUser(userId, updates) {
    return apiFetch(`/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
  },

  /**
   * PATCH /api/users/:id/status - Cập nhật trạng thái user (Admin only)
   * @param {string} status "ACTIVE" | "INACTIVE"
   */
  async updateUserStatus(userId, status) {
    return apiFetch(`/users/${userId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  },
};

export const devicesApi = {
  /**
   * GET /api/devices - Lấy danh sách thiết bị
   * @param {Object} params { status, type, keyword }
   */
  async listDevices(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`/devices${query ? `?${query}` : ""}`);
  },

  /**
   * POST /api/devices - Thêm thiết bị mới (Admin only)
   * @param {Object} deviceData { ma_thiet_bi, ten_thiet_bi, loai_thiet_bi, vi_tri, trang_thai, mo_ta }
   */
  async createDevice(deviceData) {
    return apiFetch("/devices", {
      method: "POST",
      body: JSON.stringify(deviceData),
    });
  },

  /**
   * GET /api/devices/:id - Lấy chi tiết thiết bị
   */
  async getDevice(deviceId) {
    return apiFetch(`/devices/${deviceId}`);
  },

  /**
   * PATCH /api/devices/:id - Cập nhật thiết bị
   * @param {Object} updates { ten_thiet_bi, loai_thiet_bi, vi_tri, trang_thai, mo_ta }
   */
  async updateDevice(deviceId, updates) {
    return apiFetch(`/devices/${deviceId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
  },
};

export const ticketsApi = {
  /**
   * GET /api/tickets - Lấy danh sách ticket
   * @param {Object} params { status, priority, category, technician_id, user_id, keyword }
   */
  async listTickets(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`/tickets${query ? `?${query}` : ""}`);
  },

  /**
   * POST /api/tickets - Tạo ticket mới
   * @param {Object} ticketData { title, description, device_id, category, priority }
   */
  async createTicket(ticketData) {
    return apiFetch("/tickets", {
      method: "POST",
      body: JSON.stringify(ticketData),
    });
  },

  /**
   * GET /api/tickets/:id - Lấy chi tiết ticket
   */
  async getTicket(ticketId) {
    return apiFetch(`/tickets/${ticketId}`);
  },

  /**
   * PATCH /api/tickets/:id - Cập nhật / Phân loại ticket
   * @param {Object} updates { title, description, category, priority }
   */
  async updateTicket(ticketId, updates) {
    return apiFetch(`/tickets/${ticketId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
  },

  /**
   * PATCH /api/tickets/:id/assign - Gán kỹ thuật viên (Admin only)
   * @param {number} technicianId ID của kỹ thuật viên
   */
  async assignTechnician(ticketId, technicianId) {
    return apiFetch(`/tickets/${ticketId}/assign`, {
      method: "PATCH",
      body: JSON.stringify({ technician_id: technicianId }),
    });
  },

  /**
   * PATCH /api/tickets/:id/status - Đổi trạng thái ticket
   * @param {string} status "OPEN" | "ASSIGNED" | "IN_PROGRESS" | "RESOLVED" | "CLOSED"
   */
  async updateTicketStatus(ticketId, status) {
    return apiFetch(`/tickets/${ticketId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  },

  /**
   * PATCH /api/tickets/:id/close - Đóng ticket đã hoàn tất
   * @param {string} note Ghi chú khi đóng
   */
  async closeTicket(ticketId, note = "") {
    return apiFetch(`/tickets/${ticketId}/close`, {
      method: "PATCH",
      body: JSON.stringify({ note }),
    });
  },

  /**
   * GET /api/tickets/:id/history - Lấy lịch sử xử lý của ticket
   */
  async getTicketHistory(ticketId) {
    return apiFetch(`/tickets/${ticketId}/history`);
  },
};

export const systemApi = {
  /**
   * GET /api/health - Kiểm tra tình trạng backend
   */
  async healthCheck() {
    return apiFetch("/health");
  },
};
