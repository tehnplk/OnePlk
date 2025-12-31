import os
import sys
import ssl
from paho.mqtt import client as mqtt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "oneplk/command")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

def send_command(command):
    print(f"Publishing '{command}' to {MQTT_BROKER}:{MQTT_PORT} topic {MQTT_TOPIC}...")
    
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=f"pub-{os.getpid()}")
    
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    if MQTT_PORT == 8883:
        cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emqxsl-ca.crt")
        if os.path.exists(cert_path):
            print(f"Using CA certificate: {cert_path}")
            client.tls_set(ca_certs=cert_path)
        else:
            client.tls_set(cert_reqs=ssl.CERT_NONE)
            client.tls_insecure_set(True)
        
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        info = client.publish(MQTT_TOPIC, command)
        info.wait_for_publish()
        client.disconnect()
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
