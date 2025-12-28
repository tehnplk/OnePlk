import requests
from jose import jwt
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
JWT_SECRET = "mysecretkey"
JWT_ALGORITHM = "HS256"

def create_valid_token():
    payload = {
        "sub": "testuser",
        "exp": datetime.utcnow() + timedelta(minutes=60),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

print("=" * 60)
print("TEST 1: Invalid JWT Token")
print("=" * 60)

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer invalid_token_here"
}
data = {"hospcode": "12345", "message": "test invalid"}

response = requests.post(f"{BASE_URL}/data", json=data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 60)
print("TEST 2: Valid JWT Token")
print("=" * 60)

valid_token = create_valid_token()
print(f"Token: {valid_token[:50]}...")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {valid_token}"
}
data = {"hospcode": "67890", "message": "test valid"}

response = requests.post(f"{BASE_URL}/data", json=data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
