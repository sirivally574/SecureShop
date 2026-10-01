"""
Generate clean SVG product placeholders and logo for SecureShop
Runs entirely offline without external assets.
"""
import os

IMG_DIR = os.path.join(os.path.dirname(__file__), "static", "images")
os.makedirs(IMG_DIR, exist_ok=True)

def write_svg(filename, content):
    with open(os.path.join(IMG_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content.strip())

# 1. Logo
write_svg("logo.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 60" width="240" height="60">
  <defs>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4F46E5" />
      <stop offset="100%" stop-color="#06B6D4" />
    </linearGradient>
  </defs>
  <rect x="5" y="8" width="44" height="44" rx="10" fill="url(#brandGrad)" />
  <path d="M27 16 L37 20 V28 C37 35 32 40 27 42 C22 40 17 35 17 28 V20 Z" fill="#FFFFFF" />
  <path d="M23 29 L26 32 L31 26" stroke="#4F46E5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none" />
  <text x="58" y="38" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="800" font-size="24" fill="#0F172A" letter-spacing="-0.5">Secure<tspan fill="#4F46E5">Shop</tspan></text>
</svg>
""")

# 2. Headphones
write_svg("headphones.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#F1F5F9"/>
  <circle cx="200" cy="150" r="110" fill="#E2E8F0"/>
  <path d="M140 170 C140 100 260 100 260 170" fill="none" stroke="#334155" stroke-width="16" stroke-linecap="round"/>
  <rect x="120" y="150" width="30" height="65" rx="12" fill="#1E293B"/>
  <rect x="250" y="150" width="30" height="65" rx="12" fill="#1E293B"/>
  <rect x="110" y="160" width="16" height="45" rx="8" fill="#6366F1"/>
  <rect x="274" y="160" width="16" height="45" rx="8" fill="#6366F1"/>
  <text x="200" y="260" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#64748B">AcousticPro Wireless</text>
</svg>
""")

# 3. Mouse
write_svg("mouse.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#F1F5F9"/>
  <circle cx="200" cy="150" r="110" fill="#E2E8F0"/>
  <rect x="160" y="90" width="80" height="125" rx="40" fill="#1E293B"/>
  <line x1="200" y1="90" x2="200" y2="140" stroke="#475569" stroke-width="3"/>
  <rect x="194" y="105" width="12" height="22" rx="6" fill="#06B6D4"/>
  <text x="200" y="260" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#64748B">ErgoTech Vertical Mouse</text>
</svg>
""")

# 4. Monitor
write_svg("monitor.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#F1F5F9"/>
  <circle cx="200" cy="150" r="110" fill="#E2E8F0"/>
  <rect x="100" y="70" width="200" height="120" rx="8" fill="#0F172A"/>
  <rect x="108" y="78" width="184" height="104" rx="4" fill="#38BDF8" opacity="0.85"/>
  <rect x="185" y="190" width="30" height="35" fill="#475569"/>
  <rect x="160" y="225" width="80" height="8" rx="4" fill="#334155"/>
  <text x="200" y="265" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#64748B">UltraView 4K Monitor</text>
</svg>
""")

# 5. Keyboard
write_svg("keyboard.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#F1F5F9"/>
  <circle cx="200" cy="150" r="110" fill="#E2E8F0"/>
  <rect x="90" y="110" width="220" height="90" rx="10" fill="#1E293B"/>
  <rect x="105" y="125" width="24" height="20" rx="4" fill="#6366F1"/>
  <rect x="135" y="125" width="24" height="20" rx="4" fill="#475569"/>
  <rect x="165" y="125" width="24" height="20" rx="4" fill="#475569"/>
  <rect x="195" y="125" width="24" height="20" rx="4" fill="#475569"/>
  <rect x="225" y="125" width="24" height="20" rx="4" fill="#475569"/>
  <rect x="255" y="125" width="38" height="20" rx="4" fill="#EF4444"/>
  <rect x="105" y="155" width="34" height="20" rx="4" fill="#475569"/>
  <rect x="145" y="155" width="100" height="20" rx="4" fill="#10B981"/>
  <rect x="251" y="155" width="42" height="20" rx="4" fill="#475569"/>
  <text x="200" y="255" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#64748B">Mechanical RGB Keyboard</text>
</svg>
""")

# 6. Backpack
write_svg("backpack.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#F1F5F9"/>
  <circle cx="200" cy="150" r="110" fill="#E2E8F0"/>
  <path d="M145 90 C145 75 255 75 255 90 L265 210 C265 220 250 225 200 225 C150 225 135 220 135 210 Z" fill="#334155"/>
  <rect x="155" y="145" width="90" height="60" rx="8" fill="#1E293B"/>
  <line x1="165" y1="170" x2="235" y2="170" stroke="#F59E0B" stroke-width="4" stroke-linecap="round"/>
  <path d="M175 75 C175 60 225 60 225 75" fill="none" stroke="#0F172A" stroke-width="6"/>
  <text x="200" y="260" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#64748B">Waterproof 25L Backpack</text>
</svg>
""")

# 7. Bottle
write_svg("bottle.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#F1F5F9"/>
  <circle cx="200" cy="150" r="110" fill="#E2E8F0"/>
  <rect x="180" y="70" width="40" height="25" rx="4" fill="#64748B"/>
  <rect x="165" y="95" width="70" height="130" rx="16" fill="#0EA5E9"/>
  <line x1="180" y1="130" x2="180" y2="190" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.6"/>
  <text x="200" y="260" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#64748B">Stainless Thermal Bottle</text>
</svg>
""")

# 8. Shirt
write_svg("shirt.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#F1F5F9"/>
  <circle cx="200" cy="150" r="110" fill="#E2E8F0"/>
  <path d="M140 90 L180 85 L200 110 L220 85 L260 90 L290 140 L260 155 L245 130 V225 H155 V130 L140 155 L110 140 Z" fill="#2563EB"/>
  <line x1="200" y1="110" x2="200" y2="225" stroke="#1D4ED8" stroke-width="2"/>
  <circle cx="200" cy="135" r="3" fill="#FFFFFF"/>
  <circle cx="200" cy="165" r="3" fill="#FFFFFF"/>
  <circle cx="200" cy="195" r="3" fill="#FFFFFF"/>
  <text x="200" y="260" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#64748B">Classic Oxford Shirt</text>
</svg>
""")

# 9. Lamp
write_svg("lamp.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#F1F5F9"/>
  <circle cx="200" cy="150" r="110" fill="#E2E8F0"/>
  <rect x="150" y="220" width="100" height="12" rx="6" fill="#334155"/>
  <line x1="175" y1="220" x2="175" y2="120" stroke="#475569" stroke-width="8" stroke-linecap="round"/>
  <line x1="175" y1="120" x2="245" y2="110" stroke="#475569" stroke-width="8" stroke-linecap="round"/>
  <rect x="235" y="105" width="40" height="20" rx="6" fill="#F59E0B"/>
  <polygon points="230,125 280,125 305,200 205,200" fill="#FEF3C7" opacity="0.5"/>
  <text x="200" y="260" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#64748B">Smart LED Desk Lamp</text>
</svg>
""")

print("[OK] Generated SVG placeholder images and logo.")
