from __future__ import annotations

from typing import Any

from mysql.connector import MySQLConnection


TICKET_SELECT = """
    t.id,
    t.tieu_de,
    t.mo_ta,
    t.loai_yeu_cau,
    t.muc_do_uu_tien,
    t.trang_thai,
    t.user_id,
    t.device_id,
    t.technician_id,
    t.created_at,
    t.updated_at,
    t.resolved_at,
    t.closed_at
"""


def _map_ticket_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "id": row["id"],
        "title": row["tieu_de"],
        "description": row["mo_ta"],
        "category": row["loai_yeu_cau"],
        "priority": row["muc_do_uu_tien"],
        "status": row["trang_thai"],
        "user_id": row["user_id"],
        "device_id": row["device_id"],
        "technician_id": row["technician_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "resolved_at": row["resolved_at"],
        "closed_at": row["closed_at"],
    }


def create_ticket(
    connection: MySQLConnection,
    *,
    title: str,
    description: str,
    category: str,
    priority: str,
    user_id: int,
    device_id: int | None,
) -> int:
    query = """
        INSERT INTO TICKETS (
            tieu_de,
            mo_ta,
            loai_yeu_cau,
            muc_do_uu_tien,
            trang_thai,
            user_id,
            device_id,
            technician_id
        )
        VALUES (%s, %s, %s, %s, 'OPEN', %s, %s, NULL)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (title, description, category, priority, user_id, device_id),
        )
        return int(cursor.lastrowid)


def insert_ticket_history(
    connection: MySQLConnection,
    *,
    ticket_id: int,
    actor_user_id: int,
    action: str,
    old_status: str | None,
    new_status: str | None,
    detail: str | None,
) -> None:
    query = """
        INSERT INTO TICKET_HISTORY (
            ticket_id,
            nguoi_thuc_hien_id,
            hanh_dong,
            trang_thai_cu,
            trang_thai_moi,
            chi_tiet_cap_nhat
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (ticket_id, actor_user_id, action, old_status, new_status, detail),
        )


def device_exists(connection: MySQLConnection, device_id: int) -> bool:
    query = "SELECT id FROM DEVICES WHERE id = %s LIMIT 1"
    with connection.cursor() as cursor:
        cursor.execute(query, (device_id,))
        return cursor.fetchone() is not None


def get_ticket_by_id(connection: MySQLConnection, ticket_id: int) -> dict[str, Any] | None:
    query = f"""
        SELECT {TICKET_SELECT}
        FROM TICKETS t
        WHERE t.id = %s
        LIMIT 1
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, (ticket_id,))
        row = cursor.fetchone()
        return _map_ticket_row(row)


def list_tickets(
    connection: MySQLConnection,
    *,
    role: str,
    current_user_id: int,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    technician_id: int | None = None,
    user_id: int | None = None,
    keyword: str | None = None,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if role == "USER":
        conditions.append("t.user_id = %s")
        params.append(current_user_id)
    elif role == "TECHNICIAN":
        conditions.append("t.technician_id = %s")
        params.append(current_user_id)

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

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT {TICKET_SELECT}
        FROM TICKETS t
        {where_clause}
        ORDER BY t.id ASC
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [_map_ticket_row(row) for row in rows]


def get_ticket_detail(connection: MySQLConnection, ticket_id: int) -> dict[str, Any] | None:
    query = """
        SELECT
            t.id,
            t.tieu_de,
            t.mo_ta,
            t.loai_yeu_cau,
            t.muc_do_uu_tien,
            t.trang_thai,
            t.user_id,
            t.device_id,
            t.technician_id,
            t.created_at,
            t.updated_at,
            t.resolved_at,
            t.closed_at,
            cu.id AS creator_id,
            cu.username AS creator_username,
            cu.ho_ten AS creator_ho_ten,
            cu.email AS creator_email,
            cu.vai_tro AS creator_vai_tro,
            cu.trang_thai AS creator_trang_thai,
            d.id AS device_ref_id,
            d.ma_thiet_bi AS device_ma_thiet_bi,
            d.ten_thiet_bi AS device_ten_thiet_bi,
            d.loai_thiet_bi AS device_loai_thiet_bi,
            d.vi_tri AS device_vi_tri,
            d.trang_thai AS device_trang_thai,
            d.mo_ta AS device_mo_ta,
            tu.id AS tech_id,
            tu.username AS tech_username,
            tu.ho_ten AS tech_ho_ten,
            tu.email AS tech_email,
            tu.vai_tro AS tech_vai_tro,
            tu.trang_thai AS tech_trang_thai
        FROM TICKETS t
        JOIN USERS cu ON cu.id = t.user_id
        LEFT JOIN DEVICES d ON d.id = t.device_id
        LEFT JOIN USERS tu ON tu.id = t.technician_id
        WHERE t.id = %s
        LIMIT 1
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, (ticket_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "title": row["tieu_de"],
            "description": row["mo_ta"],
            "category": row["loai_yeu_cau"],
            "priority": row["muc_do_uu_tien"],
            "status": row["trang_thai"],
            "user_id": row["user_id"],
            "device_id": row["device_id"],
            "technician_id": row["technician_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "resolved_at": row["resolved_at"],
            "closed_at": row["closed_at"],
            "creator": {
                "id": row["creator_id"],
                "username": row["creator_username"],
                "ho_ten": row["creator_ho_ten"],
                "email": row["creator_email"],
                "vai_tro": row["creator_vai_tro"],
                "trang_thai": row["creator_trang_thai"],
            },
            "device": None
            if row["device_ref_id"] is None
            else {
                "id": row["device_ref_id"],
                "ma_thiet_bi": row["device_ma_thiet_bi"],
                "ten_thiet_bi": row["device_ten_thiet_bi"],
                "loai_thiet_bi": row["device_loai_thiet_bi"],
                "vi_tri": row["device_vi_tri"],
                "trang_thai": row["device_trang_thai"],
                "mo_ta": row["device_mo_ta"],
            },
            "technician": None
            if row["tech_id"] is None
            else {
                "id": row["tech_id"],
                "username": row["tech_username"],
                "ho_ten": row["tech_ho_ten"],
                "email": row["tech_email"],
                "vai_tro": row["tech_vai_tro"],
                "trang_thai": row["tech_trang_thai"],
            },
        }


def get_user_basic_by_id(connection: MySQLConnection, user_id: int) -> dict[str, Any] | None:
    query = """
        SELECT id, username, ho_ten, email, vai_tro, trang_thai
        FROM USERS
        WHERE id = %s
        LIMIT 1
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, (user_id,))
        return cursor.fetchone()


def update_ticket_fields(
    connection: MySQLConnection,
    ticket_id: int,
    fields: dict[str, Any],
) -> None:
    assignments: list[str] = []
    params: list[Any] = []
    for column, value in fields.items():
        if value == "CURRENT_TIMESTAMP":
            assignments.append(f"{column} = CURRENT_TIMESTAMP")
        else:
            assignments.append(f"{column} = %s")
            params.append(value)
    params.append(ticket_id)
    query = f"""
        UPDATE TICKETS
        SET {", ".join(assignments)}
        WHERE id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, tuple(params))


def get_ticket_history(connection: MySQLConnection, ticket_id: int) -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            hanh_dong,
            trang_thai_cu,
            trang_thai_moi,
            chi_tiet_cap_nhat,
            nguoi_thuc_hien_id,
            thoi_gian
        FROM TICKET_HISTORY
        WHERE ticket_id = %s
        ORDER BY thoi_gian ASC, id ASC
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, (ticket_id,))
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "action": row["hanh_dong"],
                "old_status": row["trang_thai_cu"],
                "new_status": row["trang_thai_moi"],
                "detail": row["chi_tiet_cap_nhat"],
                "performed_by": row["nguoi_thuc_hien_id"],
                "performed_at": row["thoi_gian"],
            }
            for row in rows
        ]
