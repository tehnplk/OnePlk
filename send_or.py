import os
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from jose import jwt

load_dotenv()

HOSPCODE = os.getenv("HOSPCODE", "00000")
ENDPOINT_OR = os.getenv("END_POINT_OR", "http://localhost:8000/data")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", "300"))

DEFAULT_DEPARTMENT = "OR 1"
DEFAULT_BED_TOTAL = 5
DEFAULT_BED_USE = 2


def prepare_data() -> dict:
    print(f"[DB] Querying data for OR ...", end="", flush=True)
    time.sleep(0.5)
    print(" ok")

    return {
        "hospcode": HOSPCODE,
        "dataset": "OR",
        "department": DEFAULT_DEPARTMENT,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": {
            "bed_total": DEFAULT_BED_TOTAL,
            "bed_use": DEFAULT_BED_USE,
        },
    }


def send() -> tuple[str, str, str, str]:
    """Returns (command_dt, send_status, send_success_dt, error_reason)"""
    command_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_status = "fail"
    send_success_dt = ""
    error_reason = ""

    payload = prepare_data()
    token = jwt.encode(
        {"sub": HOSPCODE, "hospcode": HOSPCODE, "iat": datetime.utcnow(), "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_SECONDS)},
        JWT_SECRET,
        algorithm=JWT_ALG,
    )
    print(f"send_or -> {ENDPOINT_OR}")
    try:
        resp = requests.post(
            ENDPOINT_OR,
            json=payload,
            timeout=TIMEOUT,
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"send_or status={resp.status_code}")
        if resp.ok:
            send_status = "success"
            send_success_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            error_reason = f"HTTP_{resp.status_code}"
    except requests.exceptions.Timeout:
        error_reason = "timeout"
        print(f"send_or failed: timeout")
    except requests.exceptions.ConnectionError:
        error_reason = "connection_error"
        print(f"send_or failed: connection error")
    except Exception as exc:
        error_reason = str(exc)[:50].replace(",", ";")  # limit length & escape comma
        print(f"send_or failed: {exc}")
    return command_dt, send_status, send_success_dt, error_reason

