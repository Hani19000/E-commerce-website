#!/usr/bin/env bash
set -o errexit

echo "=== Installation des dépendances ==="
pip install -r requirements.txt

echo "=== Vérification de la structure ==="
pwd
ls -la
echo "=== Contenu du dossier static ==="
ls -la static/ 2>/dev/null || echo "Dossier static introuvable"

echo "=== Création du dossier staticfiles ==="
mkdir -p staticfiles

echo "=== Collecte des fichiers statiques ==="
python manage.py collectstatic --no-input --clear

echo "=== Résultat de la collecte ==="
ls -la staticfiles/ | head -20 || echo "Staticfiles vide"

echo "=== CSS files ==="
find staticfiles/css -type f 2>/dev/null | head -10 || echo "No CSS files"

echo "=== Total des fichiers statiques ==="
find staticfiles -type f | wc -l