"""
Root URL configuration for the project.

URL patterns
------------
  admin/   — Django admin site
  todos/   — Todo API endpoints (provided by apps.todos.urls — created by TASK-01)
  api/     — API root (reserved for future versioned routing)
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("todos/", include("apps.todos.urls", namespace="todos")),
]
