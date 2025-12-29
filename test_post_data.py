import argparse
import os
import time
from datetime import UTC, datetime, timedelta

import requests
from dotenv import load_dotenv
from jose import jwt

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

# JWT config (ต้องตรงกับ server)
JWT_SECRET = "devsecret"
JWT_ALGORITHM = "HS256"
JWT_EXP_SECONDS = 60


def create_token(hospcode: str) -> str:
    """Create JWT token locally"""
    now = datetime.now(UTC)
    payload = {
        "sub": "tester",
        "hospcode": hospcode,
        "iat": now,
        "exp": now + timedelta(seconds=JWT_EXP_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def prepare_data(hospcode: str) -> dict:
    print("[DB] Querying data for OPD ...", end="", flush=True)
    time.sleep(0.5)
    print(" ok")
    return {"message": f"OPD data from {hospcode}"}


def send(hospcode: str) -> tuple[str, str, str]:
    now_utc = datetime.now(UTC)
    command_dt = now_utc.strftime("%Y-%m-%d %H:%M:%S%z")
    send_status = "fail"
    send_success_dt = ""

    token = create_token(hospcode)
    print(f"[INFO] Created JWT (hospcode={hospcode})")

    payload = prepare_data(hospcode)

    print(f"send_opd -> {BASE_URL}/data")
    try:
        resp = requests.post(
            f"{BASE_URL}/data",
            json=payload,
            timeout=TIMEOUT,
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"send_opd status={resp.status_code}")
        if resp.ok:
            send_status = "success"
            send_success_dt = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S%z")
        else:
            print(f"send_opd error: {resp.json()}")
    except Exception as exc:
        print(f"send_opd failed: {exc}")
    return command_dt, send_status, send_success_dt


def main():
    parser = argparse.ArgumentParser(description="Test JWT authentication with server")
    parser.add_argument("hospcode", help="Hospital code (e.g., 11251, 11252)")
    args = parser.parse_args()
    send(args.hospcode)


if __name__ == "__main__":
    main()
