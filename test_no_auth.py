import requests

print("Test without Authorization header:")
r = requests.post(
    'http://localhost:8000/ipd',
    json={'hospcode': '12345'}
)
print(f'Status: {r.status_code}')
print(f'Response: {r.text}')
