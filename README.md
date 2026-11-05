# 🥛 Arokya Milk Store - Full-Stack Dairy E-Commerce Platform

A production-ready, responsive dairy e-commerce web application engineered with **Python 3.11+ / Django**, styled with **Tailwind CSS**, and backed by **SQLite** (seamlessly upgradeable to PostgreSQL). 

Built specifically for local farm-to-table dairy distribution under the **Arokya Milk Store** brand, featuring morning & evening delivery scheduling, dynamic UPI payment QR code generation via Python's `qrcode` engine, live order status progression, and an Owner Control Center (`/owner/dashboard`).

---

## 🌟 Key Architectural Features

### 1. Role-Based Access Control (RBAC)
- **Customer:**
  - Registration and Authentication supporting Username, Phone Number, or Email.
  - Profile management for saving default street address, pincode, and WhatsApp/SMS contact numbers.
  - Live order tracking, order history, and **Customer Order Cancellation** with automatic inventory restock.
- **Store Owner / Admin:**
  - Dedicated Store Management Portal (`/owner/dashboard`).
  - View real-time incoming orders, gross revenue, and pending actions.
  - One-click order actions: **"Accept Order"**, **"Reject Order"**, **"Dispatch (Out for Delivery)"**, and **"Mark Delivered"**.
  - UPI Payment Verification: Inspect customer submitted 12-digit UTR/Txn numbers and mark payment status as **Verified / Paid**.
  - Product Catalog Management: Add new dairy products with image upload, set prices, packaging units, and toggle inventory stock on/off in real-time.

### 2. Dairy Catalog & Cart Engine
- **Categorized Sections:**
  - **Fresh Milk:** 1 Litre Cow Milk, 500ml Toned Milk, 1L Buffalo Rich Milk, Homogenized pouches.
  - **Curd & Dahi:** Traditional set dahi (500g, 200g cups) and Triple-strained Greek Yogurt.
  - **Paneer & Butter:** Fresh Malai Paneer (200g, 500g) and churned white makhan.
  - **Desi Cow Ghee:** Pure A2 Bilona Vedic Cow Ghee and Danedar jars.
  - **Artisan Ice Creams:** Alphonso Mango 500ml Tubs, Belgian Dark Chocolate Waffle Cones, Royal Kesar Pista Cups.
  - **Beverages:** Spiced Masala Chaas / Buttermilk and Chilled Badam Milk.
- **Session-Based Cart:**
  - Real-time cart calculations with Vanilla JavaScript (`static/js/cart.js`).
  - Dynamic quantity steppers with instantaneous subtotal calculation without reloading.
  - Free delivery incentive: Orders above ₹199 qualify for Free Chilled Delivery (otherwise ₹5 delivery fee, customizable anytime in Owner Settings).

### 3. Delivery Scheduling & Dynamic UPI Engine
- **Delivery Windows:**
  - **Morning Slot (6:00 AM - 9:00 AM):** For morning tea, coffee, breakfast curd.
  - **Evening Slot (5:00 PM - 8:00 PM):** For dinner recipes, fresh milk, and evening desserts.
- **Payment Modes:**
  1. **Cash on Delivery (COD):** Pay on doorstep delivery.
  2. **Dynamic UPI QR Code Generation:**
     - Generates standard UPI Deep Link specification:
       ```
       upi://pay?pa=arokyamilk@upi&pn=Arokya+Milk+Store&am=225.00&tn=Order_AMS-A1B2C3D4&cu=INR
       ```
     - Renders a scannable high-resolution QR code image generated via Python's `qrcode` and `Pillow` libraries.
     - Direct mobile deep link button (`Pay via UPI App`) to launch GPay, PhonePe, Paytm, or BHIM.
     - Customer UTR / Reference ID submission form for transparent payment auditing.

---

## 🏗️ Project Architecture

```
e commerce/
├── manage.py
├── seed_data.py               # One-click demo seeder (products, owner, customer, orders)
├── requirements.txt           # Python package dependencies
├── README.md                  # Documentation and quickstart guide
├── db.sqlite3                 # Local SQLite database
│
├── freshdairy/                # Core Project Configuration
│   ├── settings.py            # App registry, media/static configuration, UPI parameters
│   ├── urls.py                # Global routing & media serving
│   ├── wsgi.py
│   └── asgi.py
│
├── users/                     # RBAC & Authentication App
│   ├── models.py              # CustomUser with CUSTOMER / OWNER roles and delivery info
│   ├── decorators.py          # @owner_required, @customer_required guards
│   ├── forms.py               # Registration, Login, and Profile forms
│   ├── views.py               # Register, multi-identifier login, logout, profile
│   ├── urls.py
│   └── admin.py
│
├── products/                  # Dairy Inventory & Catalog App
│   ├── models.py              # Product model with category choices, unit, price, image, stock
│   ├── forms.py               # ProductForm for owner additions and edits
│   ├── views.py               # Catalog listing, category filters, product detail, owner inventory
│   ├── urls.py
│   └── admin.py
│
├── orders/                    # Cart, Checkout, QR, and Order Management App
│   ├── models.py              # Order & OrderItem models with status transitions
│   ├── cart.py                # Session cart manager with delivery calculation
│   ├── context_processors.py  # Global cart badge counter
│   ├── utils.py               # Dynamic UPI payload & QR generator (qrcode + Pillow)
│   ├── forms.py               # CheckoutForm & UpiReferenceForm
│   ├── views.py               # Cart operations, checkout, UPI payment, owner dashboard
│   ├── urls.py
│   └── admin.py
│
├── templates/                 # Modern Tailwind CSS Templates
│   ├── base.html              # Layout, navbar with live badge, footer, toast container
│   ├── users/
│   │   ├── login.html         # Login with quick credential autofill
│   │   ├── register.html      # Customer signup
│   │   └── profile.html       # Saved delivery destination
│   ├── products/
│   │   ├── catalog.html       # Hero, category pills, product grid, search & sort
│   │   ├── product_detail.html# Nutrition info, farm purity checklist, quantity stepper
│   │   ├── owner_product_form.html # Add/edit product + Complete Product Deletion action
│   │   ├── owner_product_list.html # Inventory table with instant stock toggles & delete actions
│   │   └── owner_product_confirm_delete.html # Confirmation dialog for permanent product removal
│   └── orders/
│       ├── cart.html          # Shopping basket, free shipping bar, item subtotals
│       ├── checkout.html      # Address, slot selector (Morning/Evening), selectable COD & UPI cards
│       ├── payment_upi.html   # High-res dynamic QR code, VPA copier, UTR submission, or Switch to COD
│       ├── order_success.html # Order confirmation screen
│       ├── order_history.html # Customer order listing with status badges
│       ├── order_detail.html  # Live visual timeline tracker (Pending -> Delivered)
│       ├── owner_dashboard.html # Dispatch center, revenue KPIs, quick price/stock editor & 1-click delete
│       └── owner_upi_settings.html # Store Owner UPI Settings (VPA change, QR mode & custom QR upload)
│
└── static/
    └── js/
        └── cart.js            # Vanilla JS for async AJAX cart updates & toasts
```

---

## 🚀 Quick Setup Instructions

### Step 1: Clone or Navigate to Project Directory
```powershell
cd "c:\Users\Admin\OneDrive\Documents\e commerce"
```

### Step 2: Set Up Virtual Environment (Recommended)
```powershell
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```powershell
python manage.py migrate
```

### Step 5: Seed Demo Accounts & Dairy Catalog
Run the bundled database seeder to instantly create 17 dairy items, demo users, and sample orders:
```powershell
python seed_data.py
```

### Step 6: Start Servers (Dual Server or Unified)

#### Option A: Dedicated Frontend & Backend Servers (Dual-Terminal)
- **Terminal 1 — Backend Server (Port 8000):**
  ```powershell
  python start_backend.py
  ```
  *(Or double-click `start_backend.bat`)* — Runs Django ORM, Admin (`/admin`), and UPI Engine on `http://localhost:8000`.

- **Terminal 2 — Frontend Server (Port 3000):**
  ```powershell
  python start_frontend.py
  ```
  *(Or double-click `start_frontend.bat`)* — Runs Dedicated Frontend on `http://localhost:3000` connecting to Backend on `8000`.

#### Option B: 1-Click Dual Server Launcher
```powershell
python start_servers.py
```
*(Or double-click `start.bat`)* — Boots both Frontend and Backend concurrently!

#### Option C: Unified Single Server
```powershell
python manage.py runserver 0.0.0.0:8000
```
*(Or double-click `run_server.bat`)*

---

## 🔑 Demo Login Credentials & Dedicated Sections

The application features dedicated login and registration portals with role-level security:

- **Customer Login Section:** [http://127.0.0.1:8000/users/login/customer/](http://127.0.0.1:8000/users/login/customer/)
- **Customer Sign Up:** [http://127.0.0.1:8000/users/register/](http://127.0.0.1:8000/users/register/)
- **Store Owner Login Section:** [http://127.0.0.1:8000/users/login/owner/](http://127.0.0.1:8000/users/login/owner/)
- **New Store Owner Registration:** [http://127.0.0.1:8000/users/register/owner/](http://127.0.0.1:8000/users/register/owner/)

| Role | Username | Password | Purpose & Capabilities |
| :--- | :--- | :--- | :--- |
| **Store Owner** | `owner` | `owner123` | Access `/owner/dashboard`. **One-click Accept Order**, live dispatch tracking, instant **Quick Price Editor**, **Add New Products with image file upload**, **Completely Delete Old Products**, and configure **UPI & QR Settings** (`/shop/owner/upi-settings/`) anytime. |
| **Customer** | `customer` | `customer123` | Browse dairy items, add to cart, select morning/evening delivery slot, pay via **Cash on Delivery (COD)** or scan dynamic UPI QR code (with option to switch to COD anytime), and track live status. |

*(The Sign In page also provides single-click demo credential pills to autofill these credentials for immediate testing).*

---

## 🧪 Running the Automated Test Suite

A complete test suite covering RBAC security, Cart calculation, stock decrements, Cash on Delivery transitions, permanent product deletion, and UPI QR code generation is provided:

```powershell
python manage.py test
```
All 18 tests execute and pass verifying complete system stability.

