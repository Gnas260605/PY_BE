from __future__ import annotations

from typing import Any

from mysql.connector import MySQLConnection


USER_COLUMNS = """
    id,
    username,
    ho_ten,
    email,
    vai_tro,
    trang_thai,
    created_at,
    updated_at
"""


def get_user_by_username(
    connection: MySQLConnection, username: str
) -> dict[str, Any] | None:
    query = f"""
        SELECT
            {USER_COLUMNS},
            password_hash
        FROM USERS
        WHERE username = %s
        LIMIT 1
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchone()


def get_user_by_id(connection: MySQLConnection, user_id: int) -> dict[str, Any] | None:
    query = f"""
        SELECT {USER_COLUMNS}
        FROM USERS
        WHERE id = %s
        LIMIT 1
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, (user_id,))
        return cursor.fetchone()


def list_users(
    connection: MySQLConnection,
    *,
    role: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if role:
        conditions.append("vai_tro = %s")
        params.append(role)

    if status:
        conditions.append("trang_thai = %s")
        params.append(status)

    if keyword:
        conditions.append("(username LIKE %s OR ho_ten LIKE %s OR email LIKE %s)")
        like_value = f"%{keyword}%"
        params.extend([like_value, like_value, like_value])

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT {USER_COLUMNS}
        FROM USERS
        {where_clause}
        ORDER BY id ASC
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchall()


def find_duplicate_user(
    connection: MySQLConnection,
    *,
    username: str | None = None,
    email: str | None = None,
    exclude_user_id: int | None = None,
) -> dict[str, Any] | None:
    checks: list[str] = []
    params: list[Any] = []

    if username is not None:
        checks.append("username = %s")
        params.append(username)

    if email is not None:
        checks.append("email = %s")
        params.append(email)

    if not checks:
        return None

    where_clause = " OR ".join(checks)
    exclusion_clause = ""
    if exclude_user_id is not None:
        exclusion_clause = " AND id <> %s"
        params.append(exclude_user_id)

    query = f"""
        SELECT id, username, email
        FROM USERS
        WHERE ({where_clause}){exclusion_clause}
        LIMIT 1
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchone()


def create_user(
    connection: MySQLConnection,
    *,
    username: str,
    password_hash: str,
    ho_ten: str,
    email: str | None,
    vai_tro: str,
    trang_thai: str,
) -> int:
    query = """
        INSERT INTO USERS (
            username,
            password_hash,
            ho_ten,
            email,
            vai_tro,
            trang_thai
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (username, password_hash, ho_ten, email, vai_tro, trang_thai),
        )
        return int(cursor.lastrowid)


def update_user(
    connection: MySQLConnection,
    user_id: int,
    fields: dict[str, Any],
) -> None:
    assignments = ", ".join(f"{column} = %s" for column in fields)
    params = list(fields.values()) + [user_id]
    query = f"""
        UPDATE USERS
        SET {assignments}
        WHERE id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, tuple(params))


def update_user_status(connection: MySQLConnection, user_id: int, status: str) -> None:
    query = """
        UPDATE USERS
        SET trang_thai = %s
        WHERE id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (status, user_id))
