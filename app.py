"""Local subscription API for learning API testing and access control."""
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import re


class SubscriptionHandler(BaseHTTPRequestHandler):
    def reply(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        supplied = self.headers.get("X-API-Key", "")
        if not hmac.compare_digest(supplied.encode(), self.server.api_key.encode()):
            self.reply(401, {"error": "A valid API key is required."})
            return False
        return True

    def read_json(self):
        if self.headers.get("Transfer-Encoding"):
            self.reply(400, {"error": "Transfer-Encoding is not supported."})
            return None
        if self.headers.get_content_type() != "application/json":
            self.reply(415, {"error": "Use Content-Type: application/json."})
            return None
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            self.reply(400, {"error": "Use a JSON object of 1–4096 bytes."})
            return None
        return data

    def do_GET(self):
        if self.path == "/health":
            self.reply(200, {"status": "ok"})
            return
        if not self.authorized():
            return
        match = re.fullmatch(r"/subscriptions/([A-Za-z0-9_-]{1,32})", self.path)
        if not match:
            self.reply(404, {"error": "Route not found."})
            return
        item = self.server.subscriptions.get(match[1])
        self.reply(200, item) if item else self.reply(404, {"error": "Subscription not found."})

    def do_POST(self):
        if not self.authorized():
            return
        if self.path == "/subscriptions":
            data = self.read_json()
            if data is None:
                return
            identifier, plan = data.get("id"), data.get("plan")
            if (set(data) != {"id", "plan"} or not isinstance(identifier, str)
                    or not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", identifier)
                    or not isinstance(plan, str) or plan not in {"basic", "plus"}):
                self.reply(400, {"error": "Provide a valid id and a basic or plus plan."})
                return
            if identifier in self.server.subscriptions:
                self.reply(409, {"error": "Subscription already exists."})
                return
            item = {"id": identifier, "plan": plan, "status": "inactive"}
            self.server.subscriptions[identifier] = item
            self.reply(201, item)
            return
        match = re.fullmatch(r"/subscriptions/([A-Za-z0-9_-]{1,32})/(activate|deactivate)", self.path)
        if not match:
            self.reply(404, {"error": "Route not found."})
            return
        identifier, action = match.groups()
        item = self.server.subscriptions.get(identifier)
        if item is None:
            self.reply(404, {"error": "Subscription not found."})
            return
        status = "active" if action == "activate" else "inactive"
        if item["status"] == status:
            self.reply(409, {"error": f"Subscription is already {status}."})
            return
        item["status"] = status
        self.reply(200, item)


def create_server(host, port, key):
    server = HTTPServer((host, port), SubscriptionHandler)
    server.api_key = key
    server.subscriptions = {}  # This lab clears its data when the server restarts.
    return server


if __name__ == "__main__":
    key = os.environ.get("LAB_API_KEY", "")
    if len(key) < 16:
        raise SystemExit("Set LAB_API_KEY to at least 16 characters.")
    server = create_server(os.environ.get("LAB_HOST", "127.0.0.1"), 8001, key)
    print("Subscription API listening on port 8001", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
