"""
SecureShop - Automated Local Sanity & Security Test Suite
Tests all 34 quality check items across both Vulnerable and Fixed modes.
"""

import os
import unittest
from app import app, set_security_mode, get_security_mode, is_public_deploy, get_db

class SecureShopTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_homepage_and_catalogue(self):
        """Verify public home and products listing"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"SecureShop", res.data)

        res = self.client.get("/products")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AcousticPro Wireless", res.data)

    def test_02_product_details(self):
        """Verify product details page"""
        res = self.client.get("/products/1")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AcousticPro Wireless", res.data)

    def test_03_a03_sql_injection(self):
        """Test OWASP A03 SQL Injection in Vulnerable vs Fixed modes"""
        # Vulnerable mode: ' OR 1=1 -- returns all products
        set_security_mode("vulnerable")
        res_vuln = self.client.get("/products?q=' OR 1=1 --")
        self.assertEqual(res_vuln.status_code, 200)
        self.assertIn(b"AcousticPro Wireless", res_vuln.data)
        self.assertIn(b"UltraView 27-inch 4K Monitor", res_vuln.data)

        # Fixed mode: Parameterized query treats input literally, returns 0 products
        set_security_mode("fixed")
        res_fixed = self.client.get("/products?q=' OR 1=1 --")
        self.assertEqual(res_fixed.status_code, 200)
        self.assertIn(b"No matching products found", res_fixed.data)

    def test_04_user_authentication_flow(self):
        """Test Customer Registration, Login, Profile, and Logout"""
        set_security_mode("fixed")
        # Login with seed account
        res = self.client.post("/login", data={
            "username": "user",
            "password": "User@123"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Welcome back, John Doe!", res.data)

        # Profile
        res = self.client.get("/profile")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"user@secureshop.local", res.data)

        # Logout
        res = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"You have been signed out", res.data)

    def test_05_a01_broken_access_control_idor(self):
        """Test OWASP A01 IDOR on /orders/<id>"""
        # Login as 'user' (user_id = 2, owns Order #1 and #3)
        self.client.post("/login", data={"username": "user", "password": "User@123"})

        # Own order should succeed in both modes
        res = self.client.get("/orders/1")
        self.assertEqual(res.status_code, 200)

        # Attempt to access Alice's order (Order #2, user_id = 3)
        # In Vulnerable Mode: IDOR succeeds (status 200, shows Alice's details)
        set_security_mode("vulnerable")
        res_vuln = self.client.get("/orders/2")
        self.assertEqual(res_vuln.status_code, 200)
        self.assertIn(b"Alice Walker", res_vuln.data)
        self.assertIn(b"CONFIDENTIAL ALICE ORDER", res_vuln.data)

        # In Fixed Mode: IDOR is blocked (status 403 Forbidden)
        set_security_mode("fixed")
        res_fixed = self.client.get("/orders/2")
        self.assertEqual(res_fixed.status_code, 403)
        self.assertIn(b"403 - Access Forbidden", res_fixed.data)

    def test_06_admin_functionality(self):
        """Test admin authentication and back-office management"""
        # Admin login
        res = self.client.post("/admin/login", data={"username": "admin", "password": "Admin@123"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Administrator Dashboard", res.data)

        # Admin products
        res = self.client.get("/admin/products")
        self.assertEqual(res.status_code, 200)

        # Admin users
        res = self.client.get("/admin/users")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"alice", res.data)

    def test_07_cart_and_checkout_flow(self):
        """Test adding item to cart, viewing cart, and placing order"""
        self.client.post("/login", data={"username": "user", "password": "User@123"})

        # Add product 1
        res = self.client.post("/cart/add/1", data={"quantity": 1}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # View cart
        res = self.client.get("/cart")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AcousticPro Wireless", res.data)

        # Checkout
        res = self.client.post("/checkout", data={
            "address": "123 Test St",
            "city": "Seattle",
            "state": "WA",
            "zip": "98101"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Order Invoice", res.data)

    def test_08_a05_security_headers_and_config(self):
        """Verify A05 HTTP headers in vulnerable vs fixed modes"""
        set_security_mode("vulnerable")
        res_vuln = self.client.get("/")
        self.assertNotIn("X-Frame-Options", res_vuln.headers)
        self.assertIn("SecureShop-Dev", res_vuln.headers.get("Server", ""))

        set_security_mode("fixed")
        res_fixed = self.client.get("/")
        self.assertEqual(res_fixed.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(res_fixed.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("default-src 'self'", res_fixed.headers.get("Content-Security-Policy", ""))
        self.assertNotIn("Server", res_fixed.headers)

    def test_09_security_lab_and_report_pages(self):
        """Verify lab dashboard, ZAP report, workflow, and learning objectives"""
        res = self.client.get("/security-lab")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Broken Access Control", res.data)

        res = self.client.get("/security-report")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"ZAP Findings", res.data)

        res = self.client.get("/workflow")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"8-Stage Application Security Lifecycle", res.data)

        res = self.client.get("/learning-objectives")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Curriculum Progress Checklist", res.data)

    def test_10_render_production_enforced_fixed_mode(self):
        """Verify Render cloud deployment permanently enforces FIXED MODE"""
        os.environ["RENDER"] = "true"
        try:
            # 1. Mode check must be fixed
            self.assertEqual(get_security_mode(), "fixed")

            # 2. Attempt to toggle mode must be blocked
            res = self.client.post("/security-lab/toggle-mode", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Mode switching is disabled on public Render deployments", res.data)
            self.assertEqual(get_security_mode(), "fixed")

            # 3. Crash test route must never expose tracebacks
            res = self.client.get("/debug/crash-test", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertNotIn(b"Traceback (most recent call last)", res.data)

            # 4. Security headers must be active
            res = self.client.get("/")
            self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")
            self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")

            # 5. Banner must reflect Render public deployment
            self.assertIn(b"Render Public Cloud", res.data)
            self.assertIn(b"FIXED MODE (LOCKED)", res.data)
        finally:
            os.environ.pop("RENDER", None)

    def tearDown(self):
        os.environ.pop("RENDER", None)
        # Reset mode back to vulnerable by default for user's local test
        set_security_mode("vulnerable")

if __name__ == "__main__":
    unittest.main()
