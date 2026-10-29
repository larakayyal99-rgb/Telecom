# Telecom API Lab

A small subscription service for practicing API testing and basic security checks. The scenario is a fictional telecom provider: a subscription can be created, activated, and deactivated.

This is an independent learning project. It does not connect to a mobile network or use Ericsson software.

## What I wanted to check

- A new subscription starts inactive.
- Only requests with a valid API key can read or change subscriptions.
- Missing fields, invalid plans, and duplicate IDs are rejected.
- Failed requests leave the subscription unchanged.

The project uses Python's standard library, with no extra Python packages. Data stays in memory and is cleared when the server restarts.

## Run locally

Use Python 3.10 or newer on Ubuntu or Ubuntu through WSL.

Download and extract the project. Open a terminal inside the folder containing `app.py`, `demo.py`, and `tests`. Use `ls` to confirm the files are there.

**Terminal 1 — start the API:**

```bash
export LAB_API_KEY=local-practice-key-12345
python3 app.py
```

The key above is a public example for this local lab, not a real credential. The server listens on `127.0.0.1:8001` by default.

**Terminal 2 — run the example requests:**

Open another Ubuntu terminal in the same project folder. Set the same example key and run:

```bash
export LAB_API_KEY=local-practice-key-12345
python3 demo.py
```

The demo sends valid and invalid requests and prints the actual responses. Restart the server before repeating the demo, because `demo-001` will already exist.

Stop the server with Ctrl+C.

## API

All subscription routes require the `X-API-Key` header. `/health` is public.

| Method | Route | Purpose |
| --- | --- | --- |
| GET | /health | Check the service |
| POST | /subscriptions | Create an inactive subscription |
| GET | /subscriptions/{id} | Read a subscription |
| POST | /subscriptions/{id}/activate | Activate it |
| POST | /subscriptions/{id}/deactivate | Deactivate it |

Example creation body:

```json
{"id": "demo-001", "plan": "basic"}
```

IDs accept 1–32 letters, digits, underscores, or hyphens. Plans are `basic` or `plus`. Extra fields are rejected. Repeating the current activation state returns 409; this is a deliberate lab behavior.

## Automated tests

From the project folder:

```bash
python3 -m unittest discover -s tests -v
```

The 11 tests start a separate temporary server. The manual API does not need to be running. See [test notes](TEST-NOTES.md) for the tested cases and execution status.

The included GitHub Actions workflow runs these tests on pushes and pull requests when Actions is enabled. Preserve `.github/workflows/tests.yml` when uploading.

## Docker — optional

With Docker installed and running, open a terminal in the project folder:

```bash
docker build -t telecom-api-lab .
docker run --rm --name telecom-api-lab -p 127.0.0.1:8001:8001 -e LAB_API_KEY=local-practice-key-12345 telecom-api-lab
```

Stop any Python server using port 8001 first. Run `demo.py` from a second terminal as above. The container runs as a non-root user. The Docker image was built and run on Windows with Docker Desktop and Ubuntu through WSL. The demo returned the expected responses. Running `docker exec telecom-api-lab id` confirmed UID and GID 10001.

## Limits and next steps

The shared key is a simple access gate: it does not provide individual users, roles, or per-customer permissions. There is no TLS, database, rate limiting, or production deployment. The single-threaded server is intended only for a local lab.

Next, I would add separate read-only and operator roles, then test that read-only requests cannot change a subscription.

## Project status

Prepared with AI assistance for learning. I ran the demo locally on Ubuntu through WSL, passed all 11 automated tests, and repeated the demo against the Docker container. I also checked that the container runs as a non-root user. GitHub Actions has not been run yet. See [test notes](TEST-NOTES.md).
