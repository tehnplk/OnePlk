import requests

print("Test with invalid token:")
r = requests.post(
    'http://localhost:8000/ipd',
    json={'hospcode': '12345'},
    headers={'Authorization': 'Bearer invalid.token.here'}
)
print(f'Status: {r.status_code}')
print(f'Response: {r.text}')
