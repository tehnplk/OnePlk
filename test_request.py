import requests

print("Test 1: Invalid token")
r = requests.post(
    'http://localhost:8000/ipd',
    json={'hospcode': '12345', 'data': 'test'},
    headers={'Authorization': 'Bearer invalid.token.here'}
)
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')
print()

print("Test 2: No token")
r = requests.post(
    'http://localhost:8000/ipd',
    json={'hospcode': '12345', 'data': 'test'}
)
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')
