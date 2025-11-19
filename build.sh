#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
mkdir -p staticfiles
python manage.py collectstatic --no-input --clear

echo "=== Static files collected ==="
ls -la staticfiles/
echo "=== CSS files ==="
ls -la staticfiles/css/ || echo "No CSS directory found"