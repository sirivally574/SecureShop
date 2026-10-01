"""
SecureShop - Database Initialization Script
Laboratory / Educational Use Only
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "secureshop.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("[+] Removed old database file.")
        except Exception as e:
            print(f"[-] Could not remove old database: {e}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        stock INTEGER NOT NULL DEFAULT 10,
        image TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Cart Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 4. Cart Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(cart_id) REFERENCES cart(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    """)

    # 5. Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Processing',
        shipping_address TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 6. Order Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    """)

    # 7. Security Audit Log Table (for A09 Monitoring)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT NOT NULL,
        username TEXT,
        ip_address TEXT,
        details TEXT,
        severity TEXT DEFAULT 'INFO'
    );
    """)

    # 8. ZAP Findings Table (for /security-report interactive tracker)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS zap_findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_name TEXT NOT NULL,
        severity TEXT NOT NULL,
        owasp_category TEXT NOT NULL,
        affected_url TEXT NOT NULL,
        description TEXT NOT NULL,
        evidence TEXT,
        status TEXT NOT NULL DEFAULT 'Pending Test'
    );
    """)

    print("[+] Created all database tables.")

    # Seed Accounts
    # Passwords hashed with standard Werkzeug secure hashing
    admin_pw = generate_password_hash("Admin@123")
    user_pw = generate_password_hash("User@123")
    alice_pw = generate_password_hash("Alice@123")

    users_data = [
        ("Security Administrator", "admin", "admin@secureshop.local", admin_pw, "admin"),
        ("John Doe", "user", "user@secureshop.local", user_pw, "customer"),
        ("Alice Walker", "alice", "alice@secureshop.local", alice_pw, "customer")
    ]
    cursor.executemany("""
    INSERT INTO users (name, username, email, password, role)
    VALUES (?, ?, ?, ?, ?)
    """, users_data)
    print(f"[+] Seeded {len(users_data)} users (admin, user, alice).")

    # Seed Products
    products_data = [
        ("AcousticPro Wireless Headphones", "Premium active noise-cancelling over-ear headphones with 40h battery life and spatial audio.", 129.99, "Electronics", 25, "headphones.svg"),
        ("ErgoTech Vertical Mouse", "Ergonomic design reducing wrist strain with adjustable DPI and silent optical switches.", 34.50, "Electronics", 40, "mouse.svg"),
        ("UltraView 27-inch 4K Monitor", "IPS panel with 99% sRGB color gamut, HDR400, and USB-C 65W power delivery.", 399.00, "Electronics", 15, "monitor.svg"),
        ("Mechanical RGB Gaming Keyboard", "Hot-swappable mechanical switches with aluminum top plate and PBT doubleshot keycaps.", 89.99, "Electronics", 18, "keyboard.svg"),
        ("Waterproof Laptop Backpack 25L", "Rugged commuter backpack with padded 16-inch laptop compartment and hidden anti-theft pockets.", 59.95, "Accessories", 50, "backpack.svg"),
        ("Stainless Steel Thermal Bottle", "Double-walled vacuum insulated water bottle keeping liquids cold 24h or hot 12h.", 24.99, "Home & Living", 65, "bottle.svg"),
        ("Classic Oxford Cotton Shirt", "Tailored fit 100% breathable organic cotton button-down shirt for smart casual style.", 45.00, "Apparel", 30, "shirt.svg"),
        ("Smart LED Desk Lamp", "Dimmable desk lamp with wireless Qi smartphone charger and adjustable color temperature.", 49.99, "Home & Living", 22, "lamp.svg")
    ]
    cursor.executemany("""
    INSERT INTO products (name, description, price, category, stock, image)
    VALUES (?, ?, ?, ?, ?, ?)
    """, products_data)
    print(f"[+] Seeded {len(products_data)} sample products.")

    # Create empty carts for users
    for uid in (1, 2, 3):
        cursor.execute("INSERT INTO cart (user_id) VALUES (?)", (uid,))

    # Seed Orders for John (id=2) and Alice (id=3)
    # Order #1 - John Doe (id=2)
    cursor.execute("""
    INSERT INTO orders (id, user_id, total, status, shipping_address)
    VALUES (1, 2, 164.49, 'Delivered', '104 Willow Way, Seattle, WA 98101')
    """)
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1, 1, 1, 129.99)")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1, 2, 1, 34.50)")

    # Order #2 - Alice Walker (id=3) - CONFIDENTIAL ORDER TARGET FOR A01 IDOR
    cursor.execute("""
    INSERT INTO orders (id, user_id, total, status, shipping_address)
    VALUES (2, 3, 399.00, 'Processing', '42 Confidential Avenue, Suite 900, Austin, TX 78701 (CONFIDENTIAL ALICE ORDER)')
    """)
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (2, 3, 1, 399.00)")

    # Order #3 - John Doe (id=2)
    cursor.execute("""
    INSERT INTO orders (id, user_id, total, status, shipping_address)
    VALUES (3, 2, 89.99, 'Shipped', '104 Willow Way, Seattle, WA 98101')
    """)
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (3, 4, 1, 89.99)")
    print("[+] Seeded 3 sample orders with items (Order #1: John, Order #2: Alice, Order #3: John).")

    # Seed Initial ZAP Findings table with clear placeholder records
    findings_data = [
        (
            "Missing Anti-clickjacking Header (X-Frame-Options)",
            "Medium",
            "A05:2021-Security Misconfiguration",
            "http://127.0.0.1:8080/",
            "The response does not include an X-Frame-Options or Content-Security-Policy frame-ancestors header.",
            "Example – replace with actual ZAP result after scanning",
            "Vulnerable in Dev Mode"
        ),
        (
            "Content-Security-Policy (CSP) Header Not Set",
            "Medium",
            "A05:2021-Security Misconfiguration",
            "http://127.0.0.1:8080/",
            "Content Security Policy is an effective defense-in-depth against XSS and injection attacks.",
            "Example – replace with actual ZAP result after scanning",
            "Vulnerable in Dev Mode"
        ),
        (
            "X-Content-Type-Options Header Missing",
            "Low",
            "A05:2021-Security Misconfiguration",
            "http://127.0.0.1:8080/",
            "The Anti-MIME-Sniffing header X-Content-Type-Options was not set to 'nosniff'.",
            "Example – replace with actual ZAP result after scanning",
            "Vulnerable in Dev Mode"
        ),
        (
            "SQL Injection (Manual DAST Validation)",
            "High",
            "A03:2021-Injection",
            "http://127.0.0.1:8080/products?q=",
            "Unsanitized user input is concatenated directly into SQL query in search route.",
            "Example – replace with actual ZAP result after scanning",
            "Vulnerable in Dev Mode"
        ),
        (
            "Insecure Direct Object References (IDOR)",
            "High",
            "A01:2021-Broken Access Control",
            "http://127.0.0.1:8080/orders/2",
            "Access to order records is based solely on URL ID parameter without verifying session user identity.",
            "Example – replace with actual ZAP result after scanning",
            "Vulnerable in Dev Mode"
        )
    ]
    cursor.executemany("""
    INSERT INTO zap_findings (alert_name, severity, owasp_category, affected_url, description, evidence, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, findings_data)
    print(f"[+] Seeded {len(findings_data)} ZAP findings records with lab placeholders.")

    # Initial log entry
    cursor.execute("""
    INSERT INTO security_logs (event_type, username, ip_address, details, severity)
    VALUES ('SYSTEM_INIT', 'system', '127.0.0.1', 'SecureShop database initialized successfully.', 'INFO')
    """)

    conn.commit()
    conn.close()
    print(f"[OK] SecureShop database created successfully at: {DB_PATH}")

if __name__ == "__main__":
    init_db()
