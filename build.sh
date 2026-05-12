#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files for WhiteNoise
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

if [ "$CREATE_SUPERUSER" ]; then
  python manage.py createsuperuser --no-input || echo "Superuser already exists"