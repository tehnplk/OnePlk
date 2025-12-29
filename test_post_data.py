import argparse
from datetime import UTC, datetime, timedelta

import requests
from jose import jwt

# Config
BASE_URL = "http://localhost:8000"
TIMEOUT = 10
JWT_SECRET = "devsecret"
JWT_ALGORITHM = "HS256"
JWT_EXP_SECONDS = 60


def create_token(hospcode: str) -> str:
    """Create JWT token"""
    now = datetime.now(UTC)
    payload = {
        "sub": "tester",
        "hospcode": hospcode,
        "iat": now,
        "exp": now + timedelta(seconds=JWT_EXP_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def send(hospcode: str) -> None:
    """Send data to server with JWT auth"""
    token = create_token(hospcode)
    print(f"[INFO] Created JWT (hospcode={hospcode})")

    payload = {"message": f"OPD data from {hospcode}"}

    print(f"[SEND] POST {BASE_URL}/data")
    try:
        resp = requests.post(
            f"{BASE_URL}/data",
            json=payload,
            timeout=TIMEOUT,
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"[RESP] status={resp.status_code}")
        if resp.ok:
            print(f"[OK] {resp.json()}")
        else:
            print(f"[ERROR] {resp.json()}")
    except Exception as exc:
        print(f"[FAIL] {exc}")


def main():
    parser = argparse.ArgumentParser(description="Test JWT auth with server")
    parser.add_argument("hospcode", help="Hospital code (e.g., 11251)")
    args = parser.parse_args()
    send(args.hospcode)


if __name__ == "__main__":
    main()
