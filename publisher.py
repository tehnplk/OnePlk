import os
import sys
from paho.mqtt import publish
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.emqx.io")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "oneplk/command")

def send_command(command):
    print(f"Publishing '{command}' to {MQTT_BROKER}:{MQTT_PORT} topic {MQTT_TOPIC}...")
    try:
        publish.single(MQTT_TOPIC, payload=command, hostname=MQTT_BROKER, port=MQTT_PORT)
        print("Successfully published.")
    except Exception as e:
        print(f"Failed to publish: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
    else:
        print("Usage: uv run python tools/test_publisher.py [icu|ipd|or]")
        print("Defaulting to 'icu'...")
        cmd = "icu"
    
    send_command(cmd)
