"""
ASGI config for the project.

Exposes the ASGI callable as a module-level variable named ``application``.
The settings module is selected via the DJANGO_SETTINGS_MODULE environment
variable (defaults to the development settings for safety).

https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_asgi_application()
