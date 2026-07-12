# TRANSITOPS - Enterprise Vehicle Fleet Management System

TRANSITOPS is a premium, responsive web application designed for enterprise logistics and fleet operations. It enables logistics managers to monitor vehicle telemetries, dispatch drivers, log maintenance records, track fuel/expenses, analyze fleet utilization, and export operational reports.

---

## 🚀 Key Features

* **Premium UI/UX Design**: Sleek, glassmorphic card design tailored using a custom Tailwind CSS color palette, modern typography (Inter & JetBrains Mono), and animated Material symbols.
* **Light & Dark Theme**: Full support for system preferences and manual theme toggling via a quick header button.
* **Interactive Fleet Drawer**: Clicking any vehicle in the fleet overview triggers an immediate, smooth slide-over drawer displaying live telemetry, driver assignments, route progress, and diagnostic status.
* **Operational Dashboard**: Real-time stats (Active Vehicles, In Maintenance, Active Trips, Utilization Rate) alongside dynamic visual charts (vehicle distribution, driver duties, trip timelines) built with Chart.js.
* **Asset Directory**: Comprehensive management panels to create, read, update, and delete (CRUD) Vehicles, Drivers, Trips, Maintenance tickets, Fuel logs, and Expenses.
* **Export Utilities**: Quick buttons to export tabular logs (Vehicles, Drivers, Trips, Fuel logs) to CSV format.
* **Local SQLite Fallback**: Automatic detection and fallback to a local SQLite database if the main PostgreSQL database settings are offline.

---

## 🛠️ Tech Stack

* **Backend**: Django (Python 3.11+)
* **Frontend**: HTML5, Vanilla CSS, Tailwind CSS, Chart.js
* **Database**: PostgreSQL (Production) / SQLite (Local Dev fallback)

---

## 🔧 Local Quick Start Guide

### 1. Prerequisite Packages
Ensure you have Python installed (Python 3.11+ recommended).

### 2. Run Database Migrations
Initialize the local SQLite database schema by running:
```bash
python manage.py migrate
```

### 3. Seed Realistic Mock Data
Populate the database with test assets (Volvo FH16, Peterbilt 579, Freightliner, Mercedes Sprinter, driver Marcus Johnson, trips, maintenance check logs) and set up the default admin credentials:
```bash
python seed_data.py
```

### 4. Boot Development Server
Run the local server:
```bash
python manage.py runserver
```

### 5. Access and Log In
Open your browser and navigate to `http://127.0.0.1:8000/`.

Log in using the seeded administrator credentials:
* **Username**: `admin`
* **Password**: `admin123`

---

## 📂 Project Architecture

* `transitops/` - Core Django project settings and URLs routing.
* `accounts/` - Custom user authentication models, roles, and login views.
* `dashboard/` - Telemetry views, KPI computations, and dashboard templates.
* `fleet/` - Business logic models, CRUD views, forms, and templates for Vehicles, Drivers, Trips, Maintenance, Fuel logs, and Expenses.
* `reports/` - Data metrics processing, Chart.js visualizations, and CSV exporting tools.
* `templates/` - Global HTML base layouts (`base.html`).
* `static/` - Static CSS and JS assets.
* `seed_data.py` - Seeding script to initialize local databases.
