"""
Smoke tests for the Django settings architecture.

These tests verify that:
  1. The development settings load without errors.
  2. Critical settings have the expected values in development.
  3. The production settings raise ImproperlyConfigured when required
     environment variables are absent.
"""

import importlib
import os

import django
import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


# ---------------------------------------------------------------------------
# Development settings
# ---------------------------------------------------------------------------

class TestDevelopmentSettings:
    """Verify development settings are sane."""

    def test_debug_is_true(self):
        assert settings.DEBUG is True

    def test_databases_engine_is_sqlite(self):
        assert "sqlite3" in settings.DATABASES["default"]["ENGINE"]

    def test_installed_apps_contains_django_core(self):
        core_apps = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
        ]
        for app in core_apps:
            assert app in settings.INSTALLED_APPS, f"{app} missing from INSTALLED_APPS"

    def test_rest_framework_in_installed_apps(self):
        assert "rest_framework" in settings.INSTALLED_APPS

    def test_templates_dirs_contains_templates_folder(self):
        from pathlib import Path
        dirs = settings.TEMPLATES[0]["DIRS"]
        assert any(Path(d).name == "templates" for d in dirs)

    def test_static_url(self):
        assert settings.STATIC_URL == "/static/"

    def test_default_auto_field(self):
        assert settings.DEFAULT_AUTO_FIELD == "django.db.models.BigAutoField"

    def test_use_tz_is_true(self):
        assert settings.USE_TZ is True

    def test_time_zone_is_utc(self):
        assert settings.TIME_ZONE == "UTC"


# ---------------------------------------------------------------------------
# Production settings validation
# ---------------------------------------------------------------------------

class TestProductionSettingsValidation:
    """Verify production settings refuse to load when env vars are missing."""

    def _reload_production_settings(self, env_overrides: dict):
        """
        Temporarily patch os.environ, then import (or reload) the production
        settings module to trigger its startup validation.
        """
        original_env = os.environ.copy()
        try:
            # Clear any existing values that might satisfy the checks
            for key in ("SECRET_KEY", "DEBUG", "ALLOWED_HOSTS"):
                os.environ.pop(key, None)
            os.environ.update(env_overrides)

            import config.settings.production as prod_mod
            importlib.reload(prod_mod)
        finally:
            os.environ.clear()
            os.environ.update(original_env)

    def test_missing_secret_key_raises(self):
        with pytest.raises(ImproperlyConfigured, match="SECRET_KEY"):
            self._reload_production_settings({
                # SECRET_KEY intentionally absent
                "DEBUG": "False",
                "ALLOWED_HOSTS": "example.com",
            })

    def test_debug_true_raises(self):
        with pytest.raises(ImproperlyConfigured, match="DEBUG"):
            self._reload_production_settings({
                "SECRET_KEY": "a-valid-secret-key-for-testing",
                "DEBUG": "True",  # must be rejected
                "ALLOWED_HOSTS": "example.com",
            })

    def test_missing_allowed_hosts_raises(self):
        with pytest.raises(ImproperlyConfigured, match="ALLOWED_HOSTS"):
            self._reload_production_settings({
                "SECRET_KEY": "a-valid-secret-key-for-testing",
                "DEBUG": "False",
                # ALLOWED_HOSTS intentionally absent
            })
