import os
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from jose import jwt

load_dotenv()

HOSPCODE = os.getenv("HOSPCODE", "00000")
ENDPOINT_ICU = os.getenv("END_POINT_ICU", "http://localhost:8000/data")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", "300"))

DEFAULT_DEPARTMENT = "ICU 1"
DEFAULT_BED_TOTAL = 10
DEFAULT_BED_USE = 5


def prepare_data() -> dict:
    print(f"[DB] Querying data for ICU ...", end="", flush=True)
    time.sleep(0.5)
    print(" ok")

    return {
        "hospcode": HOSPCODE,
        "dataset": "ICU",
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
    token = jwt.encode(
        {"sub": HOSPCODE, "iat": datetime.utcnow(), "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_SECONDS)},
        JWT_SECRET,
        algorithm=JWT_ALG,
    )
    print(f"send_icu -> {ENDPOINT_ICU}")
    try:
        resp = requests.post(
            ENDPOINT_ICU,
            json=payload,
            timeout=TIMEOUT,
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"send_icu status={resp.status_code}")
        if resp.ok:
            send_status = "success"
            send_success_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as exc:
        print(f"send_icu failed: {exc}")
    return command_dt, send_status, send_success_dt
