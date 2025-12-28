import requests
import json

print("=" * 60)
print("Test 1: Invalid token")
print("=" * 60)
try:
    r = requests.post(
        'http://localhost:8000/ipd',
        json={'hospcode': '12345', 'data': 'test'},
        headers={'Authorization': 'Bearer invalid.token.here'}
    )
    print(f'Status Code: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')
except Exception as e:
    print(f'Error: {e}')

print("\n" + "=" * 60)
print("Test 2: No token")
print("=" * 60)
try:
    r = requests.post(
        'http://localhost:8000/ipd',
        json={'hospcode': '12345', 'data': 'test'}
    )
    print(f'Status Code: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')
except Exception as e:
    print(f'Error: {e}')

print("\n" + "=" * 60)
print("Test 3: Valid token")
print("=" * 60)
from jose import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM = os.getenv("JWT_ALG", "HS256")
token = jwt.encode({"sub": "testuser"}, JWT_SECRET, algorithm=JWT_ALGORITHM)

try:
    r = requests.post(
        'http://localhost:8000/ipd',
        json={'hospcode': '12345', 'data': 'test'},
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f'Status Code: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')
except Exception as e:
    print(f'Error: {e}')
