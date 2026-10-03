"""
Test-only URL configuration.

Mirrors config/urls.py but *includes* the todos app URLs so that all
view and URL-resolution tests work without modifying the production
URL conf.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("todos/", include("apps.todos.urls", namespace="todos")),
]
