
from fastapi.testclient import TestClient
from server import app
import os
from jose import jwt

client = TestClient(app)

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM = os.getenv("JWT_ALG", "HS256")

def create_token(payload):
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def test_valid_token():
    token = create_token({"sub": "testuser"})
    response = client.post(
        "/ipd",
        json={"hospcode": "12345", "data": "test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_invalid_token():
    response = client.post(
        "/ipd",
        json={"hospcode": "12345", "data": "test"},
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
    # Check if the error message starts with the expected string
    assert response.json()["detail"].startswith("Invalid or expired token")

def test_wrong_secret_token():
    # Token signed with different secret
    wrong_token = jwt.encode({"sub": "test"}, "wrongsecret", algorithm=JWT_ALGORITHM)
    response = client.post(
        "/ipd",
        json={"hospcode": "12345", "data": "test"},
        headers={"Authorization": f"Bearer {wrong_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"].startswith("Invalid or expired token")

if __name__ == "__main__":
    try:
        test_valid_token()
        print("test_valid_token passed")
        test_invalid_token()
        print("test_invalid_token passed")
        test_wrong_secret_token()
        print("test_wrong_secret_token passed")
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
