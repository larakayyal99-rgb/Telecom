import http.client
import json
import threading
import unittest
from app import create_server

KEY = "test-key-for-local-tests"


class SubscriptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0, KEY)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.server.subscriptions.clear()

    def request(self, method, path, data=None, key=KEY, raw=None, content_type="application/json"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Content-Type": content_type}
        if key is not None:
            headers["X-API-Key"] = key
        body = raw if raw is not None else json.dumps(data) if data is not None else None
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        result = response.status, json.loads(response.read())
        connection.close()
        return result

    def create(self):
        return self.request("POST", "/subscriptions", {"id": "demo-001", "plan": "basic"})

    def test_health_is_public(self):
        self.assertEqual(self.request("GET", "/health", key=None), (200, {"status": "ok"}))

    def test_create_starts_inactive(self):
        self.assertEqual(self.create(), (201, {"id": "demo-001", "plan": "basic", "status": "inactive"}))

    def test_activate_read_and_deactivate(self):
        self.create()
        self.assertEqual(self.request("POST", "/subscriptions/demo-001/activate")[1]["status"], "active")
        self.assertEqual(self.request("GET", "/subscriptions/demo-001")[1]["status"], "active")
        self.assertEqual(self.request("POST", "/subscriptions/demo-001/deactivate")[1]["status"], "inactive")

    def test_missing_and_wrong_keys_cannot_create(self):
        for key in (None, "wrong"):
            with self.subTest(key=key):
                self.assertEqual(self.request("POST", "/subscriptions", {"id": "demo-001", "plan": "basic"}, key=key)[0], 401)
        self.assertEqual(self.server.subscriptions, {})

    def test_wrong_key_cannot_read_or_activate(self):
        self.create()
        self.assertEqual(self.request("GET", "/subscriptions/demo-001", key="wrong")[0], 401)
        self.assertEqual(self.request("POST", "/subscriptions/demo-001/activate", key="wrong")[0], 401)
        self.assertEqual(self.server.subscriptions["demo-001"]["status"], "inactive")

    def test_invalid_fields(self):
        for data in ({"id": "demo-001"}, {"id": "bad id", "plan": "basic"},
                     {"id": "demo-001", "plan": "unknown"}, {"id": 123, "plan": "basic"},
                     {"id": "demo-001", "plan": []}, {"id": "demo-001", "plan": "basic", "status": "active"}, []):
            with self.subTest(data=data):
                self.assertEqual(self.request("POST", "/subscriptions", data)[0], 400)
        self.assertEqual(self.server.subscriptions, {})

    def test_duplicate_does_not_overwrite(self):
        self.create()
        self.assertEqual(self.request("POST", "/subscriptions", {"id": "demo-001", "plan": "plus"})[0], 409)
        self.assertEqual(self.server.subscriptions["demo-001"]["plan"], "basic")

    def test_unknown_subscription(self):
        self.assertEqual(self.request("GET", "/subscriptions/unknown")[0], 404)
        self.assertEqual(self.request("POST", "/subscriptions/unknown/activate")[0], 404)

    def test_repeated_activation(self):
        self.create()
        self.request("POST", "/subscriptions/demo-001/activate")
        self.assertEqual(self.request("POST", "/subscriptions/demo-001/activate")[0], 409)

    def test_broken_json(self):
        self.assertEqual(self.request("POST", "/subscriptions", raw="{broken")[0], 400)
        self.assertEqual(self.server.subscriptions, {})

    def test_wrong_content_type(self):
        self.assertEqual(self.request("POST", "/subscriptions", {}, content_type="text/plain")[0], 415)


if __name__ == "__main__":
    unittest.main()
