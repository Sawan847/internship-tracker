"""
Flask Backend API — Internship Application Tracker
Handles all business logic & in-memory storage.
"""

from flask import Flask, jsonify, request
from datetime import datetime
import re

app = Flask(__name__)

# ── In-Memory Storage ────────────────────────────────────────────────────────
applications = []
_id_counter = 1

# ── Helpers ──────────────────────────────────────────────────────────────────
VALID_STATUSES = ["Applied", "Under Review", "Selected", "Rejected"]

STATUS_BADGE = {
    "Applied":      "primary",
    "Under Review": "warning",
    "Selected":     "success",
    "Rejected":     "danger",
}

def validate_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))

def find_application(app_id: int):
    return next((a for a in applications if a["id"] == app_id), None)

def make_error(msg: str, code: int = 400):
    return jsonify({"success": False, "error": msg}), code

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Flask API is running", "total_applications": len(applications)})


@app.route("/applications", methods=["GET"])
def get_all_applications():
    """Return all applications, optionally filtered by status."""
    status_filter = request.args.get("status", "").strip()
    result = applications if not status_filter else [
        a for a in applications if a["status"].lower() == status_filter.lower()
    ]
    enriched = [{**a, "badge": STATUS_BADGE.get(a["status"], "secondary")} for a in result]
    return jsonify({"success": True, "count": len(enriched), "applications": enriched})


@app.route("/application/<int:app_id>", methods=["GET"])
def get_application(app_id):
    """Return a single application by ID."""
    app_obj = find_application(app_id)
    if not app_obj:
        return make_error(f"Application with id={app_id} not found.", 404)
    return jsonify({"success": True, "application": {**app_obj, "badge": STATUS_BADGE.get(app_obj["status"], "secondary")}})


@app.route("/apply", methods=["POST"])
def apply():
    """
    Accept a new internship application.
    Expected JSON body:
        name, email, college, skills, role
    """
    global _id_counter
    data = request.get_json(force=True, silent=True) or {}

    # ── Validation ──────────────────────────────────────────────────────────
    required = ["name", "email", "college", "skills", "role"]
    missing  = [f for f in required if not str(data.get(f, "")).strip()]
    if missing:
        return make_error(f"Missing or empty fields: {', '.join(missing)}")

    if not validate_email(data["email"].strip()):
        return make_error("Invalid email address format.")

    # Prevent duplicate email + role combo
    email = data["email"].strip().lower()
    role  = data["role"].strip()
    duplicate = next((a for a in applications
                      if a["email"].lower() == email and a["role"].lower() == role.lower()), None)
    if duplicate:
        return make_error(f"An application for '{role}' from '{email}' already exists (ID #{duplicate['id']}).")

    # ── Build record ─────────────────────────────────────────────────────────
    new_app = {
        "id":         _id_counter,
        "name":       data["name"].strip().title(),
        "email":      email,
        "college":    data["college"].strip(),
        "skills":     data["skills"].strip(),
        "role":       role,
        "status":     "Applied",          # always starts here
        "applied_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    }
    applications.append(new_app)
    _id_counter += 1

    return jsonify({"success": True, "message": "Application submitted successfully!", "application": new_app}), 201


@app.route("/update-status", methods=["POST"])
def update_status():
    """
    Update the status of an existing application.
    Expected JSON body:  { "id": <int>, "status": <str> }
    Status transitions allowed:
        Applied → Under Review → Selected | Rejected
    """
    data   = request.get_json(force=True, silent=True) or {}
    app_id = data.get("id")
    new_status = str(data.get("status", "")).strip()

    if app_id is None:
        return make_error("'id' field is required.")
    if new_status not in VALID_STATUSES:
        return make_error(f"Invalid status. Choose from: {', '.join(VALID_STATUSES)}")

    app_obj = find_application(int(app_id))
    if not app_obj:
        return make_error(f"Application id={app_id} not found.", 404)

    # ── Transition rules ──────────────────────────────────────────────────────
    current = app_obj["status"]
    allowed = {
        "Applied":      ["Under Review", "Rejected"],
        "Under Review": ["Selected", "Rejected"],
        "Selected":     [],           # terminal
        "Rejected":     [],           # terminal
    }
    if new_status not in allowed.get(current, []):
        if current == new_status:
            return make_error(f"Application is already '{current}'.")
        if not allowed[current]:
            return make_error(f"Status '{current}' is final and cannot be changed.")
        return make_error(
            f"Cannot move from '{current}' to '{new_status}'. "
            f"Allowed next: {allowed[current] or 'none (terminal)'}"
        )

    app_obj["status"] = new_status
    app_obj["updated_at"] = datetime.now().strftime("%d %b %Y, %I:%M %p")

    return jsonify({
        "success": True,
        "message": f"Status updated to '{new_status}'.",
        "application": {**app_obj, "badge": STATUS_BADGE[new_status]},
    })


@app.route("/delete/<int:app_id>", methods=["DELETE"])
def delete_application(app_id):
    """Remove an application from memory."""
    global applications
    app_obj = find_application(app_id)
    if not app_obj:
        return make_error(f"Application id={app_id} not found.", 404)
    applications = [a for a in applications if a["id"] != app_id]
    return jsonify({"success": True, "message": f"Application #{app_id} deleted."})


@app.route("/stats", methods=["GET"])
def stats():
    """Return a quick summary of application counts by status."""
    summary = {s: 0 for s in VALID_STATUSES}
    for a in applications:
        summary[a["status"]] = summary.get(a["status"], 0) + 1
    return jsonify({"success": True, "total": len(applications), "by_status": summary})


if __name__ == "__main__":
    app.run(port=5050, debug=True)
