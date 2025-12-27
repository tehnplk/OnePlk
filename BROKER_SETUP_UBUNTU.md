# MQTT Broker Setup on Ubuntu (Mosquitto)

## Prerequisites
- Ubuntu 22.04+ (root or sudo)
- Open ports: 1883 (MQTT), 8883 (MQTT over TLS)

## 1) Install Mosquitto
```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
sudo systemctl status mosquitto --no-pager
```

## 2) Basic local test (no TLS)
```bash
# Terminal A (subscriber)
mosquitto_sub -t "test/topic" -v
# Terminal B (publisher)
mosquitto_pub -t "test/topic" -m "hello"
```
Expect to see `test/topic hello` in Terminal A.

## 3) Create a dedicated user/password
```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd appuser
# enter strong password
```

## 4) Configure listener with auth (no TLS)
Create `/etc/mosquitto/conf.d/auth.conf`:
```bash
sudo tee /etc/mosquitto/conf.d/auth.conf >/dev/null <<'EOF'
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
EOF
```
Reload:
```bash
sudo systemctl restart mosquitto
```
Test auth:
```bash
mosquitto_sub -h localhost -p 1883 -t "test/topic" -u appuser -P 'your_password' -v
mosquitto_pub -h localhost -p 1883 -t "test/topic" -u appuser -P 'your_password' -m "hello-auth"
```

## 5) Enable TLS (recommended for remote clients)
Create CA and server certs (simplified self-signed example):
```bash
sudo mkdir -p /etc/mosquitto/certs
cd /etc/mosquitto/certs
sudo openssl req -new -x509 -days 3650 -keyout ca.key -out ca.crt -nodes -subj "/CN=MyMQTT-CA"
sudo openssl req -new -keyout server.key -out server.csr -nodes -subj "/CN=$(hostname -f)"
sudo openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650
sudo chmod 640 server.key
```
Config TLS listener `/etc/mosquitto/conf.d/tls.conf`:
```bash
sudo tee /etc/mosquitto/conf.d/tls.conf >/dev/null <<'EOF'
listener 8883
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
allow_anonymous false
password_file /etc/mosquitto/passwd
EOF
```
Reload:
```bash
sudo systemctl restart mosquitto
```
Test TLS:
```bash
mosquitto_sub -h <server_ip> -p 8883 --cafile /etc/mosquitto/certs/ca.crt \
  -t "test/topic" -u appuser -P 'your_password' -v
mosquitto_pub -h <server_ip> -p 8883 --cafile /etc/mosquitto/certs/ca.crt \
  -t "test/topic" -u appuser -P 'your_password' -m "hello-tls"
```

## 6) Harden
- Use a real CA or ACME (Let’s Encrypt) for public endpoints
- Restrict to specific networks with firewall/`listener` + `bind_address`
- Consider per-tenant topics and ACLs (`acl_file`) if multi-tenant
- Set `persistence true` if you need retained/offline storage
- Set `autosave_interval` to reduce disk churn

## 7) Client configuration hints (paho-mqtt)
```python
import paho.mqtt.client as mqtt

client = mqtt.Client(client_id="oneplk-<hospcode>")
client.username_pw_set("appuser", "your_password")
client.tls_set(ca_certs="/path/to/ca.crt")  # for TLS listener 8883
client.connect("<server_ip>", 8883, 60)
client.loop_start()
client.publish("oneplk/command", "icu")
```

## 8) Firewall / cloud SG
- Open only the ports you use: 1883 (non-TLS) or 8883 (TLS)
- Prefer TLS only when exposed to the internet

## 9) Service control
```bash
sudo systemctl status mosquitto
sudo systemctl restart mosquitto
sudo journalctl -u mosquitto -n 200 --no-pager
```
