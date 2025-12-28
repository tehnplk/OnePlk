import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt


app = FastAPI()
security = HTTPBearer(auto_error=True)

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM = os.getenv("JWT_ALG", "HS256")


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def log_received(tag: str, data: dict, claims: dict | None = None):
    hospcode = data.get("hospcode", "-")
    sub = claims.get("sub", "-") if claims else "-"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{tag}] {ts} hospcode={hospcode} sub={sub} data={data}")


@app.post("/ipd")
async def receive_ipd(request: Request, claims=Depends(verify_jwt)):
    data = await request.json()
    log_received("IPD", data, claims)
    return JSONResponse({"status": "ok", "received": data})


@app.post("/icu")
async def receive_icu(request: Request, claims=Depends(verify_jwt)):
    data = await request.json()
    log_received("ICU", data, claims)
    return JSONResponse({"status": "ok", "received": data})


@app.post("/or")
async def receive_or(request: Request, claims=Depends(verify_jwt)):
    data = await request.json()
    log_received("OR", data, claims)
    return JSONResponse({"status": "ok", "received": data})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
