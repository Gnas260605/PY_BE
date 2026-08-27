from __future__ import annotations

from typing import Any

from mysql.connector import MySQLConnection


DEVICE_COLUMNS = """
    id,
    ma_thiet_bi,
    ten_thiet_bi,
    loai_thiet_bi,
    vi_tri,
    trang_thai,
    mo_ta,
    created_at,
    updated_at
"""


def list_devices(
    connection: MySQLConnection,
    *,
    status: str | None = None,
    device_type: str | None = None,
    keyword: str | None = None,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if status:
        conditions.append("trang_thai = %s")
        params.append(status)

    if device_type:
        conditions.append("loai_thiet_bi = %s")
        params.append(device_type)

    if keyword:
        conditions.append("(ma_thiet_bi LIKE %s OR ten_thiet_bi LIKE %s OR vi_tri LIKE %s)")
        like_value = f"%{keyword}%"
        params.extend([like_value, like_value, like_value])

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT {DEVICE_COLUMNS}
        FROM DEVICES
        {where_clause}
        ORDER BY id ASC
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchall()


def get_device_by_id(connection: MySQLConnection, device_id: int) -> dict[str, Any] | None:
    query = f"""
        SELECT {DEVICE_COLUMNS}
        FROM DEVICES
        WHERE id = %s
        LIMIT 1
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, (device_id,))
        return cursor.fetchone()


def find_duplicate_device_code(
    connection: MySQLConnection,
    *,
    ma_thiet_bi: str,
    exclude_device_id: int | None = None,
) -> dict[str, Any] | None:
    params: list[Any] = [ma_thiet_bi]
    exclusion_clause = ""
    if exclude_device_id is not None:
        exclusion_clause = " AND id <> %s"
        params.append(exclude_device_id)

    query = f"""
        SELECT {DEVICE_COLUMNS}
        FROM DEVICES
        WHERE ma_thiet_bi = %s{exclusion_clause}
        LIMIT 1
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchone()


def create_device(
    connection: MySQLConnection,
    *,
    ma_thiet_bi: str,
    ten_thiet_bi: str,
    loai_thiet_bi: str | None,
    vi_tri: str | None,
    trang_thai: str,
    mo_ta: str | None,
) -> int:
    query = """
        INSERT INTO DEVICES (
            ma_thiet_bi,
            ten_thiet_bi,
            loai_thiet_bi,
            vi_tri,
            trang_thai,
            mo_ta
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (ma_thiet_bi, ten_thiet_bi, loai_thiet_bi, vi_tri, trang_thai, mo_ta),
        )
        return int(cursor.lastrowid)


def update_device(
    connection: MySQLConnection,
    device_id: int,
    fields: dict[str, Any],
) -> None:
    assignments = ", ".join(f"{column} = %s" for column in fields)
    params = list(fields.values()) + [device_id]
    query = f"""
        UPDATE DEVICES
        SET {assignments}
        WHERE id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, tuple(params))
