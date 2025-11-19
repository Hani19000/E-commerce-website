#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input --clear

echo "=== Static files collected ==="
ls -la staticfiles/ | head -20
echo "=== CSS files ==="
find staticfiles/css -type f 2>/dev/null || echo "No CSS files found!"
```

### 3. **Variables d'environnement Railway**

Ajoutez ces variables dans Railway :
```
CLOUDINARY_CLOUD_NAME=da0ye1z2e
CLOUDINARY_API_KEY=798987897232743
CLOUDINARY_API_SECRET=R7g2huNISHZivEdizV
DEBUG=False
```