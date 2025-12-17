"""
Django settings for ecom project.
Production-ready & environment-variable secured version.
"""

from pathlib import Path
import os
from decouple import config
from dotenv import load_dotenv
import dj_database_url
# Load locally stored .env (useful for dev)
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ===============================
# Security
# ===============================
SECRET_KEY = config("SECRET_KEY")
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "e-commerce-website-production-96ec.up.railway.app" , "tiffiny-tussive-kieth.ngrok-free.dev"
]

CSRF_TRUSTED_ORIGINS = [
    "https://e-commerce-website-production-96ec.up.railway.app" , "https://tiffiny-tussive-kieth.ngrok-free.dev"
]

# ===============================
# Application definition
# ===============================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom apps
    'store',
    'cart',
    'payment',

    # External
    'captcha',

    # For static optimization
    'whitenoise.runserver_nostatic',

    # For paypal integration
    'paypal.standard.ipn',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecom.urls'
AUTH_USER_MODEL = "store.CustomUser"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecom.wsgi.application'


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }



# ===============================
# Database (Railway PostgreSQL)
# ===============================
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ===============================
# Password validation
# ===============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===============================
# Internationalization
# ===============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===============================
# Static & Media Files
# ===============================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise: production static optimization
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ===============================
# reCAPTCHA
# ===============================
RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY")

# ===============================
# SendGrid
# ===============================
SENDGRID_API_KEY = config("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = config("SENDGRID_FROM_EMAIL")

# ===============================
# Default primary key
# ===============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#add paypal settings
#set sandbox to true
# PAYPAL_TEST = True
# #paypal business email
# PAYPAL_RECEIVER_EMAIL = config("PAYPAL_RECEIVER_EMAIL")


#stripe settings api
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')