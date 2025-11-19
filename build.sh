#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create staticfiles directory
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --no-input --clear

# List files to verify
echo "=== Static files collected ==="
ls -la staticfiles/
echo "=== CSS files ==="
ls -la staticfiles/css/ || echo "No CSS directory found"