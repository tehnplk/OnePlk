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
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8").strip().lower()
    print(f"Received message: '{payload}' on topic: '{msg.topic}'")

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
