"""
URL resolution tests for all named Todo URL patterns.

Covers:
  - Reverse resolution for all 8 named URL patterns
  - URL pattern parameter acceptance (int:pk)
  - Namespace inclusion verification (app_name = 'todos')
  - Forward resolution (resolve) for each URL
"""

import pytest
from django.urls import NoReverseMatch, resolve, reverse

pytestmark = pytest.mark.django_db


class TestTodoUrlReverseResolution:
    """All named URL patterns can be reversed."""

    def test_todo_list_url_resolves(self):
        url = reverse("todos:todo-list")
        assert url == "/todos/"

    def test_todo_create_url_resolves(self):
        url = reverse("todos:todo-create")
        assert url == "/todos/create/"

    def test_todo_detail_url_resolves(self):
        url = reverse("todos:todo-detail", kwargs={"pk": 1})
        assert url == "/todos/1/"

    def test_todo_update_url_resolves(self):
        url = reverse("todos:todo-update", kwargs={"pk": 1})
        assert url == "/todos/1/update/"

    def test_todo_delete_url_resolves(self):
        url = reverse("todos:todo-delete", kwargs={"pk": 1})
        assert url == "/todos/1/delete/"

    def test_todo_toggle_url_resolves(self):
        url = reverse("todos:todo-toggle", kwargs={"pk": 1})
        assert url == "/todos/1/toggle/"


class TestTodoUrlParameters:
    """URL patterns accept integer pk parameters."""

    def test_detail_url_accepts_integer_pk(self):
        url = reverse("todos:todo-detail", kwargs={"pk": 42})
        assert "/42/" in url

    def test_update_url_accepts_integer_pk(self):
        url = reverse("todos:todo-update", kwargs={"pk": 99})
        assert "/99/" in url

    def test_delete_url_accepts_integer_pk(self):
        url = reverse("todos:todo-delete", kwargs={"pk": 7})
        assert "/7/" in url

    def test_toggle_url_accepts_integer_pk(self):
        url = reverse("todos:todo-toggle", kwargs={"pk": 5})
        assert "/5/" in url

    def test_detail_url_rejects_string_pk(self):
        """String pk should raise NoReverseMatch for int: converter."""
        with pytest.raises(NoReverseMatch):
            reverse("todos:todo-detail", kwargs={"pk": "abc"})


class TestTodoUrlForwardResolution:
    """resolve() maps URL paths back to the correct view names."""

    def test_resolve_todo_list(self):
        match = resolve("/todos/")
        assert match.url_name == "todo-list"
        assert match.namespace == "todos"
        assert match.app_name == "todos"

    def test_resolve_todo_create(self):
        match = resolve("/todos/create/")
        assert match.url_name == "todo-create"

    def test_resolve_todo_detail(self):
        match = resolve("/todos/1/")
        assert match.url_name == "todo-detail"
        assert match.kwargs["pk"] == 1

    def test_resolve_todo_update(self):
        match = resolve("/todos/1/update/")
        assert match.url_name == "todo-update"
        assert match.kwargs["pk"] == 1

    def test_resolve_todo_delete(self):
        match = resolve("/todos/1/delete/")
        assert match.url_name == "todo-delete"
        assert match.kwargs["pk"] == 1

    def test_resolve_todo_toggle(self):
        match = resolve("/todos/1/toggle/")
        assert match.url_name == "todo-toggle"
        assert match.kwargs["pk"] == 1


class TestTodoUrlNamespace:
    """Namespace 'todos' is correctly configured."""

    def test_namespace_prefix_required_for_reverse(self):
        """Reversing without namespace prefix should raise NoReverseMatch."""
        with pytest.raises(NoReverseMatch):
            reverse("todo-list")  # missing 'todos:' prefix

    def test_namespace_is_todos(self):
        match = resolve("/todos/")
        assert match.namespace == "todos"

    def test_app_name_is_todos(self):
        match = resolve("/todos/")
        assert match.app_name == "todos"

    def test_all_named_patterns_use_namespace(self):
        """All 6 named patterns are reachable under the 'todos' namespace."""
        named_patterns = [
            ("todos:todo-list", {}),
            ("todos:todo-create", {}),
            ("todos:todo-detail", {"pk": 1}),
            ("todos:todo-update", {"pk": 1}),
            ("todos:todo-delete", {"pk": 1}),
            ("todos:todo-toggle", {"pk": 1}),
        ]
        for name, kwargs in named_patterns:
            url = reverse(name, kwargs=kwargs)
            assert url.startswith("/todos/"), f"{name} did not resolve under /todos/"
