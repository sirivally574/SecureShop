# SecureShop – Build → Attack → Identify → Fix → Retest

> **AUTHORIZED CYBERSECURITY LAB ONLY**  
> *"This application is intentionally vulnerable and is designed only for authorized local security testing."*  
> Scope is restricted strictly to local testing on `http://127.0.0.1:8080` or `http://localhost:8080`.  
> Do **NOT** deploy this application to public internet servers or use its concepts to target unauthorized systems.

---

## 1. Project Title
**SecureShop: An Educational Application Security & Red Team Lifecycle Lab**

---

## 2. Assignment Objective
This project demonstrates the complete end-to-end security lifecycle required for college Red Team and Application Security coursework:
$$\text{BUILD} \longrightarrow \text{EXPOSE} \longrightarrow \text{SCAN} \longrightarrow \text{INVESTIGATE} \longrightarrow \text{EXPLOIT SAFELY} \longrightarrow \text{FIX} \longrightarrow \text{RETEST} \longrightarrow \text{REPORT}$$

Students learn to:
1. Build a realistic, responsive web application.
2. Identify architectural attack surfaces and third-party dependencies.
3. Perform Dynamic Application Security Testing (DAST) using **OWASP ZAP**.
4. Conduct safe, controlled manual proof-of-concept validations for logic and injection flaws.
5. Implement secure coding mitigations across multiple OWASP Top 10 categories.
6. Retest the application to empirically verify vulnerability remediation.
7. Collect before-and-after evidence for technical presentation and reporting.

---

## 3. Project Scenario
**Company:** SecureShop  
**Context:** SecureShop is a realistic internal e-commerce application featuring product catalog browsing, keyword search, shopping cart management, customer order history, user profiles, and an administrator back-office.  

Management suspected that the application was developed using outdated software components and insecure development practices. The security team was tasked with answering:
> *"How vulnerable is the application, and can we prove that our remediation actually works?"*

SecureShop is built with a dual security architecture (**Vulnerable Mode** vs. **Fixed Mode**), allowing immediate comparative demonstration during evaluation.

---

## 4. Technology Stack
- **Backend:** Python 3.11+ using the lightweight **Flask** WSGI microframework
- **Database:** **SQLite 3** (`database/secureshop.db`) with modular relational schema (users, products, cart, cart_items, orders, order_items, security_logs, zap_findings)
- **Frontend:** Responsive **HTML5**, **CSS3**, and **JavaScript** (100% offline, self-contained SVG assets, no external CDN dependencies)
- **Testing Tools:** OWASP ZAP 2.14+, `pip-audit`, Python `unittest`

---

## 5. Project Directory Structure
```text
secureshop/
│
├── app.py                      # Main Flask application with routes, vulnerabilities & fixes
├── init_db.py                  # Database schema creation and seed data initialization
├── generate_assets.py          # Offline SVG placeholder icon and logo generator
├── test_app.py                 # Automated unit and security validation test suite
├── requirements.txt            # Default requirements
├── requirements-vulnerable.txt # Intentionally outdated dependencies for A06 demo
├── requirements-fixed.txt      # Remediated dependency baseline
├── README.md                   # Comprehensive project documentation
├── VULNERABILITY_MATRIX.md     # OWASP vulnerability matrix table
├── SECURITY_FINDINGS.md        # Technical investigations (WHAT, WHERE, WHY, etc.)
├── REMEDIATION.md              # Code diffs and remediation documentation
├── ZAP_TESTING.md              # OWASP ZAP step-by-step testing guide
├── config_state.json           # Runtime security mode state file
│
├── database/
│   └── secureshop.db           # SQLite relational database
│
├── logs/
│   └── security.log            # A09 audit trail log file
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean, responsive e-commerce stylesheet
│   ├── js/
│   │   └── main.js             # Interactive helpers (clipboard copy, alert dismiss)
│   └── images/                 # SVG assets (logo, headphones, monitor, etc.)
│
└── templates/
    ├── base.html               # Common layout with mode badge and navigation
    ├── index.html              # Home page with hero and featured products
    ├── products.html           # Catalogue and search (A03 Injection Site)
    ├── product_details.html    # Product detail page
    ├── cart.html               # Shopping cart
    ├── checkout.html           # Order placement checkout
    ├── orders.html             # Order history list
    ├── order_details.html      # Invoice details (A01 IDOR Site)
    ├── profile.html            # User account profile
    ├── login.html              # Customer login
    ├── register.html           # Customer registration
    ├── admin_login.html        # Administrator authentication portal
    ├── admin_dashboard.html    # Admin metrics and recent orders
    ├── admin_products.html     # Product management CRUD
    ├── admin_product_form.html # Add/edit product form
    ├── admin_users.html        # Registered users listing
    ├── security_lab.html       # Interactive Security Lab control dashboard
    ├── security_report.html    # ZAP scan findings report & manual tracker
    ├── workflow.html           # 8-stage Red Team lifecycle guide
    ├── learning_objectives.html# 10-point academic checklist
    └── errors/
        ├── 403.html            # 403 Forbidden page
        ├── 404.html            # 404 Not Found page
        └── 500.html            # 500 Internal Error (A05 traceback demo)
```

---

## 6. Installation & Setup

### Step 1: Open PowerShell / Terminal
Navigate to the project root:
```powershell
cd C:\Users\GOPICHAND\.gemini\antigravity\scratch\secureshop
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
For the baseline (remediated) environment:
```powershell
pip install -r requirements.txt
```

To demonstrate outdated dependencies for vulnerability scanning (A06):
```powershell
pip install -r requirements-vulnerable.txt
```

### Step 4: Initialize the Database & Assets
```powershell
python init_db.py
python generate_assets.py
```

### Step 5: Start the Application
```powershell
python app.py
```
Access the application in your browser at:  
👉 **`http://127.0.0.1:8080`**

---

## 7. Demo Accounts & Credentials
All accounts are pre-seeded in the database for lab testing only:

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Customer 1** | `user` | `User@123` | Owns Order #1 & #3. Used for IDOR and shopping tests. |
| **Customer 2** | `alice` | `Alice@123` | Owns confidential Order #2 ($399.00 monitor). Target for IDOR. |
| **Administrator** | `admin` | `Admin@123` | Back-office management at `/admin/dashboard`. |

---

## 8. Vulnerable Mode vs. Fixed Mode

SecureShop includes an instant posture toggle that allows you to demonstrate "Before Fix vs. After Fix" live during presentations:

### How to Toggle Modes:
1. **Interactive UI:** Click the **"Switch to FIXED Mode"** / **"Switch to VULNERABLE Mode"** button in the top navigation banner or on the `/security-lab` page.
2. **Environment Variable:** Set before starting `app.py`:
   ```powershell
   $env:SECURITY_MODE="vulnerable"   # Enables controlled weaknesses
   python app.py
   ```
   Or:
   ```powershell
   $env:SECURITY_MODE="fixed"        # Enables full security mitigations
   python app.py
   ```

---

## 9. Controlled Vulnerabilities & OWASP Mapping

| ID | OWASP Category | Vulnerability | Location | Vulnerable Behavior | Remediated Behavior |
|---|---|---|---|---|---|
| 1 | **A01:2021** | Broken Access Control (IDOR) | `/orders/<order_id>` | User `user` can view Alice's order #2 by modifying URL. | Strict ownership check returns `403 Forbidden` and logs event. |
| 2 | **A03:2021** | SQL Injection | `/products?q=` | Raw query concatenation; `' OR 1=1 --` returns all rows. | Parameterized queries treat input as literal text (0 matches). |
| 3 | **A05:2021** | Security Misconfiguration | `/debug/crash-test`, Headers | `DEBUG=True`, stack traces leaked, missing security headers. | `DEBUG=False`, sanitized 500 error, strict headers (CSP, nosniff, DENY). |
| 4 | **A06:2021** | Outdated Components | `requirements-vulnerable.txt` | Pinned `Werkzeug==2.2.2` (Multipart DoS CVE-2023-25577). | Upgraded to `Werkzeug>=3.0.3` in `requirements-fixed.txt`. |
| 5 | **A07:2021** | Authentication Failures | `/register`, Cookie flags | Missing `HttpOnly`/`SameSite`, 1-character password accepted. | `HttpOnly=True`, `SameSite=Lax`, 8+ char regex password complexity. |
| 6 | **A09:2021** | Logging & Monitoring Failures | App event handling | Failed logins and IDOR probes pass unrecorded. | Structured logging to `logs/security.log` and database audit table. |

---

## 10. Outdated Dependency Reference (A06)

| Component | Vulnerable Version | Fixed Version | Security Concern | CVE / Advisory Reference |
|---|---|---|---|---|
| **Werkzeug** | `2.2.2` | `3.0.3`+ | High Denial of Service risk via unconstrained multipart/form-data parsing; resource exhaustion. | **CVE-2023-25577**, **CVE-2023-46136** |
| **Flask** | `2.2.5` | `3.1.3`+ | Older framework baseline lacking latest secure cookie defaults. | Upstream maintenance release |
| **Jinja2** | `3.1.2` | `3.1.6`+ | Potential compiler sandbox escape under specific template configurations. | **CVE-2024-34064** |

---

## 11. Step-by-Step Safe Manual Validation

### 1. Validating A01 (IDOR)
1. Ensure mode is **VULNERABLE MODE**.
2. Sign in as `user` with password `User@123`.
3. Browse to `/orders`. Notice you own Order #1 and #3.
4. Alter the URL to: `http://127.0.0.1:8080/orders/2`.
5. **Observed:** Alice Walker's confidential invoice and shipping address are exposed!
6. Click **Switch to FIXED Mode** in the header banner. Refresh `/orders/2`.
7. **Observed:** Access is blocked with **403 - Access Forbidden** and an audit entry is logged.

### 2. Validating A03 (SQL Injection)
1. Ensure mode is **VULNERABLE MODE**.
2. Go to `/products` and type `' OR 1=1 --` into the search bar.
3. **Observed:** The query evaluates to true; all 8 products in the database are returned.
4. Click **Switch to FIXED Mode** and run the same search.
5. **Observed:** Zero products matched safely without any database errors.

### 3. Validating A05 (Security Misconfiguration)
1. In **VULNERABLE MODE**, navigate to `http://127.0.0.1:8080/debug/crash-test`.
2. **Observed:** Full Python traceback and local disk paths are exposed.
3. In **FIXED MODE**, visit the same route.
4. **Observed:** The crash is safely caught; generic error page displayed with no stack trace.

---

## 12. OWASP ZAP Testing Procedure
Detailed instructions are available in [ZAP_TESTING.md](file:///C:/Users/GOPICHAND/.gemini/antigravity/scratch/secureshop/ZAP_TESTING.md).
Brief summary:
1. Start SecureShop: `python app.py`
2. Open ZAP and define context scope: `http://127.0.0.1:8080/.*`
3. Run **Automated Spider** to map out endpoints.
4. Run **Active Scan** against the mapped target.
5. Review generated alerts in the **Alerts** tab (clickjacking, missing CSP, SQLi).
6. Record findings into the interactive dashboard at:  
   👉 **`http://127.0.0.1:8080/security-report`**
7. Switch to **FIXED Mode** and rescan to demonstrate alert elimination.

---

## 13. Running Automated Tests
To run the automated regression test suite:
```powershell
python test_app.py
```
This tests all 9 core functional and security suites (IDOR, SQLi, headers, auth, checkout, admin, lab dashboards) across both modes.

---

## 14. College Presentation Walkthrough

Use this sequence to present your project to professors or evaluators:

1. **Introduction:** Show the home page (`/`) and explain that SecureShop is a realistic e-commerce application.
2. **Architecture:** Show the database schema in `init_db.py` and the 8-stage lifecycle in `/workflow`.
3. **Scan Phase:** Show OWASP ZAP alerts and the live findings table at `/security-report`.
4. **Vulnerable State Demonstration:**
   - Demonstrate IDOR: Log in as `user` and access Alice's invoice at `/orders/2`.
   - Demonstrate SQLi: Search `' OR 1=1 --` on `/products`.
   - Demonstrate Misconfiguration: Visit `/debug/crash-test` to reveal stack traces.
5. **Remediation Walkthrough:** Walk through the code diffs in [REMEDIATION.md](file:///C:/Users/GOPICHAND/.gemini/antigravity/scratch/secureshop/REMEDIATION.md).
6. **Fixed State Demonstration:**
   - Click **"Switch to FIXED Mode"**.
   - Show `/orders/2` returning **403 Forbidden**.
   - Show search treating `' OR 1=1 --` safely as literal text.
   - Show live audit log in `/security-lab` proving the IDOR attempt was caught.
7. **Conclusion:** Show the Before vs After matrix at `/security-report` and the 10-point checklist at `/learning-objectives`.

---

## 15. Deploying on Render (Public Deployment Safety)

SecureShop is prepared for deployment to [Render](https://render.com) using **Gunicorn** and includes strict safeguards to ensure that public instances **NEVER expose vulnerable mode**.

### Public Deployment Safety Guarantee:
- **Permanently Enforced Fixed Mode:** When running on Render (detected via `RENDER=true` or `RENDER_SERVICE_ID`), the application permanently locks security mode to **FIXED**.
- **Mode Switching Disabled:** The `/security-lab/toggle-mode` route is disabled on public deployments to prevent anyone from toggling weaknesses over the public Internet.
- **Traceback Leaks Neutralized:** The `/debug/crash-test` route does not trigger unhandled exceptions in production.
- **Localhost Only Vulnerability Lab:** Vulnerable mode remains available **strictly on localhost (127.0.0.1)** for your authorized local testing.

### Render Deployment Configuration:
- **Blueprint File:** [`render.yaml`](file:///C:/Users/GOPICHAND/.gemini/antigravity/scratch/secureshop/render.yaml)
- **Build Command:**
  ```bash
  pip install -r requirements.txt && python init_db.py && python generate_assets.py
  ```
- **Start Command:**
  ```bash
  gunicorn app:app
  ```
- **Environment Variables on Render:**
  - `RENDER`: `true`
  - `SECURITY_MODE`: `fixed`
  - `PYTHON_VERSION`: `3.11.9`
  - `SECRET_KEY`: Automatically generated by Render
- **Auto-Initialization:** Even if the build step is skipped or ephemeral storage resets, `app.py` automatically initializes and seeds `secureshop.db` and SVG assets upon module load.
