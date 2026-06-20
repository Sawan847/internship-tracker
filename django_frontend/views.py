"""
Django Views — Internship Application Tracker
All communication with Flask happens via the requests library.
"""

import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages

FLASK = settings.FLASK_API_URL

def _roles():
    return [
        "Python Developer", "Web Developer", "Frontend Developer",
        "Backend Developer", "Full Stack Developer", "Data Analyst",
        "Machine Learning Engineer", "DevOps Engineer", "UI/UX Designer",
        "Android Developer", "iOS Developer", "Cybersecurity Analyst",
        "Cloud Engineer", "Database Administrator", "Project Manager",
    ]


def _flask_get(path, params=None):
    """GET helper — returns (data_dict | None, error_str | None)."""
    try:
        r = requests.get(f"{FLASK}{path}", params=params, timeout=5)
        return r.json(), None
    except requests.ConnectionError:
        return None, "Cannot reach Flask API. Make sure it is running on port 5050."
    except Exception as e:
        return None, f"Unexpected error: {e}"


def _flask_post(path, payload):
    """POST helper — returns (data_dict | None, error_str | None)."""
    try:
        r = requests.post(f"{FLASK}{path}", json=payload, timeout=5)
        return r.json(), None
    except requests.ConnectionError:
        return None, "Cannot reach Flask API. Make sure it is running on port 5050."
    except Exception as e:
        return None, f"Unexpected error: {e}"


# ── Home ──────────────────────────────────────────────────────────────────────

def home(request):
    """Landing page with quick stats."""
    data, err = _flask_get("/stats")
    stats = None
    if err:
        messages.error(request, err)
    elif data and data.get("success"):
        stats = data

    return render(request, "django_frontend/home.html", {"stats": stats})


# ── Apply ─────────────────────────────────────────────────────────────────────

def apply_view(request):
    """Show & process the application form."""
    if request.method == "POST":
        payload = {
            "name":    request.POST.get("name", "").strip(),
            "email":   request.POST.get("email", "").strip(),
            "college": request.POST.get("college", "").strip(),
            "skills":  request.POST.get("skills", "").strip(),
            "role":    request.POST.get("role", "").strip(),
        }

        data, err = _flask_post("/apply", payload)

        if err:
            messages.error(request, err)
            return render(request, "django_frontend/apply.html", {"form_data": payload, "roles": _roles()})

        if data.get("success"):
            # Store in session so user can see their own apps
            my_apps = request.session.get("my_application_ids", [])
            my_apps.append(data["application"]["id"])
            request.session["my_application_ids"] = my_apps

            messages.success(request, f"🎉 Application submitted! Your ID is #{data['application']['id']}.")
            return redirect("dashboard")
        else:
            messages.error(request, data.get("error", "Submission failed."))
            return render(request, "django_frontend/apply.html", {"form_data": payload, "roles": _roles()})

    return render(request, "django_frontend/apply.html", {"form_data": {}, "roles": _roles()})


# ── Dashboard ─────────────────────────────────────────────────────────────────

def dashboard(request):
    """Show all applications with status badges."""
    status_filter = request.GET.get("status", "").strip()
    params = {"status": status_filter} if status_filter else {}

    data, err = _flask_get("/applications", params=params)

    if err:
        messages.error(request, err)
        apps = []
    elif data and data.get("success"):
        apps = data["applications"]
    else:
        apps = []
        if data:
            messages.error(request, data.get("error", "Failed to load applications."))

    my_ids = set(request.session.get("my_application_ids", []))

    return render(request, "django_frontend/dashboard.html", {
        "applications":    apps,
        "my_ids":          my_ids,
        "status_filter":   status_filter,
        "status_choices":  ["Applied", "Under Review", "Selected", "Rejected"],
    })


# ── Detail ────────────────────────────────────────────────────────────────────

def detail_view(request, app_id):
    """View a single application + allow status update."""
    data, err = _flask_get(f"/application/{app_id}")

    if err:
        messages.error(request, err)
        return redirect("dashboard")

    if not data.get("success"):
        messages.error(request, data.get("error", "Application not found."))
        return redirect("dashboard")

    application = data["application"]

    # Status transition map (mirrors Flask)
    transitions = {
        "Applied":      ["Under Review", "Rejected"],
        "Under Review": ["Selected", "Rejected"],
        "Selected":     [],
        "Rejected":     [],
    }
    allowed_next = transitions.get(application["status"], [])

    return render(request, "django_frontend/detail.html", {
        "application": application,
        "allowed_next": allowed_next,
    })


# ── Update Status ─────────────────────────────────────────────────────────────

def update_status(request):
    """POST-only: update status via Flask API."""
    if request.method != "POST":
        return redirect("dashboard")

    app_id     = request.POST.get("app_id")
    new_status = request.POST.get("status")

    data, err = _flask_post("/update-status", {"id": int(app_id), "status": new_status})

    if err:
        messages.error(request, err)
    elif data.get("success"):
        messages.success(request, f"✅ Status updated to '{new_status}' for application #{app_id}.")
    else:
        messages.error(request, data.get("error", "Status update failed."))

    return redirect("detail", app_id=app_id)


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_application(request, app_id):
    """DELETE via Flask API."""
    if request.method == "POST":
        try:
            r = requests.delete(f"{FLASK}/delete/{app_id}", timeout=5)
            data = r.json()
            if data.get("success"):
                # Remove from session too
                my_apps = request.session.get("my_application_ids", [])
                if app_id in my_apps:
                    my_apps.remove(app_id)
                    request.session["my_application_ids"] = my_apps
                messages.success(request, f"Application #{app_id} has been deleted.")
            else:
                messages.error(request, data.get("error", "Delete failed."))
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return redirect("dashboard")
