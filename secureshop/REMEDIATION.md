# SecureShop – Remediation Guide

This guide documents the technical fixes applied to remediate all controlled weaknesses identified in the SecureShop application, providing code diffs, configuration adjustments, and retest procedures.

---

## 1. Remediation for A01: Broken Access Control (IDOR)

### Original Weakness
Standard customer `user` could access the order invoice of another customer (`alice`) by altering the URL path variable `/orders/1` to `/orders/2`.

### Root Cause
Missing server-side ownership authorization. The application accepted the order ID directly from user input and rendered the database record without verifying if `order['user_id'] == session['user_id']`.

### Security Fix
Added server-side ownership authorization logic in `order_details()` before rendering invoice data. If the order owner ID does not match the active session ID (and user is not an administrator), the request is aborted with HTTP 403 Forbidden and logged.

### Code Change
```diff
--- vulnerable/app.py
+++ fixed/app.py
@@ -370,6 +370,14 @@
     if not order:
         conn.close()
         abort(404)
 
+    # SECURITY FIX: Server-side ownership verification
+    current_uid = session.get("user_id")
+    is_admin = session.get("role") == "admin"
+    if order["user_id"] != current_uid and not is_admin:
+        log_security_event("UNAUTHORIZED_ACCESS_IDOR", f"User {current_uid} tried Order #{order_id}", "CRITICAL")
+        conn.close()
+        abort(403)
+
     items = cursor.execute("SELECT ... WHERE order_id = ?", (order_id,)).fetchall()
```

### Expected Result
Unauthorized access attempts return `403 Forbidden`. Authorized access by the true owner or admin succeeds normally.

### Retest Method
1. Sign in as `user` (id=2).
2. Browse to `http://127.0.0.1:8080/orders/2`.
3. Verify HTTP 403 Forbidden is returned and an entry appears in `logs/security.log`.

---

## 2. Remediation for A03: SQL Injection (SQLi)

### Original Weakness
The product search endpoint was vulnerable to SQL syntax manipulation via unescaped string interpolation.

### Root Cause
Constructing SQL commands dynamically using Python string formatting (`f"SELECT ... LIKE '%{search_query}%'"`).

### Security Fix
Replaced raw string concatenation with DB-API parameterized queries using bound parameters (`?`).

### Code Change
```diff
--- vulnerable/app.py
+++ fixed/app.py
@@ -148,8 +148,8 @@
     if search_query:
-        raw_sql = f"SELECT * FROM products WHERE name LIKE '%{search_query}%' OR description LIKE '%{search_query}%';"
-        cursor.execute(raw_sql)
+        # SECURITY FIX: Parameterized prepared statement
+        like_param = f"%{search_query}%"
+        cursor.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ?;", (like_param, like_param))
         product_list = cursor.fetchall()
```

### Expected Result
User input is treated strictly as data literals. SQL metacharacters (quotes, dashes, semicolons) cannot alter query structure.

### Retest Method
1. Submit test payload `' OR 1=1 --` into the search box.
2. Confirm that 0 items are returned and no database syntax errors are generated.

---

## 3. Remediation for A05: Security Misconfiguration

### Original Weakness
Flask development debug mode was active in runtime, exposing interactive tracebacks on unhandled errors; missing standard defensive HTTP response headers.

### Root Cause
Default developer configuration was left in place; lack of response header injection middleware.

### Security Fix
1. Disabled debug mode (`debug=False`).
2. Created custom error handlers for 403, 404, and 500 status codes.
3. Added `@app.after_request` middleware applying `X-Frame-Options`, `Content-Security-Policy`, and `X-Content-Type-Options`.

### Code Change
```diff
--- vulnerable/app.py
+++ fixed/app.py
@@ -95,6 +95,14 @@
 @app.after_request
 def apply_security_headers(response):
+    # SECURITY FIX: Defensive response headers
+    response.headers["X-Frame-Options"] = "DENY"
+    response.headers["X-Content-Type-Options"] = "nosniff"
+    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none';"
+    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
+    response.headers.pop("Server", None)
     return response
```

### Expected Result
Unhandled exceptions display generic error pages without tracebacks; browser inspect shows security headers present; Clickjacking is prevented.

### Retest Method
1. Navigate to `/debug/crash-test`.
2. Verify generic 500 error page displays with no directory paths or stack trace.
3. Inspect HTTP response headers in browser DevTools Network tab.

---

## 4. Remediation for A06: Outdated Components

### Original Weakness
Pinned dependency `Werkzeug==2.2.2` has known security advisories (CVE-2023-25577, CVE-2023-46136).

### Root Cause
Unmaintained requirement pinning without dependency scanning.

### Security Fix
Updated dependency baseline in `requirements-fixed.txt` to modern patched releases:
```text
Flask>=3.0.0
Werkzeug>=3.0.3
Jinja2>=3.1.4
itsdangerous>=2.2.0
click>=8.1.7
```

### Expected Result
Automated software composition analysis tools detect zero known high-severity vulnerabilities.

### Retest Method
Run `pip-audit -r requirements-fixed.txt` to confirm no vulnerabilities found.

---

## 5. Remediation for A07: Authentication / Session Weaknesses

### Original Weakness
Session cookie created without `HttpOnly` or `SameSite` flags; user registration allowed 1-character passwords.

### Root Cause
Insecure session configuration defaults and missing password complexity validation.

### Security Fix
1. Enabled `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SAMESITE = 'Lax'`.
2. Enforced password complexity regex on registration requiring uppercase, lowercase, number, and special character (minimum 8 characters).

### Expected Result
JavaScript access to session cookies via `document.cookie` is blocked; weak passwords are rejected during account creation.

### Retest Method
1. Inspect `session` cookie in browser Application tab to verify `HttpOnly` and `SameSite` flags.
2. Attempt registration with weak password `test` and verify rejection.

---

## 6. Remediation for A09: Security Logging & Monitoring

### Original Weakness
Security-critical operations (failed logins, unauthorized access attempts) occurred silently with no audit trail.

### Root Cause
Absence of structured logging instrumentation.

### Security Fix
Created a dedicated `log_security_event()` logging function that writes timestamped records to `logs/security.log` and the `security_logs` database table.

### Expected Result
Every authentication failure, IDOR probe, and administrator action is recorded persistently for monitoring and incident response.

### Retest Method
1. Submit an invalid password at `/login`.
2. Check `logs/security.log` and the `/security-lab` audit log table to confirm event capture.
