# SecureShop – Security Findings Report

This document records the detailed technical investigations for all controlled security weaknesses evaluated in the SecureShop educational laboratory.

---

# Finding 1 – Insecure Direct Object References (IDOR)

## OWASP Category
A01:2021 – Broken Access Control (CWE-639: Authorization Bypass Through User-Controlled Key)

## Severity
**High** (Lab Assessment Rating)

## What?
The application fails to enforce resource-level authorization when retrieving customer orders. Any authenticated user can modify the numeric identifier in the URL to view order invoices belonging to other customers.

## Where?
- **Endpoint:** `GET /orders/<order_id>`
- **Parameter:** `order_id` (Path variable)
- **Component:** `order_details()` route handler in `app.py`

## Why?
The endpoint queries the database using `SELECT ... WHERE id = ?` based solely on the user-supplied `order_id` without verifying whether the record's `user_id` matches the authenticated caller's `session['user_id']` or whether the user holds an administrative role.

## Impact
Horizontal privilege escalation leading to loss of customer confidentiality. An attacker logged in as `user` can enumerate order IDs (e.g., `/orders/1`, `/orders/2`, `/orders/3`) and extract full names, email addresses, order totals, and physical shipping destinations of other customers (such as Alice Walker).

## Evidence
```http
[PLACEHOLDER – REPLACE WITH ACTUAL OWASP ZAP REQUEST / SCREENSHOT]

GET /orders/2 HTTP/1.1
Host: 127.0.0.1:8080
Cookie: session=ey... (Authenticated as user 'user', id=2)

HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!-- Exposes Alice Walker's confidential order and Texas address -->
```

## Safe Validation
1. Start the application in **Vulnerable Mode** (`SECURITY_MODE=vulnerable`).
2. Log in with standard user credentials: `user` / `User@123`.
3. Navigate to `/orders` and observe that Order #1 and Order #3 belong to your account.
4. Manually edit the URL in the browser to `http://127.0.0.1:8080/orders/2`.
5. Observe that Alice Walker's confidential invoice and shipping address are returned with HTTP 200 OK.

## Remediation
Implemented server-side authorization enforcement before rendering the invoice:
```python
# app.py - SECURITY FIX
if order["user_id"] != session.get("user_id") and session.get("role") != "admin":
    log_security_event(
        "UNAUTHORIZED_ACCESS_IDOR",
        f"Unauthorized access attempt to Order #{order_id}",
        "CRITICAL"
    )
    abort(403)
```

## Retest
```
[PLACEHOLDER – REPLACE WITH ACTUAL RETEST SCREENSHOT / LOG OUTPUT]

Status: Verified Remediated
Result: Navigating to /orders/2 while logged in as 'user' returns HTTP 403 Forbidden.
Audit Trail: Event logged to logs/security.log.
```

---

# Finding 2 – SQL Injection in Product Search

## OWASP Category
A03:2021 – Injection (CWE-89: Improper Neutralization of Special Elements used in an SQL Command)

## Severity
**High** (Lab Assessment Rating)

## What?
The product search functionality dynamically concatenates untrusted user input into an SQL command string, allowing attackers to break out of data literals and manipulate the SQL interpreter.

## Where?
- **Endpoint:** `GET /products?q=<search_query>`
- **Parameter:** `q` (Query string)
- **Component:** `products()` route handler in `app.py`

## Why?
The search handler constructs the database query using raw Python string formatting:
`query = f"SELECT * FROM products WHERE name LIKE '%{search_query}%' OR description LIKE '%{search_query}%';"`

## Impact
Data exposure and integrity risk. Untrusted input alters database execution logic. While scoped to the local SQLite database, this flaw allows enumeration of arbitrary records and potential extraction of data across database tables.

## Evidence
```http
[PLACEHOLDER – REPLACE WITH ACTUAL OWASP ZAP ACTIVE SCAN ALERT]

GET /products?q=%27+OR+1%3D1+-- HTTP/1.1
Host: 127.0.0.1:8080

HTTP/1.1 200 OK
<!-- Response contains all database products regardless of search criteria -->
```

## Safe Validation
1. Start the application in **Vulnerable Mode**.
2. Navigate to `/products` and locate the search bar.
3. Submit the harmless local boolean payload: `' OR 1=1 --`.
4. Observe that the SQL interpreter treats `1=1` as an unconditional true statement, returning every product in the database.

## Remediation
Converted the query to use parameterized prepared statements with bound parameter markers (`?`):
```python
# app.py - SECURITY FIX
like_param = f"%{search_query}%"
cursor.execute(
    "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?;",
    (like_param, like_param)
)
```

## Retest
```
[PLACEHOLDER – REPLACE WITH ACTUAL RETEST EVIDENCE]

Status: Verified Remediated
Result: Submitting '' OR 1=1 -- treats the string as literal text; returns 0 matches safely without errors.
```

---

# Finding 3 – Security Misconfiguration (Debug Mode & Missing Headers)

## OWASP Category
A05:2021 – Security Misconfiguration (CWE-16, CWE-1021)

## Severity
**Medium** (Lab Assessment Rating)

## What?
The application runs with Flask development debug mode enabled, exposing detailed stack traces and system internals upon application exceptions. Additionally, essential HTTP defensive security headers (such as `X-Frame-Options` and `Content-Security-Policy`) are omitted.

## Where?
- **Endpoint:** Global HTTP response headers & `GET /debug/crash-test`
- **Component:** `apply_security_headers()` middleware and error handlers in `app.py`

## Why?
Development convenience configurations were left active in the operational runtime, and no security response middleware was applied to inject defensive headers.

## Impact
Information disclosure of local file paths, framework versions, and variable states during crashes. Furthermore, missing framing restrictions expose the application to UI redressing (Clickjacking).

## Evidence
```http
[PLACEHOLDER – REPLACE WITH ACTUAL ZAP HEADER CHECK ALERT]

Response Headers Missing:
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options: nosniff
Server Header Leaked:
- Server: SecureShop-Dev/1.0 (Python/Flask-Debug)
```

## Safe Validation
1. In **Vulnerable Mode**, navigate to `http://127.0.0.1:8080/debug/crash-test`.
2. Observe the full interactive exception traceback disclosing local Python file paths.
3. Inspect HTTP response headers via browser DevTools (F12) Network tab to verify absence of `X-Frame-Options` and presence of verbose `Server` header.

## Remediation
1. Disabled debug mode (`debug=False`).
2. Implemented custom sanitized error handlers for 403, 404, and 500 status codes.
3. Injected hardened HTTP security headers via `@app.after_request`:
```python
# app.py - SECURITY FIX
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none';"
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
response.headers.pop("Server", None)
```

## Retest
```
[PLACEHOLDER – REPLACE WITH ACTUAL ZAP RESCAN EVIDENCE]

Status: Verified Remediated
Result: Triggering /debug/crash-test displays a sanitized error page; ZAP alerts 10020 and 10038 resolved.
```

---

# Finding 4 – Vulnerable and Outdated Dependency

## OWASP Category
A06:2021 – Vulnerable and Outdated Components (CWE-1104)

## Severity
**High** (Lab Assessment Rating)

## What?
The application relies on legacy releases of third-party ecosystem libraries with known, publicly cataloged security advisories.

## Where?
- **Component:** `requirements-vulnerable.txt`
- **Package:** `Werkzeug==2.2.2`

## Why?
Software dependency versions were unpinned or frozen at outdated releases without routine Software Composition Analysis (SCA) or vulnerability tracking.

## Impact
Potential Denial of Service (DoS) through crafted multipart/form-data payloads (CVE-2023-25577), allowing malicious requests to consume excessive memory and CPU resources on the host machine.

## Evidence
```bash
[PLACEHOLDER – REPLACE WITH ACTUAL PIP-AUDIT / SAFETY OUTPUT]

pip-audit -r requirements-vulnerable.txt
Found 2 known vulnerabilities in 1 package:
- Package: werkzeug (2.2.2)
  ID: PYSEC-2023-55 / CVE-2023-25577 (High) - Multipart form data parsing DoS
  ID: PYSEC-2023-219 / CVE-2023-46136 (Moderate) - Resource exhaustion
```

## Safe Validation
Execute dependency scanner against the vulnerable requirement specification:
```bash
pip-audit -r requirements-vulnerable.txt
```

## Remediation
Upgraded dependency specifications in `requirements-fixed.txt` to patched upstream versions:
```text
# requirements-fixed.txt
Flask>=3.0.0
Werkzeug>=3.0.3
Jinja2>=3.1.4
itsdangerous>=2.2.0
click>=8.1.7
```

## Retest
```bash
[PLACEHOLDER – REPLACE WITH ACTUAL AUDIT CLEAN SCAN OUTPUT]

pip-audit -r requirements-fixed.txt
No known vulnerabilities found!
```

---

# Finding 5 – Identification & Authentication Failures

## OWASP Category
A07:2021 – Identification and Authentication Failures (CWE-384, CWE-521)

## Severity
**Medium** (Lab Assessment Rating)

## What?
Session identification cookies lack `HttpOnly` and `SameSite` flags, allowing client-side scripts to read session data. Furthermore, user registration accepts single-character passwords without complexity requirements.

## Where?
- **Endpoint:** `POST /register` & `Set-Cookie: session=...`
- **Component:** `register()` and `configure_session_security()` in `app.py`

## Why?
Framework session defaults were overridden to permit unconstrained cookies and registration lacked regex validation.

## Impact
Increased susceptibility to Cross-Site Scripting (XSS) session hijacking and credential stuffing / brute-force password guessing.

## Evidence
```http
[PLACEHOLDER – REPLACE WITH ACTUAL BROWSER COOKIE INSPECTOR SCREENSHOT]

Vulnerable Cookie:
Set-Cookie: session=ey...; Path=/
(Missing HttpOnly, Missing SameSite)
```

## Safe Validation
1. Inspect the `session` cookie in browser DevTools Application > Cookies.
2. In Vulnerable Mode, verify that `document.cookie` in the browser console accesses session information.
3. Test registering a user with password `a`. In Vulnerable Mode, the registration succeeds.

## Remediation
Configured hardened session cookie flags and enforced password complexity:
```python
# app.py - SECURITY FIX
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Registration password complexity regex (min 8 chars, upper, lower, digit, special)
password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
```

## Retest
```
[PLACEHOLDER – REPLACE WITH ACTUAL RETEST COOKIE HEADER]

Status: Verified Remediated
Result: Set-Cookie includes HttpOnly and SameSite=Lax. Weak passwords are rejected.
```

---

# Finding 6 – Security Logging & Monitoring Failures

## OWASP Category
A09:2021 – Security Logging and Monitoring Failures (CWE-778)

## Severity
**Medium** (Lab Assessment Rating)

## What?
The application fails to maintain an audit trail for critical security events, including failed login attempts, unauthorized IDOR probes, and administrative operations.

## Where?
- **Component:** Authentication, authorization, and administrative handlers in `app.py`
- **Log Destination:** `logs/security.log` and `security_logs` database table

## Why?
No centralized security event logging was implemented; security violations failed silently without operator alerting.

## Impact
Lack of visibility into active attacks, preventing timely incident response and forensic analysis.

## Evidence
```
[PLACEHOLDER – REPLACE WITH ACTUAL AUDIT LOG SNIPPET]

Vulnerable Mode:
No entries created in logs/security.log during attack attempts.
```

## Safe Validation
1. Trigger 3 consecutive failed login attempts with invalid credentials at `/login`.
2. Attempt to access `/orders/2` while authenticated as `user`.
3. In Vulnerable Mode, inspect `logs/security.log` and verify that no audit events were recorded.

## Remediation
Implemented a centralized `log_security_event()` logging function that records timestamp, event type, username, IP address, and details to both SQLite and a persistent file:
```python
# app.py - SECURITY FIX
def log_security_event(event_type, details, severity="INFO", username=None):
    # Logs event to logs/security.log and security_logs DB table
```

## Retest
```
[PLACEHOLDER – REPLACE WITH ACTUAL LOG OUTPUT FROM RETEST]

Status: Verified Remediated
Result: Failed logins and IDOR attempts produce immediate timestamped audit records.
```
