import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv
from paho.mqtt import client as mqtt
import send_ipd
import send_icu
import send_or
from send_log import log_send, ensure_log_file

load_dotenv()

HOSPCODE = os.getenv("HOSPCODE", "00001")
ensure_log_file()  # auto-create log file on client start

# MQTT Settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "oneplk/command")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Rate Limiting (seconds between same command)
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "5"))
_last_command_time: dict[str, float] = {}


def resolve_client_id(argv: list[str]) -> str:
    if len(argv) > 1 and argv[1]:
        return argv[1]
    return os.getenv("MQTT_CLIENT_ID") or HOSPCODE or f"oneplk-{os.getpid()}"


MQTT_CLIENT_ID = resolve_client_id(sys.argv)


def on_connect(client, userdata, flags, reason_code, properties=None):
    rc = getattr(reason_code, "value", reason_code)
    if rc == 0:
        print(f"Connected to MQTT Broker: {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect: {reason_code} (Code: {rc})")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8").strip().lower()
    print(f"Received message: '{payload}' on topic: '{msg.topic}'")

    # Rate limiting - prevent command flooding
    now = time.time()
    if payload in _last_command_time:
        elapsed = now - _last_command_time[payload]
        if elapsed < RATE_LIMIT_SECONDS:
            print(f"Rate limited: '{payload}' (wait {RATE_LIMIT_SECONDS - elapsed:.1f}s)")
            return
    _last_command_time[payload] = now

    command_dt = ""
    send_status = "fail"
    send_success_dt = ""
    error_reason = ""
    func_name = ""
    command = ""

    match payload:
        case "icu":
            command = "icu"
            func_name = "send_icu"
            command_dt, send_status, send_success_dt, error_reason = send_icu.send()
        case "ipd":
            command = "ipd"
            func_name = "send_ipd"
            command_dt, send_status, send_success_dt, error_reason = send_ipd.send()
        case "or":
            command = "or"
            func_name = "send_or"
            command_dt, send_status, send_success_dt, error_reason = send_or.send()
        case _:
            print(f"Unknown command: '{payload}' (ignored)")
            return

    log_send(command, func_name, command_dt, send_status, send_success_dt, error_reason)


def run_mqtt():
    print(f"Starting MQTT Client... Broker: {MQTT_BROKER}:{MQTT_PORT}, Topic: {MQTT_TOPIC}")
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    if MQTT_PORT == 8883:
        import ssl
        cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emqxsl-ca.crt")
        if os.path.exists(cert_path):
            print(f"Using CA certificate: {cert_path}")
            client.tls_set(ca_certs=cert_path)
        else:
            print("Warning: CA certificate not found. Using insecure SSL.")
            client.tls_set(cert_reqs=ssl.CERT_NONE)
            client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            break
        except Exception as e:
            print(f"MQTT Connection failed: {e}. Retrying in 5s...")
            time.sleep(5)

    client.loop_forever()


if __name__ == "__main__":
    run_mqtt()
