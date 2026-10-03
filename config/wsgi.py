"""
WSGI config for the project.

Exposes the WSGI callable as a module-level variable named ``application``.
The settings module is selected via the DJANGO_SETTINGS_MODULE environment
variable (defaults to the development settings for safety).

https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_wsgi_application()
