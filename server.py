from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Any
import os

app = FastAPI(title="JWT Auth Server")
security = HTTPBearer(auto_error=True)

# Config - JWT_SECRET should be set in production!
_default_secret = "devsecret"
JWT_SECRET = os.getenv("JWT_SECRET", _default_secret)
if JWT_SECRET == _default_secret:
    print("⚠️  WARNING: Using default JWT_SECRET. Set JWT_SECRET env var in production!")
JWT_ALGORITHM = os.getenv("JWT_ALG", "HS256")
ALLOWED_HOSPCODE = set(os.getenv("ALLOWED_HOSPCODE", "11251,11252,10679").split(","))


class DataPayload(BaseModel):
    """Payload structure for incoming data from client"""
    hospcode: str
    dataset: str  # IPD, ICU, OR, etc.
    department: str
    datetime: str
    data: dict[str, Any]


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and check hospcode"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        hospcode = payload.get("hospcode")
        if not hospcode or hospcode not in ALLOWED_HOSPCODE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid hospcode in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/data")
async def receive_data(payload: DataPayload, claims: dict = Depends(verify_jwt)):
    """Protected endpoint - requires valid JWT"""
    # Verify that the hospcode in payload matches the one in JWT
    if payload.hospcode != claims.get("hospcode"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospcode mismatch between token and payload",
        )
    
    return {
        "status": "ok",
        "user": claims.get("sub"),
        "hospcode": claims.get("hospcode"),
        "dataset": payload.dataset,
        "received": payload.model_dump(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
