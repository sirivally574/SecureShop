"""
SecureShop - Educational E-Commerce Security Laboratory
Authorized Local Cybersecurity Lab (127.0.0.1:8080)

Demonstrating the Complete Security Lifecycle:
BUILD -> EXPOSE -> SCAN -> INVESTIGATE -> EXPLOIT SAFELY -> FIX -> RETEST -> REPORT

OWASP Categories Demonstrated:
- A01:2021 - Broken Access Control (IDOR on /orders/<id>)
- A03:2021 - Injection (SQL Injection on Product Search)
- A05:2021 - Security Misconfiguration (Debug Mode, Verbose Errors & Missing Headers)
- A06:2021 - Vulnerable & Outdated Components (requirements-vulnerable.txt vs requirements-fixed.txt)
- A07:2021 - Authentication / Session Weaknesses (Insecure Session Flags & Password Complexity)
- A09:2021 - Security Logging & Monitoring Failures (Audit Trail Implementation)
"""

import os
import re
import json
import sqlite3
import traceback
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------
# APPLICATION SETUP & CONFIGURATION
# ---------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secureshop-insecure-lab-secret-key-2026")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "secureshop.db")
LOG_PATH = os.path.join(BASE_DIR, "logs", "security.log")
CONFIG_STATE_PATH = os.path.join(BASE_DIR, "config_state.json")

os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)

# ---------------------------------------------------------
# WSGI ZERO-CONFIG AUTO-INITIALIZATION (Render / Gunicorn)
# ---------------------------------------------------------
if not os.path.exists(DB_PATH):
    try:
        import init_db
        init_db.init_db()
    except Exception as e:
        print(f"[!] Warning: Could not auto-initialize DB: {e}")

LOGO_PATH = os.path.join(BASE_DIR, "static", "images", "logo.svg")
if not os.path.exists(LOGO_PATH):
    try:
        import generate_assets
    except Exception as e:
        print(f"[!] Warning: Could not auto-generate SVG assets: {e}")

# ---------------------------------------------------------
# SECURITY MODE MANAGEMENT (Vulnerable vs Fixed)
# ---------------------------------------------------------
def is_public_deploy():
    """
    Returns True if running in a public cloud hosting environment (Render, production, etc.).
    When True, the application STRICTLY forces FIXED MODE and disables
    mode switching to prevent exposing vulnerabilities publicly.
    """
    return bool(
        os.environ.get("RENDER")
        or os.environ.get("RENDER_SERVICE_ID")
        or os.environ.get("ENVIRONMENT") == "production"
        or os.environ.get("PUBLIC_DEPLOYMENT") == "true"
    )

def get_security_mode():
    """
    Retrieves active security posture mode:
    - If running in public cloud/Render: ALWAYS returns 'fixed' (enforced)
    - If running locally:
      1. Check config_state.json (allows dynamic lab switching)
      2. Fallback to SECURITY_MODE environment variable
      3. Default to 'vulnerable' for assignment baseline
    """
    if is_public_deploy():
        return "fixed"

    if os.path.exists(CONFIG_STATE_PATH):
        try:
            with open(CONFIG_STATE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("security_mode", "vulnerable")
        except Exception:
            pass
    return os.environ.get("SECURITY_MODE", "vulnerable").lower()

def set_security_mode(mode):
    """Saves security posture mode to config_state.json (localhost only)"""
    if is_public_deploy():
        return "fixed"
    mode = "fixed" if mode == "fixed" else "vulnerable"
    with open(CONFIG_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"security_mode": mode, "updated_at": datetime.now().isoformat()}, f)
    return mode

# ---------------------------------------------------------
# DATABASE CONNECTION HELPER
# ---------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ---------------------------------------------------------
# A09: SECURITY AUDIT LOGGING HELPER
# ---------------------------------------------------------
def log_security_event(event_type, details, severity="INFO", username=None):
    """
    OWASP A09 Logging & Monitoring:
    In Fixed Mode, records security-relevant events to database and persistent log file.
    In Vulnerable Mode, minimal/no logging takes place to demonstrate monitoring weakness.
    """
    mode = get_security_mode()
    if mode == "vulnerable":
        # INTENTIONALLY VULNERABLE - SECURITY LAB
        # In vulnerable mode, security-critical events pass unrecorded (A09 demonstration)
        return

    # SECURITY FIX: Structured security event recording
    user = username or session.get("username", "ANONYMOUS")
    ip_addr = request.remote_addr or "127.0.0.1"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"[{timestamp}] [{severity}] [{event_type}] User: {user} | IP: {ip_addr} | Details: {details}\n"
    
    # Write to security.log file
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[-] Failed to write to log file: {e}")

    # Write to database audit table
    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO security_logs (timestamp, event_type, username, ip_address, details, severity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, event_type, user, ip_addr, details, severity))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[-] Failed to write to security_logs table: {e}")

# ---------------------------------------------------------
# A05 & A07: HTTP RESPONSE HEADERS & SESSION SECURITY
# ---------------------------------------------------------
@app.before_request
def configure_session_security():
    """
    OWASP A07: Session Cookie Configuration
    Dynamically adjusts session cookie parameters based on active security mode.
    """
    mode = get_security_mode()
    if mode == "vulnerable":
        # INTENTIONALLY VULNERABLE - SECURITY LAB
        # Missing HttpOnly and SameSite=None allows JavaScript access and CSRF exposure
        app.config["SESSION_COOKIE_HTTPONLY"] = False
        app.config["SESSION_COOKIE_SAMESITE"] = None
        app.config["SESSION_COOKIE_SECURE"] = False
    else:
        # SECURITY FIX
        # Strict session protection flags
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = False  # Local HTTP lab testing

@app.after_request
def apply_security_headers(response):
    """
    OWASP A05: Security Misconfiguration - HTTP Headers
    In Fixed Mode: Injects defensive headers (X-Frame-Options, CSP, nosniff).
    In Vulnerable Mode: Omits defensive headers and exposes server banner.
    """
    mode = get_security_mode()
    if mode == "vulnerable":
        # INTENTIONALLY VULNERABLE - SECURITY LAB
        # Missing X-Frame-Options, CSP, X-Content-Type-Options; leaks server info
        response.headers["Server"] = "SecureShop-Dev/1.0 (Python/Flask-Debug)"
    else:
        # SECURITY FIX
        # Defensive HTTP security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers.pop("Server", None)
    return response

# ---------------------------------------------------------
# CONTEXT PROCESSOR (Globally available variables in templates)
# ---------------------------------------------------------
@app.context_processor
def inject_global_template_vars():
    mode = get_security_mode()
    cart_count = 0
    if session.get("user_id"):
        try:
            conn = get_db()
            row = conn.execute("""
                SELECT SUM(ci.quantity) as count
                FROM cart c
                JOIN cart_items ci ON c.id = ci.cart_id
                WHERE c.user_id = ?
            """, (session["user_id"],)).fetchone()
            if row and row["count"]:
                cart_count = row["count"]
            conn.close()
        except Exception:
            pass
    return {
        "security_mode": mode,
        "is_public_deploy": is_public_deploy(),
        "cart_count": cart_count,
        "current_user": session.get("username"),
        "is_admin": session.get("role") == "admin"
    }

# ---------------------------------------------------------
# AUTHENTICATION DECORATORS
# ---------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Administrator login required.", "warning")
            return redirect(url_for("admin_login", next=request.url))
        if session.get("role") != "admin":
            log_security_event("UNAUTHORIZED_ADMIN_ACCESS_ATTEMPT", f"User attempted admin route {request.path}", "CRITICAL")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# PUBLIC ROUTES
# ---------------------------------------------------------
@app.route("/")
def index():
    """Home page with hero banner and featured products"""
    conn = get_db()
    featured = conn.execute("SELECT * FROM products ORDER BY id ASC LIMIT 4;").fetchall()
    conn.close()
    return render_template("index.html", featured_products=featured)

@app.route("/products")
def products():
    """
    Product catalogue and search.
    OWASP A03 Demonstration (SQL Injection):
    - In Vulnerable Mode: uses raw SQL string concatenation with user input 'q'.
    - In Fixed Mode: uses parameterized queries.
    """
    mode = get_security_mode()
    search_query = request.args.get("q", "").strip()
    active_category = request.args.get("category", "").strip()

    conn = get_db()
    cursor = conn.cursor()

    if search_query:
        if mode == "vulnerable":
            # ---------------------------------------------------------
            # INTENTIONALLY VULNERABLE - SECURITY LAB
            # OWASP A03: SQL Injection via unsanitized query formatting
            # ---------------------------------------------------------
            raw_sql = (
                f"SELECT * FROM products "
                f"WHERE name LIKE '%{search_query}%' OR description LIKE '%{search_query}%';"
            )
            try:
                cursor.execute(raw_sql)
                product_list = cursor.fetchall()
            except sqlite3.OperationalError as e:
                # In vulnerable debug mode, surface the database error
                flash(f"SQL Syntax Error: {e}", "danger")
                product_list = []
        else:
            # ---------------------------------------------------------
            # SECURITY FIX
            # OWASP A03: Parameterized prepared statement
            # ---------------------------------------------------------
            like_param = f"%{search_query}%"
            cursor.execute(
                "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?;",
                (like_param, like_param)
            )
            product_list = cursor.fetchall()
    elif active_category:
        cursor.execute("SELECT * FROM products WHERE category = ?;", (active_category,))
        product_list = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM products ORDER BY id ASC;")
        product_list = cursor.fetchall()

    conn.close()
    return render_template(
        "products.html",
        products=product_list,
        search_query=search_query,
        active_category=active_category
    )

@app.route("/products/<int:product_id>")
def product_details(product_id):
    """Detailed view for single product"""
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?;", (product_id,)).fetchone()
    conn.close()
    if not product:
        abort(404)
    return render_template("product_details.html", product=product)

# ---------------------------------------------------------
# AUTHENTICATION: REGISTER, LOGIN, LOGOUT
# ---------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    User Registration
    OWASP A07 Demonstration:
    - In Vulnerable Mode: weak password complexity allowed.
    - In Fixed Mode: strong password complexity validated.
    """
    mode = get_security_mode()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not (name and username and email and password):
            flash("All fields are mandatory.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        # Password complexity validation
        if mode == "fixed":
            # SECURITY FIX: Enforce minimum 8 chars, uppercase, lowercase, digit, special symbol
            password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            if not re.match(password_regex, password):
                flash(
                    "Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character.",
                    "danger"
                )
                return render_template("register.html")

        conn = get_db()
        cursor = conn.cursor()

        # Check existing username or email
        existing = cursor.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?;",
            (username, email)
        ).fetchone()

        if existing:
            conn.close()
            flash("Username or Email already registered. Please sign in.", "warning")
            return redirect(url_for("login"))

        hashed_pw = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, username, email, password, role) VALUES (?, ?, ?, ?, 'customer');",
            (name, username, email, hashed_pw)
        )
        new_uid = cursor.lastrowid
        # Initialize cart for new user
        cursor.execute("INSERT INTO cart (user_id) VALUES (?);", (new_uid,))
        conn.commit()
        conn.close()

        log_security_event("AUTH_USER_REGISTERED", f"New user '{username}' registered with ID {new_uid}", "INFO", username)
        flash("Registration successful! You may now sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Customer Login endpoint"""
    if request.method == "POST":
        identifier = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?;",
            (identifier, identifier)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            log_security_event("AUTH_LOGIN_SUCCESS", f"User '{user['username']}' successfully logged in", "INFO", user["username"])
            flash(f"Welcome back, {user['name']}!", "success")

            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("index"))
        else:
            log_security_event("AUTH_LOGIN_FAILURE", f"Failed authentication attempt for username: {identifier}", "WARNING", identifier)
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Dedicated Administrator Login endpoint"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND role = 'admin';",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["name"] = user["name"]
            session["role"] = "admin"

            log_security_event("AUTH_ADMIN_LOGIN_SUCCESS", f"Admin '{username}' successfully authenticated", "INFO", username)
            flash("Administrator authentication confirmed.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            log_security_event("AUTH_ADMIN_LOGIN_FAILURE", f"Failed admin login for '{username}'", "CRITICAL", username)
            flash("Invalid administrator credentials.", "danger")

    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    """Terminates session"""
    user = session.get("username")
    log_security_event("AUTH_LOGOUT", f"User '{user}' logged out", "INFO", user)
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))

# ---------------------------------------------------------
# AUTHENTICATED CUSTOMER FEATURES: CART, CHECKOUT, PROFILE, ORDERS
# ---------------------------------------------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile management"""
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_profile":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            if name and email:
                cursor.execute(
                    "UPDATE users SET name = ?, email = ? WHERE id = ?;",
                    (name, email, user_id)
                )
                conn.commit()
                session["name"] = name
                flash("Profile details updated successfully.", "success")
                log_security_event("USER_PROFILE_UPDATED", f"User updated name/email", "INFO")
        elif action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            user = cursor.execute("SELECT password FROM users WHERE id = ?;", (user_id,)).fetchone()
            if not check_password_hash(user["password"], current_pw):
                flash("Current password is incorrect.", "danger")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "danger")
            else:
                cursor.execute(
                    "UPDATE users SET password = ? WHERE id = ?;",
                    (generate_password_hash(new_pw), user_id)
                )
                conn.commit()
                flash("Password changed successfully.", "success")
                log_security_event("USER_PASSWORD_CHANGED", f"User changed account password", "INFO")

    user = cursor.execute("SELECT * FROM users WHERE id = ?;", (user_id,)).fetchone()
    conn.close()
    return render_template("profile.html", user=user)

@app.route("/cart")
@login_required
def cart_view():
    """Shopping cart overview"""
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()

    # Ensure user has a cart
    cart = cursor.execute("SELECT id FROM cart WHERE user_id = ?;", (user_id,)).fetchone()
    if not cart:
        cursor.execute("INSERT INTO cart (user_id) VALUES (?);", (user_id,))
        conn.commit()
        cart = cursor.execute("SELECT id FROM cart WHERE user_id = ?;", (user_id,)).fetchone()

    items = cursor.execute("""
        SELECT ci.id as item_id, ci.quantity, p.id as product_id, p.name, p.price, p.image, p.category
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = ?;
    """, (cart["id"],)).fetchall()
    conn.close()

    subtotal = sum(item["price"] * item["quantity"] for item in items)
    shipping = 0.00 if subtotal > 50.00 or subtotal == 0 else 9.99
    tax = subtotal * 0.08
    total = subtotal + shipping + tax

    return render_template(
        "cart.html",
        cart_items=items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        total=total
    )

@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def cart_add(product_id):
    """Adds a product to customer cart"""
    user_id = session["user_id"]
    quantity = int(request.form.get("quantity", 1))

    conn = get_db()
    cursor = conn.cursor()

    cart = cursor.execute("SELECT id FROM cart WHERE user_id = ?;", (user_id,)).fetchone()
    if not cart:
        cursor.execute("INSERT INTO cart (user_id) VALUES (?);", (user_id,))
        conn.commit()
        cart = cursor.execute("SELECT id FROM cart WHERE user_id = ?;", (user_id,)).fetchone()

    existing_item = cursor.execute(
        "SELECT id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?;",
        (cart["id"], product_id)
    ).fetchone()

    if existing_item:
        cursor.execute(
            "UPDATE cart_items SET quantity = quantity + ? WHERE id = ?;",
            (quantity, existing_item["id"])
        )
    else:
        cursor.execute(
            "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?);",
            (cart["id"], product_id, quantity)
        )

    conn.commit()
    conn.close()

    flash("Item added to cart.", "success")
    return redirect(request.referrer or url_for("cart_view"))

@app.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def cart_update(item_id):
    """Updates item quantity in cart"""
    quantity = int(request.form.get("quantity", 1))
    if quantity < 1:
        quantity = 1

    conn = get_db()
    conn.execute("UPDATE cart_items SET quantity = ? WHERE id = ?;", (quantity, item_id))
    conn.commit()
    conn.close()

    flash("Cart updated.", "info")
    return redirect(url_for("cart_view"))

@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def cart_remove(item_id):
    """Removes an item from cart"""
    conn = get_db()
    conn.execute("DELETE FROM cart_items WHERE id = ?;", (item_id,))
    conn.commit()
    conn.close()

    flash("Item removed from cart.", "info")
    return redirect(url_for("cart_view"))

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """Checkout process: converts cart items into order"""
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()

    cart = cursor.execute("SELECT id FROM cart WHERE user_id = ?;", (user_id,)).fetchone()
    items = cursor.execute("""
        SELECT ci.quantity, p.id as product_id, p.name, p.price
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = ?;
    """, (cart["id"],)).fetchall() if cart else []

    if not items:
        conn.close()
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart_view"))

    subtotal = sum(item["price"] * item["quantity"] for item in items)
    shipping = 0.00 if subtotal > 50.00 else 9.99
    tax = subtotal * 0.08
    total = subtotal + shipping + tax

    if request.method == "POST":
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        zip_code = request.form.get("zip", "").strip()
        full_shipping = f"{address}, {city}, {state} {zip_code}"

        cursor.execute("""
            INSERT INTO orders (user_id, total, status, shipping_address)
            VALUES (?, ?, 'Processing', ?);
        """, (user_id, total, full_shipping))
        order_id = cursor.lastrowid

        for item in items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?);
            """, (order_id, item["product_id"], item["quantity"], item["price"]))

        # Clear cart items
        cursor.execute("DELETE FROM cart_items WHERE cart_id = ?;", (cart["id"],))
        conn.commit()
        conn.close()

        log_security_event("ORDER_CREATED", f"Order #{order_id} created for total ${total:.2f}", "INFO")
        flash(f"Order #{order_id} placed successfully!", "success")
        return redirect(url_for("order_details", order_id=order_id))

    user = cursor.execute("SELECT * FROM users WHERE id = ?;", (user_id,)).fetchone()
    conn.close()
    return render_template(
        "checkout.html",
        user=user,
        cart_items=items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        total=total
    )

@app.route("/orders")
@login_required
def orders():
    """Customer's order history list"""
    user_id = session["user_id"]
    conn = get_db()
    order_list = conn.execute("""
        SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC;
    """, (user_id,)).fetchall()
    conn.close()
    return render_template("orders.html", orders=order_list)

@app.route("/orders/<int:order_id>")
@login_required
def order_details(order_id):
    """
    OWASP A01 Demonstration (Broken Access Control / IDOR):
    - In Vulnerable Mode: The server fetches the order by ID without verifying if
      order['user_id'] == session['user_id'] or role == 'admin'.
      User A can view User B's order by changing the ID in the URL.
    - In Fixed Mode: The server enforces strict ownership authorization:
      Verifies that order['user_id'] == session['user_id'] or role == 'admin',
      aborting with 403 Forbidden and logging an audit event if unauthorized.
    """
    mode = get_security_mode()
    conn = get_db()
    cursor = conn.cursor()

    order = cursor.execute("""
        SELECT o.*, u.name as customer_name, u.username as customer_username, u.email as customer_email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = ?;
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        abort(404)

    # Authorization Check
    current_uid = session.get("user_id")
    is_admin = session.get("role") == "admin"

    if mode == "vulnerable":
        # ---------------------------------------------------------
        # INTENTIONALLY VULNERABLE - SECURITY LAB
        # OWASP A01: Missing authorization check (IDOR)
        # Any authenticated user can view any order by changing the ID
        # ---------------------------------------------------------
        pass
    else:
        # ---------------------------------------------------------
        # SECURITY FIX
        # OWASP A01: Strict server-side ownership authorization
        # ---------------------------------------------------------
        if order["user_id"] != current_uid and not is_admin:
            log_security_event(
                "UNAUTHORIZED_ACCESS_IDOR",
                f"User '{session.get('username')}' (ID: {current_uid}) attempted unauthorized access to Order #{order_id} belonging to User ID {order['user_id']}",
                "CRITICAL"
            )
            conn.close()
            abort(403)

    items = cursor.execute("""
        SELECT oi.*, p.name as product_name, p.category
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?;
    """, (order_id,)).fetchall()
    conn.close()

    return render_template("order_details.html", order=order, items=items)

# ---------------------------------------------------------
# ADMINISTRATIVE BACK-OFFICE ROUTES
# ---------------------------------------------------------
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Administrator control dashboard with metrics and audit previews"""
    conn = get_db()
    cursor = conn.cursor()

    total_users = cursor.execute("SELECT COUNT(*) as c FROM users;").fetchone()["c"]
    total_products = cursor.execute("SELECT COUNT(*) as c FROM products;").fetchone()["c"]
    total_orders = cursor.execute("SELECT COUNT(*) as c FROM orders;").fetchone()["c"]
    rev_row = cursor.execute("SELECT SUM(total) as r FROM orders;").fetchone()
    total_revenue = rev_row["r"] if rev_row and rev_row["r"] else 0.00

    recent_orders = cursor.execute("""
        SELECT o.*, u.name as customer_name, u.email as customer_email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC LIMIT 5;
    """).fetchall()

    recent_logs = cursor.execute("""
        SELECT * FROM security_logs ORDER BY id DESC LIMIT 6;
    """).fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        recent_logs=recent_logs
    )

@app.route("/admin/products")
@admin_required
def admin_products():
    """Product management listing"""
    conn = get_db()
    products_list = conn.execute("SELECT * FROM products ORDER BY id DESC;").fetchall()
    conn.close()
    return render_template("admin_products.html", products=products_list)

@app.route("/admin/products/add", methods=["GET", "POST"])
@admin_required
def admin_product_add():
    """Add new product"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = float(request.form.get("price", 0.0))
        category = request.form.get("category", "").strip()
        stock = int(request.form.get("stock", 10))
        image = request.form.get("image", "headphones.svg")

        conn = get_db()
        conn.execute("""
            INSERT INTO products (name, description, price, category, stock, image)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (name, description, price, category, stock, image))
        conn.commit()
        conn.close()

        log_security_event("ADMIN_PRODUCT_CREATED", f"Admin added product '{name}'", "INFO")
        flash(f"Product '{name}' added successfully.", "success")
        return redirect(url_for("admin_products"))

    return render_template("admin_product_form.html", product=None)

@app.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
@admin_required
def admin_product_edit(product_id):
    """Edit existing product"""
    conn = get_db()
    cursor = conn.cursor()
    product = cursor.execute("SELECT * FROM products WHERE id = ?;", (product_id,)).fetchone()

    if not product:
        conn.close()
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = float(request.form.get("price", 0.0))
        category = request.form.get("category", "").strip()
        stock = int(request.form.get("stock", 10))
        image = request.form.get("image", "headphones.svg")

        cursor.execute("""
            UPDATE products
            SET name = ?, description = ?, price = ?, category = ?, stock = ?, image = ?
            WHERE id = ?;
        """, (name, description, price, category, stock, image, product_id))
        conn.commit()
        conn.close()

        log_security_event("ADMIN_PRODUCT_UPDATED", f"Admin edited product ID {product_id}", "INFO")
        flash(f"Product #{product_id} updated.", "success")
        return redirect(url_for("admin_products"))

    conn.close()
    return render_template("admin_product_form.html", product=product)

@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@admin_required
def admin_product_delete(product_id):
    """Delete a product"""
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?;", (product_id,))
    conn.commit()
    conn.close()

    log_security_event("ADMIN_PRODUCT_DELETED", f"Admin deleted product ID {product_id}", "WARNING")
    flash(f"Product #{product_id} removed.", "info")
    return redirect(url_for("admin_products"))

@app.route("/admin/users")
@admin_required
def admin_users():
    """User accounts listing"""
    conn = get_db()
    users_list = conn.execute("""
        SELECT u.id, u.name, u.username, u.email, u.role, u.created_at,
               (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count
        FROM users u
        ORDER BY u.id ASC;
    """).fetchall()
    conn.close()
    return render_template("admin_users.html", users=users_list)

# ---------------------------------------------------------
# SECURITY LAB & EDUCATIONAL CONTROL DASHBOARDS
# ---------------------------------------------------------
@app.route("/security-lab")
def security_lab():
    """Security Testing Lab Dashboard"""
    mode = get_security_mode()
    conn = get_db()
    logs = conn.execute("SELECT * FROM security_logs ORDER BY id DESC LIMIT 50;").fetchall()
    conn.close()
    return render_template("security_lab.html", security_mode=mode, logs=logs)

@app.route("/security-lab/toggle-mode", methods=["GET", "POST"])
def toggle_security_mode():
    """Toggles between Vulnerable and Fixed security mode (Localhost Only)"""
    if is_public_deploy():
        flash("Mode switching is disabled on public Render deployments. The application remains permanently locked in FIXED MODE for safety.", "warning")
        return redirect(url_for("security_lab"))

    current_mode = get_security_mode()
    new_mode = "fixed" if current_mode == "vulnerable" else "vulnerable"
    set_security_mode(new_mode)

    status_name = "FIXED (Remediated)" if new_mode == "fixed" else "VULNERABLE (Lab Weaknesses Enabled)"
    flash(f"Security Posture switched to: {status_name}", "info")

    next_url = request.form.get("next") or request.referrer or url_for("security_lab")
    return redirect(next_url)

@app.route("/security-report")
def security_report():
    """OWASP ZAP Assessment Report & Manual Tracking Dashboard"""
    conn = get_db()
    findings = conn.execute("SELECT * FROM zap_findings ORDER BY id ASC;").fetchall()
    conn.close()
    return render_template("security_report.html", findings=findings)

@app.route("/security-report/add", methods=["POST"])
def security_report_add():
    """Adds a new manual ZAP finding to the assessment report"""
    alert_name = request.form.get("alert_name", "").strip()
    severity = request.form.get("severity", "Medium")
    owasp_cat = request.form.get("owasp_category", "")
    affected_url = request.form.get("affected_url", "").strip()
    description = request.form.get("description", "").strip()
    evidence = request.form.get("evidence", "").strip()
    status = request.form.get("status", "Pending Test")

    if alert_name and affected_url:
        conn = get_db()
        conn.execute("""
            INSERT INTO zap_findings (alert_name, severity, owasp_category, affected_url, description, evidence, status)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (alert_name, severity, owasp_cat, affected_url, description, evidence, status))
        conn.commit()
        conn.close()
        flash("ZAP scan finding recorded.", "success")

    return redirect(url_for("security_report"))

@app.route("/security-report/delete/<int:finding_id>", methods=["POST"])
def security_report_delete(finding_id):
    """Deletes a finding record"""
    conn = get_db()
    conn.execute("DELETE FROM zap_findings WHERE id = ?;", (finding_id,))
    conn.commit()
    conn.close()
    flash("Finding record removed.", "info")
    return redirect(url_for("security_report"))

@app.route("/workflow")
def workflow():
    """Red Team 8-Stage Lifecycle Guide"""
    return render_template("workflow.html")

@app.route("/learning-objectives")
def learning_objectives():
    """Assignment Learning Objectives Checklist"""
    return render_template("learning_objectives.html")

# ---------------------------------------------------------
# A05 DEMO ROUTE: DEBUG CRASH TEST
# ---------------------------------------------------------
@app.route("/debug/crash-test")
def debug_crash():
    """
    OWASP A05 Demonstration:
    Triggers an unhandled exception to demonstrate verbose traceback leakage
    in Vulnerable Mode vs clean sanitized 500 error in Fixed Mode.
    On public deployments, unhandled crashes are never triggered.
    """
    mode = get_security_mode()
    if is_public_deploy() or mode != "vulnerable":
        flash("Debug crash test simulated. Caught and handled gracefully without exposing tracebacks.", "info")
        return redirect(url_for("security_lab"))

    # INTENTIONALLY VULNERABLE - SECURITY LAB (Localhost Only)
    raise RuntimeError("Intentional unhandled exception for OWASP A05 laboratory validation")

# ---------------------------------------------------------
# CUSTOM ERROR HANDLERS (A05 Verification)
# ---------------------------------------------------------
@app.errorhandler(403)
def forbidden_error(e):
    return render_template("errors/403.html", error_message=str(e)), 403

@app.errorhandler(404)
def not_found_error(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
@app.errorhandler(Exception)
def internal_server_error(e):
    mode = get_security_mode()
    err_trace = traceback.format_exc()
    log_security_event("INTERNAL_SERVER_ERROR", f"Unhandled Exception: {str(e)}", "CRITICAL")

    if mode == "vulnerable" and not is_public_deploy():
        # INTENTIONALLY VULNERABLE - SECURITY LAB (Localhost Only)
        # Exposes full traceback to client
        return render_template("errors/500.html", show_traceback=True, error_details=err_trace), 500
    else:
        # SECURITY FIX
        # Sanitized error response, suppressing implementation internals
        return render_template("errors/500.html", show_traceback=False, error_details=None), 500

# ---------------------------------------------------------
# MAIN EXECUTION ENTRYPOINT
# ---------------------------------------------------------
if __name__ == "__main__":
    # Ensure database is present
    if not os.path.exists(DB_PATH):
        print("[!] Database not found. Initializing database...")
        import init_db
        init_db.init_db()

    active_mode = get_security_mode()
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"

    print("==================================================")
    print(" SecureShop - Authorized Cybersecurity Platform   ")
    print("==================================================")
    print(f" Bind Host & Port:  http://{host}:{port}")
    print(f" Environment:       {'Render / Public Cloud' if is_public_deploy() else 'Localhost Lab'}")
    print(f" Active Mode:       {active_mode.upper()} {'(LOCKED)' if is_public_deploy() else ''}")
    print(f" Lab Accounts:      user / User@123 (Customer)")
    print(f"                    alice / Alice@123 (Customer 2)")
    print(f"                    admin / Admin@123 (Administrator)")
    print(" Scope:             Authorized Testing Only")
    print("==================================================")

    # In vulnerable mode, run with debug=True (localhost only); in fixed mode or public deployment, debug=False
    is_debug = (active_mode == "vulnerable" and not is_public_deploy())
    app.run(host=host, port=port, debug=is_debug)
