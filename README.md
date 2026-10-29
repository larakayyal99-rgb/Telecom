# Telecom API Lab

A small subscription service for practicing API testing and basic security checks. The scenario is a fictional telecom provider: a subscription can be created, activated, and deactivated.

This is an independent learning project. It does not connect to a mobile network or use Ericsson software.

## What I wanted to check

- A new subscription starts inactive.
- Only requests with a valid API key can read or change subscriptions.
- Missing fields, invalid plans, and duplicate IDs are rejected.
- Failed requests leave the subscription unchanged.

The project uses Python's standard library, with no extra Python packages. Data stays in memory and is cleared when the server restarts.

## Download and open the project

These instructions use Ubuntu or Ubuntu through WSL.

1. On GitHub, select **Code → Download ZIP**.
2. Extract the ZIP.
3. Find the folder containing `app.py`, `demo.py`, and `tests`.
4. Open an Ubuntu terminal in that folder.

If your terminal opens in your home folder, use `cd` followed by the actual location of the extracted project. The location depends on where you saved it.

Run:

```bash
ls
```

You should see `app.py`, `demo.py`, and `tests` among the files.

Repeat this folder-opening step in every new terminal before running project commands.

Choose either Python or Docker below. Both use port 8001, so run one server at a time.

## Run with Python

Python 3.10 or newer is required.

### Terminal 1 — start the API

From the project folder:

```bash
export LAB_API_KEY=local-practice-key-12345
python3 app.py
```

The server should print: `Subscription API listening on port 8001`.

Leave this terminal open while using the API.

The key above is a public example for this local lab. The server listens on `127.0.0.1:8001` by default.

### Terminal 2 — run the demo

Open another Ubuntu terminal and navigate to the same project folder. Use `ls` to confirm that `demo.py` is there.

Run:

```bash
export LAB_API_KEY=local-practice-key-12345
python3 demo.py
```

The demo sends requests to the running API and prints its responses.

| Request | Expected HTTP status |
| --- | --- |
| Missing API key | 401 |
| Invalid plan | 400 |
| Create subscription | 201 |
| Activate subscription | 200 |
| Read subscription | 200 |
| Wrong API key | 401 |
| Deactivate subscription | 200 |
| Unknown subscription | 404 |

These responses are output to read; do not paste them into the terminal as commands.

### Repeat the demo

The demo creates `demo-001`. Before repeating it:

1. Press **Ctrl+C** in Terminal 1 to stop the API.
2. Run `python3 app.py` again in that terminal.
3. Run `python3 demo.py` again in Terminal 2.

Restarting the API clears the stored subscriptions.

## Run with Docker — optional

Docker must be installed and running. Python 3 is also needed on your computer to run `demo.py`.

Stop any Python API server using port 8001 with **Ctrl+C** first.

### Terminal 1 — build and start the container

From the project folder:

```bash
docker build -t telecom-api-lab .
docker run --rm --name telecom-api-lab -p 127.0.0.1:8001:8001 -e LAB_API_KEY=local-practice-key-12345 telecom-api-lab
```

Leave this terminal open. The container exposes the API on `127.0.0.1:8001` and runs as a non-root user.

### Terminal 2 — run the demo

Open another Ubuntu terminal in the same project folder:

```bash
export LAB_API_KEY=local-practice-key-12345
python3 demo.py
```

The expected responses are listed in the table above.

### Stop or repeat

From Terminal 2, stop the container with:

```bash
docker stop telecom-api-lab
```

The container is removed automatically because it was started with `--rm`.

To repeat the demo with empty data, run the same `docker run` command again in Terminal 1, then run `python3 demo.py` in Terminal 2. You do not need to rebuild the image unless the code changes.

## API

All subscription routes require the `X-API-Key` header. `/health` is public.

| Method | Route | Purpose |
| --- | --- | --- |
| GET | /health | Check the service |
| POST | /subscriptions | Create an inactive subscription |
| GET | /subscriptions/{id} | Read a subscription |
| POST | /subscriptions/{id}/activate | Activate it |
| POST | /subscriptions/{id}/deactivate | Deactivate it |

Example JSON body for creating a subscription:

```json
{"id": "demo-001", "plan": "basic"}
```

IDs accept 1–32 letters, digits, underscores, or hyphens. Plans are `basic` or `plus`. Extra fields are rejected.

Activating an already active subscription, or deactivating an already inactive one, returns 409. This is a deliberate lab behavior.

## Automated tests

From the project folder:

```bash
python3 -m unittest discover -s tests -v
```

The 11 tests start a separate temporary server. You do not need to start the API manually.

The included GitHub Actions workflow runs these tests on pushes and pull requests when Actions is enabled. Keep `.github/workflows/tests.yml` when uploading the project.

See [test notes](TEST-NOTES.md) for the tested cases and execution status.

## Troubleshooting

- **Cannot open `app.py` or `demo.py`:** The terminal is in the wrong folder. Navigate to the extracted project folder and check its contents with `ls`.
- **Connection refused:** Start the API before running the demo and keep its terminal open.
- **Port 8001 is unavailable:** Stop the existing Python API or Docker container before starting another server.
- **The demo fails with 401 on a valid request:** Set the same `LAB_API_KEY` in the server and demo terminals.
- **Creating `demo-001` returns 409:** Restart the API or recreate the container before repeating the demo.

## Limits and next steps

The shared key is a simple access gate. It does not provide individual users, roles, or per-customer permissions.

There is no TLS, database, rate limiting, or production deployment. The single-threaded server is intended only for a local lab.

Next, I would add separate read-only and operator roles, then test that read-only requests cannot change a subscription.

## Project status

I ran the Python demo on Ubuntu through WSL and passed all 11 automated tests.

I also built and ran the Docker image with Docker Desktop, then ran the demo against the container. Running `docker exec telecom-api-lab id` confirmed UID and GID 10001.

See [test notes](TEST-NOTES.md) for details.
