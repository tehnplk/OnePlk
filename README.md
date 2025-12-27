# OnePlk

ระบบส่งข้อมูล Dataset (IPD, ICU, OR) ไปยัง Endpoint ที่กำหนด โดยรับคำสั่งผ่าน MQTT

## การตั้งค่า

แก้ไขไฟล์ `.env`:

- `HOSPCODE`: รหัสสถานพยาบาล
- `END_POINT_IPD`: URL สำหรับส่งข้อมูล IPD
- `END_POINT_ICU`: URL สำหรับส่งข้อมูล ICU
- `END_POINT_OR`: URL สำหรับส่งข้อมูล OR
- `MQTT_BROKER`: ที่อยู่ของ MQTT Broker (เช่น `broker.hivemq.com`)
- `MQTT_TOPIC`: Topic ที่ใช้รับคำสั่ง (ค่าเริ่มต้น `oneplk/command`)

## การใช้งาน

ติดตั้งไลบรารี:
```bash
uv sync
```

รัน MQTT Client:
```bash
uv run client.py
```

รัน FastAPI Server:
```bash
uv run python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## การสั่งงานผ่าน MQTT

ส่งข้อความ (Payload) ไปยัง Topic `oneplk/command`:

- `icu` → เรียกฟังก์ชัน `SEND_ICU`
- `ipd` → เรียกฟังก์ชัน `SEND_IPD`
- `or` → เรียกฟังก์ชัน `SEND_OR`
