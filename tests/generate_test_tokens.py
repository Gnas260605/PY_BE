import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.security import create_access_token, decode_access_token


def main():
    test_users = [
        {"id": 1, "username": "admin", "role": "ADMIN", "desc": "Quản trị hệ thống"},
        {"id": 2, "username": "tech01", "role": "TECHNICIAN", "desc": "Kỹ thuật viên 01"},
        {"id": 3, "username": "user01", "role": "USER", "desc": "Người dùng 01"},
    ]

    print("=" * 70)
    print("CS466 TEST JWT TOKENS (Validity: 480 minutes)")
    print("=" * 70)

    for u in test_users:
        token = create_access_token(user_id=u["id"], username=u["username"], role=u["role"])
        decoded = decode_access_token(token)
        print(f"\n[{u['role']}] - {u['username']} ({u['desc']})")
        print(f"Token: {token}")
        print(f"Header: Authorization: Bearer {token}")
        print(f"Payload: {decoded}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
