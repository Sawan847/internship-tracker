#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
#  start_flask.sh  — Run the Flask backend API on port 5050
# ──────────────────────────────────────────────────────────────────
cd "$(dirname "$0")/flask_service"
echo "Starting Flask API on http://127.0.0.1:5050 ..."
python3 app.py
