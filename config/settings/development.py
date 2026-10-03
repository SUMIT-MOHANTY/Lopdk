"""
Development settings.

Inherits from base.py and overrides values suitable for local development:
  - DEBUG = True
  - SQLite database
  - All hosts allowed
  - Browsable API renderer enabled
"""

from .base import *  # noqa: F401, F403
from .base import BASE_DIR, REST_FRAMEWORK

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Use a dev secret key when none is provided via .env so that the dev server
# starts without any extra setup.  Never use this value in production.
if not SECRET_KEY:  # noqa: F405
    SECRET_KEY = "django-insecure-dev-only-secret-key-change-me"  # noqa: S105

# ---------------------------------------------------------------------------
# Database — SQLite (zero-config for local development)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# CORS — permissive for local front-end development
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Django REST Framework — add browsable API in development
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# ---------------------------------------------------------------------------
# Email — console backend so no SMTP server is required
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
