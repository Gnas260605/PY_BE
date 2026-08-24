from app.db.connection import check_connection


def get_health_status() -> dict[str, str]:
    # Sprint 1 keeps the endpoint contract minimal while DB smoke remains optional.
    return {"status": "ok"}


def get_database_health() -> dict[str, str | bool]:
    return check_connection()
