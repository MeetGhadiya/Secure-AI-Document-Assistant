import requests
import json
import uuid
headers = {'X-Session-Id': str(uuid.uuid4())}
r = requests.post('http://127.0.0.1:8000/api/query', json={'question':'hello from test'}, headers=headers)
print(r.status_code)
try:
    print(r.json())
except Exception:
    print(r.text)
