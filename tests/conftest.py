"""
Shared pytest fixtures for the Todo application test suite.

Provides:
  - django_db marker auto-use for DB tests
  - client fixture (Django TestClient)
  - todo_factory callable fixture
  - todo_instance single Todo record
  - multiple_todos 10 Todo records for pagination tests
"""

import django
import pytest
from django.test import Client

# ---------------------------------------------------------------------------
# Settings patches applied before Django fully initialises
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """
    Ensure that:
      1. apps.todos is in INSTALLED_APPS (it is commented-out in base.py).
      2. The todos URL patterns are wired into ROOT_URLCONF.
    Both patches are applied once, before any test collection.
    """
    import django.conf as django_conf

    # We must call setup only if Django hasn't been configured yet.
    # pytest-django handles setup, but we hook in *after* settings are loaded.
    from django.conf import settings

    # Patch INSTALLED_APPS
    if "apps.todos" not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS) + ["apps.todos"]

    # Patch ROOT_URLCONF to use a test URL conf that includes todos URLs.
    # We override it to point at our test url module defined below.
    settings.ROOT_URLCONF = "tests.urls"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Return a Django test client instance."""
    return Client()


@pytest.fixture
def todo_factory(db):
    """
    Callable factory fixture.  Usage::

        def test_something(todo_factory):
            todo = todo_factory(title="My task")
    """
    from apps.todos.models import Todo

    def _factory(title="Test Todo", is_completed=False):
        return Todo.objects.create(title=title, is_completed=is_completed)

    return _factory


@pytest.fixture
def todo_instance(todo_factory):
    """A single persisted Todo instance."""
    return todo_factory(title="Sample Todo", is_completed=False)


@pytest.fixture
def multiple_todos(todo_factory):
    """Ten persisted Todo instances for pagination / list tests."""
    return [todo_factory(title=f"Todo Item {i}") for i in range(1, 11)]
