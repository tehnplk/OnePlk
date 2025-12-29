from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

app = FastAPI(title="JWT Auth Server")
security = HTTPBearer(auto_error=True)

# Config
JWT_SECRET = "devsecret"
JWT_ALGORITHM = "HS256"
ALLOWED_HOSPCODE = {"11251", "11252", "10679"}


class DataPayload(BaseModel):
    message: str = ""


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
    return {
        "status": "ok",
        "user": claims.get("sub"),
        "hospcode": claims.get("hospcode"),
        "received": payload.model_dump(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
