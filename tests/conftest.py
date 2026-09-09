from __future__ import annotations

import os
import sys
from typing import Generator
import pytest

# Ensure environment is configured for testing before loading backend settings
os.environ.setdefault("MYSQL_DATABASE", "cs466_helpdesk_test")
os.environ.setdefault("JWT_SECRET_KEY", "cs466-helpdesk-jwt-secret-key-test")
os.environ.setdefault("APP_ENV", "testing")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from starlette.testclient import TestClient  # type: ignore

try:
    from app.main import app  # type: ignore
    from app.core.security import create_access_token  # type: ignore
except ImportError:
    from backend.app.main import app  # type: ignore
    from backend.app.core.security import create_access_token  # type: ignore

try:
    from tests.helpers import BugReportCollector, is_database_connected  # type: ignore
    from tests.run_role_based_tests import reset_database, ensure_test_database  # type: ignore
except ImportError:
    from helpers import BugReportCollector, is_database_connected  # type: ignore
    from run_role_based_tests import reset_database, ensure_test_database  # type: ignore


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def bug_collector() -> BugReportCollector:
    return BugReportCollector()


@pytest.fixture(scope="session")
def admin_token() -> str:
    return create_access_token(user_id=1, username="admin", role="ADMIN")


@pytest.fixture(scope="session")
def tech_token() -> str:
    return create_access_token(user_id=2, username="tech01", role="TECHNICIAN")


@pytest.fixture(scope="session")
def user_token() -> str:
    return create_access_token(user_id=3, username="user01", role="USER")


@pytest.fixture(scope="session")
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def tech_headers(tech_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tech_token}"}


@pytest.fixture(scope="session")
def user_headers(user_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(autouse=False)
def db_reset() -> Generator[None, None, None]:
    """Reset the test database to seed state if database is available."""
    if is_database_connected():
        ensure_test_database()
        reset_database()
    yield
