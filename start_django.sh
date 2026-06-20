#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
#  start_django.sh  — Run the Django frontend on port 8000
# ──────────────────────────────────────────────────────────────────
cd "$(dirname "$0")"
echo "Starting Django frontend on http://127.0.0.1:8000 ..."
python3 manage.py runserver 8000
