"""Send example requests to the running local API."""
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

key = os.environ.get("LAB_API_KEY", "")
if not key:
    raise SystemExit("Set LAB_API_KEY to the same value used by the server.")


def send(label, method, path, expected, data=None, supplied_key=key):
    headers = {"Content-Type": "application/json", "X-API-Key": supplied_key}
    body = json.dumps(data).encode() if data is not None else None
    request = Request("http://127.0.0.1:8001" + path, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=3) as response:
            status, result = response.status, json.load(response)
    except HTTPError as error:
        status, result = error.code, json.load(error)
        error.close()
    print(f"{label}: HTTP {status} {result}")
    if status != expected:
        raise SystemExit(f"Expected HTTP {expected}. Restart the lab server for a fresh demo.")


send("Missing key", "POST", "/subscriptions", 401,
     {"id": "demo-001", "plan": "basic"}, supplied_key="")
send("Invalid plan", "POST", "/subscriptions", 400,
     {"id": "demo-001", "plan": "unknown"})
send("Create", "POST", "/subscriptions", 201, {"id": "demo-001", "plan": "basic"})
send("Activate", "POST", "/subscriptions/demo-001/activate", 200)
send("Read", "GET", "/subscriptions/demo-001", 200)
send("Wrong key", "POST", "/subscriptions/demo-001/deactivate", 401, supplied_key="wrong")
send("Deactivate", "POST", "/subscriptions/demo-001/deactivate", 200)
send("Unknown subscription", "POST", "/subscriptions/not-found/activate", 404)
