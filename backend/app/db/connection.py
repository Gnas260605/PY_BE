from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from typing import Iterator

import mysql.connector
from mysql.connector import MySQLConnection

from app.core.config import get_settings


def get_connection() -> MySQLConnection:
    settings = get_settings()
    return mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=settings.mysql_database,
        user=settings.mysql_user,
        password=settings.mysql_password,
    )


@contextmanager
def connection_scope() -> Iterator[MySQLConnection]:
    connection = get_connection()
    try:
        yield connection
    finally:
        if connection.is_connected():
            connection.close()


def check_connection() -> dict[str, Any]:
    try:
        with connection_scope() as connection:
            connection.ping(reconnect=False, attempts=1, delay=0)
    except mysql.connector.Error as exc:
        return {"ok": False, "detail": str(exc)}
    return {"ok": True, "detail": "connected"}
