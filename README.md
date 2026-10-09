# Cara Fashion — Modern E-Commerce Platform

A premium modern fashion e-commerce web application built with **Django**, **SQLite**, and modern Vanilla HTML5/CSS3/JavaScript.

---

## 🌟 Key Features

- **Luxury Modern UI**: Curated typography (Plus Jakarta Sans & Outfit), responsive design, subtle micro-interactions, and glassmorphic headers.
- **Dynamic Catalogue & Search**: Live keyword search, category filter pills (`Shirts`, `Jeans`, `Jackets`, `T-Shirts`), and sorting (`Price: Low to High`, `Price: High to Low`, `Newest First`).
- **INR Product Pricing**: Distinct suggested Indian retail prices for everyday and designer products, formatted for readability.
- **Interactive Product Details**: Thumbnail image gallery with instant image swap, interactive size selection pills (`S`, `M`, `L`, `XL`, `XXL`), and quantity stepper.
- **Cart & Checkout**:
  - Live item quantity updates and removals.
  - Promo code discounts (use code **`CARA10`** for 10% off).
  - Separate checkout and payment-method selection pages (Cash on Delivery, UPI, or card preference).
  - Orders and selected payment method are recorded in Django Admin. Online payments are not processed.
- **Contact & Concierge**: Interactive inquiry form saving messages directly to backend database, with integrated showroom location map.
- **Newsletter**: Instant subscription with duplicate prevention.
- **Admin Dashboard**: Full product, category, and order management via Django Admin.

---

## 🚀 How to Run Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations & Seed Data**:
   ```bash
   python manage.py migrate
   python manage.py seed
   python manage.py createsuperuser
   ```

3. **Start Development Server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

4. **Access the Application**:
   - **Storefront**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Admin Portal**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
   - **Discount Voucher**: `CARA10` (10% off)

For production, set a unique `DJANGO_SECRET_KEY` and set `DJANGO_DEBUG=false` in the environment. The built-in key is only for local development.

---

## 📁 Clean Project Structure

```
├── cara/                 # Django project settings & URL routing
├── store/                # Store application (models, views, admin, commands)
├── templates/store/      # Clean HTML5 templates (base, home, shop, product, cart, etc.)
├── static/               # Assets (style.css, product images, banners, logos)
├── db.sqlite3            # Local SQLite database (created by migrations; not tracked)
├── manage.py             # Django CLI management script
├── requirements.txt      # Project requirements (Django)
└── README.md             # Project documentation
```

> **Note on Folder Name**: The website brand name is **Cara Fashion** (or **Cara**). If you wish to rename the root folder from `website Template Design` to `Cara` or `cara-fashion`, close this folder in your IDE/editor, rename the folder in File Explorer, and re-open it.

> **Pricing note**: Catalog prices are suggested demo INR amounts, not verified official brand prices. Confirm product authenticity and your final selling prices before accepting live orders.
