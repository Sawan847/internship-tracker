<<<<<<< HEAD
# 🧾 Internship Application Tracker

> **Django Frontend + Flask REST API + In-Memory Storage (No Database)**

A full-stack internship application tracking system demonstrating a **two-tier architecture**:
- **Django** handles the UI, forms, sessions and talks to the backend via HTTP
- **Flask** handles all business logic, validation and stores data in Python lists

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                     USER BROWSER                         │
└──────────────────────────┬───────────────────────────────┘
                           │ HTTP  (port 8000)
┌──────────────────────────▼───────────────────────────────┐
│              DJANGO  (Frontend Layer)                     │
│  • Renders HTML templates (Bootstrap 5)                  │
│  • Handles forms, sessions, messages                     │
│  • Calls Flask via requests library                      │
└──────────────────────────┬───────────────────────────────┘
                           │ REST API  (port 5050)
┌──────────────────────────▼───────────────────────────────┐
│              FLASK  (Backend API Layer)                   │
│  • In-memory Python list (no DB)                         │
│  • Validates input, generates IDs                        │
│  • Enforces status transitions                           │
│  • Returns JSON responses                                │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
InternshipTracker/
│
├── config/                     # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   └── urls.py
│
├── django_frontend/            # Django app (UI layer)
│   ├── __init__.py
│   ├── apps.py
│   ├── views.py                # Page views + Flask API calls
│   ├── urls.py                 # URL routes
│   └── templates/
│       └── django_frontend/
│           ├── base.html       # Layout + navbar + styles
│           ├── home.html       # Landing page with live stats
│           ├── apply.html      # Application form
│           ├── dashboard.html  # All applications list
│           └── detail.html     # Single application + status update
│
├── flask_service/              # Flask app (backend API)
│   └── app.py                  # All routes + business logic
│
├── manage.py                   # Django CLI
├── requirements.txt
├── start_flask.sh              # Helper: run Flask
├── start_django.sh             # Helper: run Django
└── README.md
```

---

## 🚀 Quick Start (Step-by-Step)

### 1. Clone / Navigate to Project

```bash
cd InternshipTracker
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Flask API (Terminal 1)

```bash
bash start_flask.sh
# OR manually:
cd flask_service && python3 app.py
```

Flask starts at: **http://127.0.0.1:5050**

### 5. Start Django (Terminal 2)

```bash
bash start_django.sh
# OR manually:
python3 manage.py runserver 8000
```

Django starts at: **http://127.0.0.1:8000**

### 6. Open in Browser

```
http://127.0.0.1:8000
```

> ⚠️ **Both servers must be running simultaneously.** Flask MUST start before Django.

---

## 🔌 Flask REST API Reference

Base URL: `http://127.0.0.1:5050`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/applications` | Get all applications |
| `GET` | `/applications?status=Applied` | Filter by status |
| `POST` | `/apply` | Submit new application |
| `GET` | `/application/<id>` | Get single application |
| `POST` | `/update-status` | Update application status |
| `DELETE` | `/delete/<id>` | Delete an application |
| `GET` | `/stats` | Summary counts by status |

### POST /apply — Request Body

```json
{
  "name":    "Sawan Kumar",
  "email":   "sawan@college.edu",
  "college": "Delhi University",
  "skills":  "Python, Django, REST APIs",
  "role":    "Python Developer"
}
```

### POST /update-status — Request Body

```json
{
  "id":     1,
  "status": "Under Review"
}
```

### Example API Calls with curl

```bash
# Submit application
curl -X POST http://localhost:5050/apply \
  -H "Content-Type: application/json" \
  -d '{"name":"Aryan","email":"aryan@mit.edu","college":"MIT","skills":"Python","role":"Python Developer"}'

# Get all applications
curl http://localhost:5050/applications

# Update status
curl -X POST http://localhost:5050/update-status \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "status": "Under Review"}'

# Get stats
curl http://localhost:5050/stats
```

---

## 🔄 Status Transitions (Business Rules)

Flask enforces strict one-way status transitions:

```
Applied  ──►  Under Review  ──►  Selected  (terminal)
   │                        └──►  Rejected  (terminal)
   └─────────────────────────►  Rejected
```

- **Applied** → can move to `Under Review` or `Rejected`
- **Under Review** → can move to `Selected` or `Rejected`
- **Selected** → final, no further changes
- **Rejected** → final, no further changes

---

## 🎨 Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Landing page with live stats |
| Apply | `/apply/` | Internship application form |
| Dashboard | `/dashboard/` | All applications with filters |
| Detail | `/application/<id>/` | View + manage single application |

---

## 🧠 Key Concepts for Viva

**Q: Why Django + Flask separately?**
> Demonstrates separation of concerns: Django excels at UI/templating/sessions;
> Flask is lightweight and ideal for pure REST API logic.

**Q: How do they communicate?**
> Django uses Python's `requests` library to make HTTP calls to Flask endpoints.
> Flask returns JSON; Django parses it and renders HTML.

**Q: Why no database?**
> Applications are stored in a Python list in Flask's memory.
> The list lives as long as the Flask process runs — perfectly valid for demos.

**Q: How does session tracking work?**
> Django stores the list of the user's application IDs in a signed cookie session.
> No server-side session storage needed.

**Q: What happens if Flask restarts?**
> All in-memory data is lost (by design — no DB). This is expected behavior.

---

## ✅ Features Checklist

- [x] Apply for internship form (Name, Email, College, Skills, Role)
- [x] Flask validates all fields + email format
- [x] Duplicate application prevention (same email + role)
- [x] In-memory storage with auto-incrementing IDs
- [x] Status flow: Applied → Under Review → Selected/Rejected
- [x] Dashboard with color-coded status badges
- [x] Filter dashboard by status
- [x] Session-based "Mine" badge for user's own applications
- [x] Delete application
- [x] Stats API endpoint
- [x] Responsive Bootstrap 5 dark UI
- [x] No database, no AI/ML

---

*Built with Python 3 · Django 5 · Flask 3 · Bootstrap 5*
=======
# internship-tracker
>>>>>>> 317c243b8d276c3bd1a66b067fd7924f245feba1
