from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

app = FastAPI(title="JWT Auth Server")
security = HTTPBearer(auto_error=True)

# Hardcoded config
JWT_SECRET = "devsecret"
JWT_ALGORITHM = "HS256"


class DataPayload(BaseModel):
    message: str = ""


ALLOWED_HOSPCODE = {"11251", "11252", "10679"}



def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """ตรวจสอบ JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        hospcode_claim = payload.get("hospcode")
        if not hospcode_claim or hospcode_claim not in ALLOWED_HOSPCODE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid hospcode in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(f"[AUTH] JWT valid: sub={payload.get('sub')}")
        return payload
    except JWTError as exc:
        print(f"[AUTH] JWT error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/data")
async def receive_data(payload: DataPayload, claims: dict = Depends(verify_jwt)):
    """Endpoint ที่ต้องการ JWT authentication"""
    print(f"[DATA] Received from {claims.get('sub')}: {payload}")
    return {
        "status": "ok",
        "user": claims.get("sub"),
        "hospcode": claims.get("hospcode"),
        "received": payload.model_dump(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
