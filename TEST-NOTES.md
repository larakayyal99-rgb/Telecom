# Test notes

## Cases

| Test | Expected result |
| --- | --- |
| Health without a key | 200 |
| Create valid subscription | 201, inactive |
| Activate, read, deactivate | Active then inactive |
| Create without a valid key | 401, no record created |
| Read or activate with wrong key | 401, state unchanged |
| Invalid fields or JSON shape | 400, no record created |
| Duplicate ID | 409, original plan preserved |
| Unknown subscription | 404 |
| Repeat activation | 409 |
| Broken JSON | 400 |
| Wrong content type | 415 |

## Development results

On 29 October 2026, all 11 automated tests passed in the assistant's development environment. The example client was also run against the actual app process. See DEVELOPMENT-OUTPUT.txt for the captured output.

These are development checks, not a claim that I ran the project on my own device.

## My Ubuntu run

Tested on 29 October 2026 on Ubuntu through WSL on Windows.

The demo completed with the expected responses:

| Request | Observed response |
| --- | --- |
| Create without a key | 401 |
| Create with an invalid plan | 400 |
| Create valid subscription | 201, inactive |
| Activate subscription | 200, active |
| Read subscription | 200, active |
| Deactivate with wrong key | 401 |
| Deactivate with correct key | 200, inactive |
| Activate unknown subscription | 404 |

The automated test run completed with `Ran 11 tests in 0.542s` and `OK`.

## Docker run

Built the image using `docker build -t telecom-api-lab .` and ran it with the host port restricted to `127.0.0.1:8001`.

The initial container start failed to publish port 8001. A later retry started successfully. The exact cause of the initial failure was not established.

Repeated the demo against the running container. All eight example requests returned their expected responses.

Checked the container user:

```bash
docker exec telecom-api-lab id
```

Observed:

```text
uid=10001 gid=10001 groups=10001
```

This confirms the default container user is non-root. It does not by itself establish that the whole application is secure.

## GitHub Actions

Workflow included, but no GitHub execution result is recorded yet.

## Evidence

The personal lab results above were transcribed from terminal screenshots supplied during the lab. DEVELOPMENT-OUTPUT.txt contains separate development-environment results, not the personal terminal output.
