from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/ipd")
async def receive_ipd(request: Request):
    data = await request.json()
    print("[IPD] Received:", data)
    return JSONResponse({"status": "ok", "received": data})

@app.post("/icu")
async def receive_icu(request: Request):
    data = await request.json()
    print("[ICU] Received:", data)
    return JSONResponse({"status": "ok", "received": data})

@app.post("/or")
async def receive_or(request: Request):
    data = await request.json()
    print("[OR] Received:", data)
    return JSONResponse({"status": "ok", "received": data})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
