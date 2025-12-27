import os
from paho.mqtt import publish
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.emqx.io")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "oneplk/command")

print(f"Publishing 'icu' to {MQTT_BROKER}:{MQTT_PORT} topic {MQTT_TOPIC}...")
publish.single(MQTT_TOPIC, payload="icu", hostname=MQTT_BROKER, port=MQTT_PORT)
print("Done.")
