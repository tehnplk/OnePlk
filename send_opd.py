import os
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from jose import jwt

load_dotenv()

HOSPCODE = os.getenv("HOSPCODE", "00000")
ENDPOINT_OPD = os.getenv("END_POINT_OPD", "http://localhost:8000/data")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", "300"))

DEFAULT_DEPARTMENT = "OPD 1"
DEFAULT_BED_TOTAL = 20
DEFAULT_BED_USE = 8


def prepare_data() -> dict:
    print(f"[DB] Querying data for OPD ...", end="", flush=True)
    time.sleep(0.5)
    print(" ok")

    return {
        "hospcode": HOSPCODE,
        "dataset": "OPD",
        "department": DEFAULT_DEPARTMENT,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": {
            "bed_total": DEFAULT_BED_TOTAL,
            "bed_use": DEFAULT_BED_USE,
        },
    }


def send() -> tuple[str, str, str]:
    command_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_status = "fail"
    send_success_dt = ""

    payload = prepare_data()
    
    invalid_token = "invalid.jwt.token"
    
    print(f"send_opd -> {ENDPOINT_OPD}")
    print(f"[WARNING] Using INVALID JWT token for testing")
    try:
        resp = requests.post(
            ENDPOINT_OPD,
            json=payload,
            timeout=TIMEOUT,
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        print(f"send_opd status={resp.status_code}")
        if resp.ok:
            send_status = "success"
            send_success_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            print(f"send_opd error: {resp.json()}")
    except Exception as exc:
        print(f"send_opd failed: {exc}")
    return command_dt, send_status, send_success_dt


if __name__ == "__main__":
    send()
