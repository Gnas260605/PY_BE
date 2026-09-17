from __future__ import annotations

from typing import Any

from mysql.connector import MySQLConnection


def get_technician_workload(connection: MySQLConnection) -> list[dict[str, Any]]:
    query = """
        SELECT
            u.id AS technician_id,
            u.username,
            u.ho_ten,
            u.email,
            COALESCE(SUM(CASE WHEN t.trang_thai IN ('ASSIGNED', 'IN_PROGRESS') THEN 1 ELSE 0 END), 0)
                AS active_tickets,
            COALESCE(SUM(CASE WHEN t.trang_thai = 'RESOLVED' THEN 1 ELSE 0 END), 0)
                AS resolved_tickets,
            COALESCE(SUM(CASE WHEN t.trang_thai = 'CLOSED' THEN 1 ELSE 0 END), 0)
                AS closed_tickets,
            COUNT(t.id) AS total_assigned_tickets
        FROM USERS u
        LEFT JOIN TICKETS t ON t.technician_id = u.id
        WHERE u.vai_tro = 'TECHNICIAN'
        GROUP BY u.id, u.username, u.ho_ten, u.email
        ORDER BY active_tickets DESC, resolved_tickets DESC, u.id ASC
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        return [
            {
                "technician_id": row["technician_id"],
                "username": row["username"],
                "ho_ten": row["ho_ten"],
                "email": row["email"],
                "active_tickets": int(row["active_tickets"]),
                "resolved_tickets": int(row["resolved_tickets"]),
                "closed_tickets": int(row["closed_tickets"]),
                "total_assigned_tickets": int(row["total_assigned_tickets"]),
            }
            for row in rows
        ]


def list_tickets_for_export(
    connection: MySQLConnection,
    *,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    technician_id: int | None = None,
    user_id: int | None = None,
    keyword: str | None = None,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if status:
        conditions.append("t.trang_thai = %s")
        params.append(status)
    if priority:
        conditions.append("t.muc_do_uu_tien = %s")
        params.append(priority)
    if category:
        conditions.append("t.loai_yeu_cau = %s")
        params.append(category)
    if technician_id is not None:
        conditions.append("t.technician_id = %s")
        params.append(technician_id)
    if user_id is not None:
        conditions.append("t.user_id = %s")
        params.append(user_id)
    if keyword:
        conditions.append("(t.tieu_de LIKE %s OR t.mo_ta LIKE %s)")
        like_value = f"%{keyword}%"
        params.extend([like_value, like_value])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT
            t.id,
            t.tieu_de AS title,
            t.mo_ta AS description,
            t.loai_yeu_cau AS category,
            t.muc_do_uu_tien AS priority,
            t.trang_thai AS status,
            t.user_id,
            cu.ho_ten AS creator_name,
            t.device_id,
            d.ma_thiet_bi AS device_code,
            d.ten_thiet_bi AS device_name,
            t.technician_id,
            tu.ho_ten AS technician_name,
            t.created_at,
            t.updated_at,
            t.resolved_at,
            t.closed_at
        FROM TICKETS t
        JOIN USERS cu ON cu.id = t.user_id
        LEFT JOIN DEVICES d ON d.id = t.device_id
        LEFT JOIN USERS tu ON tu.id = t.technician_id
        {where_clause}
        ORDER BY t.created_at DESC, t.id DESC
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
