
import os
from jose import jwt, JWTError
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException
from server import verify_jwt

# Mock environment if needed (though server.py sets defaults)
# os.environ["JWT_SECRET"] = "changeme"

def test_verify_jwt_invalid():
    print("Testing verify_jwt with invalid token...")
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token")
    try:
        result = verify_jwt(creds)
        print(f"Result: {result}")
        print("ERROR: verify_jwt did NOT raise exception for invalid token!")
    except HTTPException as e:
        print(f"Success: Caught expected HTTPException: {e.detail}")
    except Exception as e:
        print(f"Caught unexpected exception: {type(e)} {e}")

if __name__ == "__main__":
    test_verify_jwt_invalid()
