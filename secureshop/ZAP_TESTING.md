# OWASP ZAP Testing Guide – SecureShop Lab

This guide explains how to safely perform Dynamic Application Security Testing (DAST) against the local **SecureShop** web application using **OWASP Zed Attack Proxy (ZAP)**.

> [!CAUTION]
> **AUTHORIZED LOCAL LAB ONLY**  
> All security scanning must be restricted strictly to `http://127.0.0.1:8080` or `http://localhost:8080`.  
> Never target external networks, cloud services, university infrastructure, or systems you do not own.

---

## 1. Prerequisites & Setup
1. **Java Runtime:** Ensure Java 11+ is installed for OWASP ZAP.
2. **OWASP ZAP:** Download and install [OWASP ZAP](https://www.zaproxy.org/download/) (version 2.14 or later).
3. **SecureShop Application:** Running locally in PowerShell / Terminal:
   ```powershell
   python app.py
   ```
4. Verify accessibility in your browser:
   [http://127.0.0.1:8080](http://127.0.0.1:8080)

---

## 2. Step-by-Step ZAP Scanning Procedure

### Step 1: Launch OWASP ZAP & Set Context Scope
1. Open OWASP ZAP.
2. Select **"No, I do not want to persist this session at this moment in time"** (or choose a session name for your college lab report).
3. In the left **Sites** tree, right-click and choose **"Include in Context" > "New Context"**.
4. Set the Context Name to `SecureShop-LocalLab`.
5. Under **Include in Context**, enter:
   ```regex
   \Qhttp://127.0.0.1:8080\E.*
   ```
6. Set the **Target In Scope** checkbox so ZAP will not scan any external URLs.

---

### Step 2: Automated Spider (Crawling)
Crawling maps out the application attack surface:
1. In the ZAP Quick Start tab, select **Automated Scan**.
2. Enter the URL to attack:
   ```text
   http://127.0.0.1:8080/
   ```
3. Check **Use traditional spider**.
4. Click **Attack**.
5. ZAP will crawl all discoverable links, including:
   - `/` (Home)
   - `/products` (Catalogue & Search)
   - `/products/1` through `/products/8` (Product Details)
   - `/login` & `/register`
   - `/admin/login`
   - `/security-lab`, `/security-report`, `/workflow`, `/learning-objectives`

---

### Step 3: Authenticated Crawling (Manual Exploration Proxy)
To allow ZAP to discover authenticated routes (`/cart`, `/checkout`, `/profile`, `/orders`, `/orders/1`):
1. In ZAP, click **Manual Explore**.
2. Enter `http://127.0.0.1:8080`.
3. Select your preferred browser (e.g., Firefox or Chrome) with the ZAP HUD/Proxy enabled.
4. Click **Launch Browser**.
5. In the opened browser window:
   - Log in using Customer credentials: `user` / `User@123`.
   - Add a product to the cart.
   - Proceed to `/cart`, view `/orders`, and open an invoice (`/orders/1`).
6. This feeds the authenticated session tokens directly into ZAP's site tree.

---

### Step 4: Active Scan (DAST Vulnerability Detection)
1. In ZAP's **Sites** pane on the left, locate `http://127.0.0.1:8080`.
2. Right-click the node and select **Attack > Active Scan...**.
3. In the Active Scan dialog:
   - **Starting Point:** `http://127.0.0.1:8080`
   - **Context:** `SecureShop-LocalLab`
   - **Scope:** In Scope only
4. Click **Start Scan**.
5. Observe the **Active Scan** progress tab at the bottom. ZAP will send test payloads against parameters like `q` in `/products`.

---

### Step 5: Reviewing Scanner Alerts
Once the Active Scan finishes, click the **Alerts** tab:
1. Note alerts flagged by ZAP:
   - **A05 Misconfiguration:**
     - *Anti-clickjacking Header Not Set* (Plugin ID: 10020)
     - *Content-Security-Policy (CSP) Header Not Set* (Plugin ID: 10038)
     - *X-Content-Type-Options Header Missing* (Plugin ID: 10021)
     - *Server Leaks Information via "Server" Header* (Plugin ID: 10036)
   - **A03 Injection:**
     - *SQL Injection* probes on `GET /products?q=`
   - **A07 Session:**
     - *Cookie Without SameSite Attribute* (Plugin ID: 10054)
     - *Cookie No HttpOnly Flag* (Plugin ID: 10010)

---

### Step 6: Recording Findings into SecureShop
SecureShop includes an interactive reporting page to document your results:
1. Navigate to:
   [http://127.0.0.1:8080/security-report](http://127.0.0.1:8080/security-report)
2. Scroll to the **"Record Actual OWASP ZAP Scan Alert"** section.
3. Fill in:
   - **Alert Name:** e.g., `Content-Security-Policy (CSP) Header Not Set`
   - **Severity:** High / Medium / Low / Informational
   - **OWASP Category:** `A05:2021-Security Misconfiguration`
   - **Affected URL:** `http://127.0.0.1:8080/`
   - **Description:** Copy description from ZAP Alert tab.
   - **Evidence:** Paste the HTTP response header or payload.
4. Click **Add ZAP Finding to Report**.

---

### Step 7: Exporting ZAP Report
1. In ZAP, click **Report > Generate Report...**.
2. Select **Traditional HTML Report** or **Modern High-Level Report**.
3. Choose the export directory inside your project folder:
   `secureshop/reports/zap-report-vulnerable.html`
4. Click **Generate Report**.

---

### Step 8: Retesting in FIXED Mode
1. In SecureShop, click **Switch to FIXED Mode** in the top navigation banner.
2. Clear previous scan sessions in ZAP (**File > New Session**).
3. Re-run the Spider and Active Scan against `http://127.0.0.1:8080/`.
4. Observe that:
   - Missing header alerts (10020, 10038, 10021) are resolved.
   - SQL injection attempts against `/products?q=` are neutralized.
   - Server identification banner is removed.
5. Export the retest report:
   `secureshop/reports/zap-report-fixed.html`.
