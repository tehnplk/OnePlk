from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


app = FastAPI()


def log_received(tag: str, data: dict):
    hospcode = data.get("hospcode", "-")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{tag}] {ts} hospcode={hospcode} data={data}")


@app.post("/ipd")
async def receive_ipd(request: Request):
    data = await request.json()
    log_received("IPD", data)
    return JSONResponse({"status": "ok", "received": data})


@app.post("/icu")
async def receive_icu(request: Request):
    data = await request.json()
    log_received("ICU", data)
    return JSONResponse({"status": "ok", "received": data})


@app.post("/or")
async def receive_or(request: Request):
    data = await request.json()
    log_received("OR", data)
    return JSONResponse({"status": "ok", "received": data})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
