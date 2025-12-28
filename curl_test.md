# Curl Test Guide (PowerShell)

ใช้ทดสอบ POST ไปยัง FastAPI server (endpoint `/ipd`, `/icu`, `/or`).

## รูปแบบคำสั่งพื้นฐาน
```powershell
curl.exe --% -X POST http://localhost:8000/<path> -H "Content-Type: application/json" -d "{\"key\":\"value\"}"
```
> ใช้ `--%` (stop-parsing) ใน PowerShell เพื่อปิดการตีความ string เพิ่มเติม ลดปัญหา JSONDecodeError

## ตัวอย่างที่ใช้งานได้

### 1) ทดสอบ `/ipd`
```powershell
curl.exe --% -X POST http://localhost:8000/ipd -H "Content-Type: application/json" -d "{\"test\":\"ipd_check\"}"
```

### 2) ทดสอบ `/icu`
```powershell
curl.exe --% -X POST http://localhost:8000/icu -H "Content-Type: application/json" -d "{\"test\":\"icu_check\"}"
```

### 3) ทดสอบ `/or`
```powershell
curl.exe --% -X POST http://localhost:8000/or -H "Content-Type: application/json" -d "{\"test\":\"or_check\"}"
```

## เคล็ดลับ
- ใช้ `localhost` หรือ `127.0.0.1` ได้เหมือนกัน: `http://127.0.0.1:8000/ipd`
- ถ้าเจอ error `Port number was not a decimal number ...` หรือ `Expecting property name enclosed in double quotes` ให้ใช้ `--%` และตรวจสอบว่า JSON อยู่ในรูปแบบ `{\"key\":\"value\"}`
- เซิร์ฟเวอร์ต้องกำลังรันอยู่ (uvicorn) เช่น: `uv run uvicorn server:app --host 0.0.0.0 --port 8000 --reload` ก่อนค่อยยิง curl

## ตรวจสอบผลลัพธ์
- รหัสตอบกลับควรเป็น `200 OK`
- ค่าที่ส่งมาจะสะท้อนใน `received` ของ response JSON
- ที่ console ฝั่งเซิร์ฟเวอร์จะเห็น log `[IPD] Received: ...` (หรือ ICU/OR ตาม path)
