"""
Production settings.

Inherits from base.py and applies strict security validation at startup.
The application will refuse to start if any required environment variable
is missing or misconfigured.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401, F403
from .base import BASE_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    """Return the value of *name* from the environment or raise ImproperlyConfigured."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(
            f"Required environment variable '{name}' is not set or is empty. "
            "Set it before starting the production server."
        )
    return value


# ---------------------------------------------------------------------------
# Security — all three must be explicitly configured
# ---------------------------------------------------------------------------
SECRET_KEY = _require_env("SECRET_KEY")

_debug_raw = os.environ.get("DEBUG", "False").strip().lower()
if _debug_raw in ("true", "1", "yes"):
    raise ImproperlyConfigured(
        "DEBUG must be 'False' (or unset) in production. "
        f"Got: '{os.environ.get('DEBUG')}'"
    )
DEBUG = False

_allowed_hosts_raw = _require_env("ALLOWED_HOSTS")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_raw.split(",") if h.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must contain at least one hostname in production."
    )
if "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must not contain '*' in production. "
        "Specify explicit hostnames instead."
    )

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Default to SQLite so the project can be deployed quickly; swap for
# PostgreSQL by setting DATABASE_URL (requires dj-database-url).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True").strip().lower() != "false"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ---------------------------------------------------------------------------
# CORS — explicit origins required in production
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False
_cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "").strip()
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(",") if o.strip()]

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
