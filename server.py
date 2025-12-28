import os
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

app = FastAPI(title="JWT Auth Server")
security = HTTPBearer(auto_error=True)

JWT_SECRET = os.getenv("JWT_SECRET", "mysecretkey")
JWT_ALGORITHM = "HS256"


class DataPayload(BaseModel):
    hospcode: str
    message: str = ""


def create_jwt_token(sub: str, expires_minutes: int = 60) -> str:
    payload = {
        "sub": sub,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print(f"[AUTH] JWT valid: sub={payload.get('sub')}")
        return payload
    except JWTError as exc:
        print(f"[AUTH] JWT error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/token/{username}")
async def get_token(username: str):
    token = create_jwt_token(sub=username)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/data")
async def receive_data(payload: DataPayload, claims: dict = Depends(verify_jwt)):
    print(f"[DATA] Received from {claims.get('sub')}: {payload}")
    return JSONResponse({
        "status": "ok",
        "user": claims.get("sub"),
        "received": payload.model_dump()
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
