# Cara Fashion

Cara Fashion is a Django-based fashion e-commerce demo. It includes a responsive storefront, a product catalogue, session-backed shopping features, checkout and order recording, customer accounts, product reviews, and a Django admin area for managing store data.

The storefront is built with Django templates, HTML, CSS, and vanilla JavaScript. SQLite is used for local development.

## Features

### Storefront

- **Home page:** Featured products, new arrivals, promotional sections, and newsletter sign-up.
- **Shop:** Browse the catalogue, search by keyword, filter by category, and sort products by price or newest first.
- **Product details:** Product descriptions, image gallery, size selection, quantity controls, and customer ratings and reviews.
- **Wishlist:** Save products for later.
- **Shopping cart:** Add products in a selected size, change quantities, remove items, and view line-item and order totals.
- **Discount code:** Apply `CARA10` at checkout for a 10% discount.
- **Checkout:** Enter delivery and contact details, then choose a payment preference.
- **Customer accounts:** Sign up, log in, and log out.
- **Contact and newsletter forms:** Save customer messages and newsletter subscriptions in the database.
- **Informational pages:** About and blog pages.

### Administration

The Django admin site lets staff manage products, orders and order items, reviews, contact messages, newsletter subscriptions, blog posts, and cart records. Product records include a brand, name, price, category, description, image path, and featured/new-arrival flags.

## Technology

- Python
- Django 5.2.6
- SQLite
- Django templates, HTML, CSS, and vanilla JavaScript

## Requirements

- Python 3.10 or newer
- `pip`

The Python dependencies are listed in [`requirements.txt`](requirements.txt).

## Run locally

### Windows PowerShell

Open PowerShell in the project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

If the virtual environment already exists, skip the first command. Alternatively, on Windows, run `runserver.bat` to start the development server after dependencies have been installed and migrations applied.

### macOS or Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Open these local URLs while the development server is running:

- Storefront: <http://127.0.0.1:8000/>
- Django admin: <http://127.0.0.1:8000/admin/>

The `seed` command adds the demo catalogue and blog posts when their tables are empty. It does not create an administrator account; use `createsuperuser` to make one with your own credentials.

## Configuration and security

The project uses SQLite at `db.sqlite3` by default. That database is created locally by migrations and is intentionally excluded from version control.

For local development, the settings provide a development-only fallback secret key and enable debug mode by default. To supply settings through environment variables in PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-secret"
$env:DJANGO_DEBUG = "true"
```

In a deployment environment, set `DJANGO_SECRET_KEY` to a private, randomly generated value and set `DJANGO_DEBUG` to `false`. Never commit production secrets. Before deployment, also configure `ALLOWED_HOSTS` for the deployment's hostnames, use a production-ready web server and database, and review Django's deployment checklist. `runserver` is for development, not production.

## Tests and useful commands

Run the project test suite:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

On macOS or Linux, use:

```bash
.venv/bin/python manage.py test
```

Other useful Django commands:

```text
python manage.py check             Check project configuration
python manage.py showmigrations    Show migration status
python manage.py makemigrations    Create migrations after model changes
python manage.py migrate           Apply database migrations
python manage.py seed              Add demo products and blog posts
python manage.py createsuperuser   Create an admin login
```

Use the Python executable from the virtual environment when running these commands.

## Main pages

| Page | URL |
| --- | --- |
| Home | `/` |
| Shop | `/shop/` |
| Product details | `/product/<product-id>/` |
| Cart | `/cart/` |
| Checkout | `/checkout/` |
| Payment preference | `/payment/` |
| Wishlist | `/wishlist/` |
| About | `/about/` |
| Blog | `/blog/` |
| Contact | `/contact/` |
| Sign up | `/signup/` |
| Log in | `/login/` |
| Admin | `/admin/` |

## Project structure

```text
cara-fashion/
├── cara/                       Django project settings and URL configuration
├── store/                      Store app: models, views, forms, admin, and tests
│   ├── management/commands/    Custom management commands, including demo seeding
│   └── migrations/             Database schema migrations
├── templates/store/            Django HTML templates for storefront pages
├── static/                     CSS, images, video, and other static assets
├── manage.py                   Django command-line utility
├── requirements.txt            Python dependencies
├── runserver.bat               Windows development-server shortcut
└── README.md                   Project documentation
```

## Important demo limitations

- **Payments are not processed online.** Cash on Delivery, UPI, and card are recorded as order payment preferences only. No payment gateway is connected.
- **Catalogue prices are sample INR values.** They are not verified retail or brand prices. Confirm product authenticity, permissions to use product imagery and brand names, and final prices before using the site commercially.
- **The default database is for local development.** The SQLite database file is not included in the repository; run migrations and the seed command to create a local demo catalogue.
- **Deployment requires additional configuration.** Configure allowed hosts, secrets, HTTPS, database backups, and other production settings before making the application public.
