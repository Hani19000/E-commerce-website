import os
import sys

# Ajoutez le chemin du projet
sys.path.append('/app/ecom')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')

application = get_wsgi_application()