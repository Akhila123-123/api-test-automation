# API Test Automation (pytest + Bash)

Automated functional, negative and performance tests for a REST API, with a
Bash regression runner that saves a log and scans it for failures.

## What is in this project
| File | Purpose |
|---|---|
| `mock_api.py` | Small local REST API (`/posts`) used as the test target |
| `tests/test_posts_api.py` | 16 pytest tests: GET, POST, DELETE, 404/400 cases, response-time check |
| `tests/conftest.py` | Starts the mock API automatically; supports a real API via `BASE_URL` |
| `run_tests.bat ` | Runs the suite, saves a timestamped log, fails if anything fails |
| `check_logs.sh` | Scans a log and prints passed / failed / error counts |

## Run it
```bash
pip install -r requirements.txt
./run_tests.bat                        # tests the local mock API
BASE_URL=https://jsonplaceholder.typicode.com ./run_tests.sh   # a public API
```
When using a public API, run only read tests (`pytest -k "list or single or filter"`)
because those APIs do not truly store POST/DELETE changes.

## What the tests check
- Status codes (200, 201, 400, 404) and JSON content type
- Required fields in every response
- Query filtering (`?userId=1`)
- Create, then fetch; delete, then confirm 404
- Invalid input returns 400 (parametrized tests)
- List endpoint responds in under one second

## How an HTTP request works, end to end
1. **DNS lookup:** the client asks a DNS resolver to turn `example.com` into an IP address.
2. **TCP connection:** the client opens a connection to that IP on port 80 (HTTP) or 443 (HTTPS), using a three-way handshake (SYN, SYN-ACK, ACK).
3. **TLS handshake (HTTPS only):** client and server agree on encryption and the server proves its identity with a certificate.
4. **HTTP request:** the client sends a method (GET/POST/DELETE), a path, headers and an optional body.
5. **Server processing:** the server routes the request, runs its logic, and may query a database.
6. **HTTP response:** the server returns a status code (2xx success, 4xx client error, 5xx server error), headers and a body (here, JSON).
7. **Connection reuse or close:** the connection is kept alive for further requests or closed.

When a test fails, the status code tells you where to look: 4xx means the
request was wrong, 5xx means the server failed, a timeout often means a
network or DNS problem.

## Ideas to extend it
- Add authentication tests (401/403)
- Add a load test with `locust`
- Run the suite in GitHub Actions on every push
- Containerize the mock API with Docker
