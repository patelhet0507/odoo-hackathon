# TRANSITOPS - Enterprise Vehicle Fleet Management System

TRANSITOPS is a premium, responsive web application designed for enterprise logistics and fleet operations. It enables logistics managers to monitor vehicle telemetries, dispatch drivers, log maintenance records, track fuel/expenses, analyze fleet utilization, and export operational reports.

**Live Demo**: [https://odoo-hackathon-wheat.vercel.app/](https://odoo-hackathon-wheat.vercel.app/)

---

## 🚀 Key Features

* **Premium UI/UX Design**: Sleek, glassmorphic card design tailored using a custom Tailwind CSS color palette, modern typography (Inter & JetBrains Mono), and animated Material symbols.
* **Light & Dark Theme**: Full support for system preferences and manual theme toggling via a quick header button.
* **Interactive Fleet Drawer**: Clicking any vehicle in the fleet overview triggers an immediate, smooth slide-over drawer displaying live telemetry, driver assignments, route progress, and diagnostic status.
* **Operational Dashboard**: Real-time stats (Active Vehicles, In Maintenance, Active Trips, Utilization Rate) alongside dynamic visual charts (vehicle distribution, driver duties, trip timelines) built with Chart.js.
* **Asset Directory**: Comprehensive management panels to create, read, update, and delete (CRUD) Vehicles, Drivers, Trips, Maintenance tickets, Fuel logs, and Expenses.
* **Export Utilities**: Quick buttons to export tabular logs (Vehicles, Drivers, Trips, Fuel logs) to CSV format.
* **Auto DB Fallback**: Automatically uses PostgreSQL when available (via DATABASE_URL env var), falls back to local SQLite for development.

---

## 🛠️ Tech Stack

* **Backend**: Django 6.0 (Python 3.12+)
* **Frontend**: HTML5, Vanilla CSS, Tailwind CSS, Chart.js
* **Database**: PostgreSQL (Supabase, via connection pooler) / SQLite (local dev)
* **Hosting**: Vercel (serverless functions + static files via WhiteNoise)
* **Storage**: S3-compatible (optional, via django-storages)

---

## 🌐 Production Deployment

The app is deployed on **Vercel** with **Supabase PostgreSQL** using the connection pooler (port 6543) for IPv4 compatibility. Set the following environment variables on Vercel:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Supabase pooler URL (e.g., `postgresql://postgres.REF:PASS@aws-0-REGION.pooler.supabase.com:6543/postgres`) |
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_DEBUG` | Set to `False` in production |

Migrations run automatically on each deploy via `manage.py migrate` in the build step.

---

## 🔧 Local Quick Start Guide

### 1. Prerequisites
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Seed Realistic Mock Data
Populate the database with test assets (vehicles, drivers, trips, maintenance logs) and default admin credentials:
```bash
python seed_data.py
```

### 4. Start Development Server
```bash
python manage.py runserver
```

### 5. Login
Open `http://127.0.0.1:8000/` and log in with:
* **Username**: `admin`
* **Password**: `admin123`

---

## 📂 Project Architecture

* `transitops/` - Core Django settings and URL routing.
* `accounts/` - Custom user model (roles: fleet manager, driver, safety officer, financial analyst), auth views.
* `dashboard/` - KPI computations, telemetry dashboard with Chart.js.
* `fleet/` - CRUD for Vehicles, Drivers, Trips, Maintenance, Fuel, Expenses.
* `reports/` - Analytics, CSV export, PDF report generation (xhtml2pdf).
* `templates/` - Global base layout (`base.html`) with light/dark theme.
* `static/` - CSS and JS assets.
* `api/` - Vercel serverless function entry point (`index.py`).
* `seed_data.py` - Script to populate database with sample data.


