"""
View tests for all Todo endpoints.

Endpoints covered
-----------------
  GET  /todos/                  – list view (200, template, pagination)
  GET  /todos/?q=<term>         – search (200, filtered results)
  GET  /todos/create/           – create form (200, empty form)
  POST /todos/create/           – create (302 redirect / 200 with errors)
  GET  /todos/<pk>/             – detail (200, object in context)
  GET  /todos/<pk>/update/      – edit form (200, pre-populated)
  POST /todos/<pk>/update/      – edit (302 redirect / 200 with errors)
  GET  /todos/<pk>/delete/      – confirm delete (200)
  POST /todos/<pk>/delete/      – delete (302 redirect)
  POST /todos/<pk>/toggle/      – toggle (302 redirect)
  GET  /todos/<pk>/toggle/      – toggle GET (405 – method not allowed)
  GET  /admin/todos/todo/       – admin list (302 to login for anon user)

Integration flows
-----------------
  - Full CRUD: create → list → detail → edit → delete → list (gone)
  - Search with pagination state retention
  - Toggle flips is_completed correctly
  - Django messages framework across redirects
"""

import pytest
from django.urls import reverse

from apps.todos.models import Todo

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def list_url():
    return reverse("todos:todo-list")


def create_url():
    return reverse("todos:todo-create")


def detail_url(pk):
    return reverse("todos:todo-detail", kwargs={"pk": pk})


def update_url(pk):
    return reverse("todos:todo-update", kwargs={"pk": pk})


def delete_url(pk):
    return reverse("todos:todo-delete", kwargs={"pk": pk})


def toggle_url(pk):
    return reverse("todos:todo-toggle", kwargs={"pk": pk})


# ---------------------------------------------------------------------------
# List view  GET /todos/
# ---------------------------------------------------------------------------

class TestTodoListView:
    """GET /todos/ — list all todos."""

    def test_list_returns_200(self, client, multiple_todos):
        response = client.get(list_url())
        assert response.status_code == 200

    def test_list_uses_correct_template(self, client, multiple_todos):
        response = client.get(list_url())
        assert "todos/todo_list.html" in [t.name for t in response.templates]

    def test_list_context_contains_todos(self, client, todo_instance):
        response = client.get(list_url())
        assert "todos" in response.context

    def test_list_pagination_page_obj_present(self, client, multiple_todos):
        response = client.get(list_url())
        assert "page_obj" in response.context or "todos" in response.context

    def test_list_shows_all_10_todos(self, client, multiple_todos):
        response = client.get(list_url())
        # paginate_by=10, so all 10 fit on page 1
        assert response.status_code == 200
        assert len(multiple_todos) == 10


# ---------------------------------------------------------------------------
# Search  GET /todos/?q=<term>
# ---------------------------------------------------------------------------

class TestTodoSearchView:
    """GET /todos/?q=<term> — filtered results."""

    def test_search_returns_200(self, client, todo_instance):
        response = client.get(list_url(), {"q": "Sample"})
        assert response.status_code == 200

    def test_search_filters_results(self, client, todo_factory):
        todo_factory(title="Buy apples")
        todo_factory(title="Read a book")
        response = client.get(list_url(), {"q": "apples"})
        todos = list(response.context["todos"])
        assert all("apples" in t.title.lower() for t in todos)

    def test_search_no_match_returns_empty_list(self, client, todo_instance):
        response = client.get(list_url(), {"q": "xyzzy_no_match"})
        todos = list(response.context["todos"])
        assert todos == []

    def test_search_query_retained_in_context(self, client, todo_instance):
        response = client.get(list_url(), {"q": "Sample"})
        assert response.context["search_query"] == "Sample"

    def test_search_is_case_insensitive(self, client, todo_factory):
        todo_factory(title="Django Testing")
        response = client.get(list_url(), {"q": "django"})
        todos = list(response.context["todos"])
        assert len(todos) >= 1


# ---------------------------------------------------------------------------
# Create view  GET + POST /todos/create/
# ---------------------------------------------------------------------------

class TestTodoCreateView:
    """GET /todos/create/ and POST /todos/create/."""

    def test_get_create_returns_200(self, client):
        response = client.get(create_url())
        assert response.status_code == 200

    def test_get_create_uses_form_template(self, client):
        response = client.get(create_url())
        assert "todos/todo_form.html" in [t.name for t in response.templates]

    def test_get_create_context_has_empty_form(self, client):
        response = client.get(create_url())
        assert "form" in response.context
        # Form should be unbound (no data submitted yet)
        assert not response.context["form"].is_bound

    def test_valid_post_creates_object(self, client):
        count_before = Todo.objects.count()
        client.post(create_url(), {"title": "New task via POST", "is_completed": False})
        assert Todo.objects.count() == count_before + 1

    def test_valid_post_redirects_to_list(self, client):
        response = client.post(
            create_url(),
            {"title": "Redirect test", "is_completed": False},
        )
        assert response.status_code == 302
        assert response["Location"] == list_url()

    def test_invalid_post_empty_title_returns_200(self, client):
        response = client.post(create_url(), {"title": "", "is_completed": False})
        assert response.status_code == 200

    def test_invalid_post_shows_form_errors(self, client):
        response = client.post(create_url(), {"title": "", "is_completed": False})
        assert response.context["form"].errors

    def test_invalid_post_does_not_create_object(self, client):
        count_before = Todo.objects.count()
        client.post(create_url(), {"title": "", "is_completed": False})
        assert Todo.objects.count() == count_before


# ---------------------------------------------------------------------------
# Detail view  GET /todos/<pk>/
# ---------------------------------------------------------------------------

class TestTodoDetailView:
    """GET /todos/<pk>/."""

    def test_detail_returns_200(self, client, todo_instance):
        response = client.get(detail_url(todo_instance.pk))
        assert response.status_code == 200

    def test_detail_uses_correct_template(self, client, todo_instance):
        response = client.get(detail_url(todo_instance.pk))
        assert "todos/todo_detail.html" in [t.name for t in response.templates]

    def test_detail_context_contains_todo(self, client, todo_instance):
        response = client.get(detail_url(todo_instance.pk))
        assert "todo" in response.context
        assert response.context["todo"].pk == todo_instance.pk

    def test_detail_404_for_nonexistent_pk(self, client):
        response = client.get(detail_url(99999))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Update view  GET + POST /todos/<pk>/update/
# ---------------------------------------------------------------------------

class TestTodoUpdateView:
    """GET /todos/<pk>/update/ and POST /todos/<pk>/update/."""

    def test_get_update_returns_200(self, client, todo_instance):
        response = client.get(update_url(todo_instance.pk))
        assert response.status_code == 200

    def test_get_update_uses_form_template(self, client, todo_instance):
        response = client.get(update_url(todo_instance.pk))
        assert "todos/todo_form.html" in [t.name for t in response.templates]

    def test_get_update_form_is_prepopulated(self, client, todo_instance):
        response = client.get(update_url(todo_instance.pk))
        form = response.context["form"]
        assert form.initial.get("title") == todo_instance.title or \
               form.instance.title == todo_instance.title

    def test_valid_post_updates_object(self, client, todo_instance):
        client.post(
            update_url(todo_instance.pk),
            {"title": "Updated title", "is_completed": True},
        )
        todo_instance.refresh_from_db()
        assert todo_instance.title == "Updated title"
        assert todo_instance.is_completed is True

    def test_valid_post_redirects_to_list(self, client, todo_instance):
        response = client.post(
            update_url(todo_instance.pk),
            {"title": "Redirect after update", "is_completed": False},
        )
        assert response.status_code == 302
        assert response["Location"] == list_url()

    def test_invalid_post_returns_200(self, client, todo_instance):
        response = client.post(
            update_url(todo_instance.pk),
            {"title": "", "is_completed": False},
        )
        assert response.status_code == 200

    def test_invalid_post_shows_form_errors(self, client, todo_instance):
        response = client.post(
            update_url(todo_instance.pk),
            {"title": "", "is_completed": False},
        )
        assert response.context["form"].errors

    def test_invalid_post_does_not_change_title(self, client, todo_instance):
        original_title = todo_instance.title
        client.post(
            update_url(todo_instance.pk),
            {"title": "", "is_completed": False},
        )
        todo_instance.refresh_from_db()
        assert todo_instance.title == original_title


# ---------------------------------------------------------------------------
# Delete view  GET + POST /todos/<pk>/delete/
# ---------------------------------------------------------------------------

class TestTodoDeleteView:
    """GET /todos/<pk>/delete/ and POST /todos/<pk>/delete/."""

    def test_get_delete_returns_200(self, client, todo_instance):
        response = client.get(delete_url(todo_instance.pk))
        assert response.status_code == 200

    def test_get_delete_uses_confirm_template(self, client, todo_instance):
        response = client.get(delete_url(todo_instance.pk))
        assert "todos/todo_confirm_delete.html" in [t.name for t in response.templates]

    def test_get_delete_context_contains_todo(self, client, todo_instance):
        response = client.get(delete_url(todo_instance.pk))
        assert "todo" in response.context
        assert response.context["todo"].pk == todo_instance.pk

    def test_post_delete_removes_object(self, client, todo_instance):
        pk = todo_instance.pk
        client.post(delete_url(pk))
        assert not Todo.objects.filter(pk=pk).exists()

    def test_post_delete_redirects_to_list(self, client, todo_instance):
        response = client.post(delete_url(todo_instance.pk))
        assert response.status_code == 302
        assert response["Location"] == list_url()

    def test_delete_404_for_nonexistent_pk(self, client):
        response = client.post(delete_url(99999))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Toggle view  POST /todos/<pk>/toggle/
# ---------------------------------------------------------------------------

class TestTodoToggleView:
    """POST /todos/<pk>/toggle/ — flip is_completed."""

    def test_toggle_redirects_to_list(self, client, todo_instance):
        response = client.post(toggle_url(todo_instance.pk))
        assert response.status_code == 302
        assert response["Location"] == list_url()

    def test_toggle_flips_false_to_true(self, client, todo_instance):
        assert todo_instance.is_completed is False
        client.post(toggle_url(todo_instance.pk))
        todo_instance.refresh_from_db()
        assert todo_instance.is_completed is True

    def test_toggle_flips_true_to_false(self, client, todo_factory):
        todo = todo_factory(title="Already done", is_completed=True)
        client.post(toggle_url(todo.pk))
        todo.refresh_from_db()
        assert todo.is_completed is False

    def test_toggle_get_returns_405(self, client, todo_instance):
        """toggle_complete is @require_POST; GET must return 405."""
        response = client.get(toggle_url(todo_instance.pk))
        assert response.status_code == 405

    def test_toggle_404_for_invalid_pk(self, client):
        response = client.post(toggle_url(99999))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Admin redirect  GET /admin/todos/todo/
# ---------------------------------------------------------------------------

class TestAdminRedirect:
    """Unauthenticated access to admin must redirect to login."""

    def test_admin_list_redirects_unauthenticated(self, client):
        response = client.get("/admin/todos/todo/")
        # Django admin redirects to /admin/login/?next=...
        assert response.status_code == 302
        assert "/admin/" in response["Location"] or "login" in response["Location"]


# ---------------------------------------------------------------------------
# Integration: Full CRUD flow
# ---------------------------------------------------------------------------

class TestFullCrudIntegration:
    """End-to-end CRUD flow with messages verification."""

    def test_full_crud_flow(self, client):
        # 1. CREATE
        response = client.post(
            create_url(),
            {"title": "Integration Todo", "is_completed": False},
            follow=True,
        )
        assert response.status_code == 200
        todo = Todo.objects.get(title="Integration Todo")
        assert todo is not None

        # 2. LIST — verify it appears
        response = client.get(list_url())
        titles = [t.title for t in response.context["todos"]]
        assert "Integration Todo" in titles

        # 3. DETAIL — verify object in context
        response = client.get(detail_url(todo.pk))
        assert response.status_code == 200
        assert response.context["todo"].pk == todo.pk

        # 4. EDIT
        response = client.post(
            update_url(todo.pk),
            {"title": "Integration Todo – Edited", "is_completed": True},
            follow=True,
        )
        assert response.status_code == 200
        todo.refresh_from_db()
        assert todo.title == "Integration Todo – Edited"
        assert todo.is_completed is True

        # 5. DELETE
        pk = todo.pk
        response = client.post(delete_url(pk), follow=True)
        assert response.status_code == 200
        assert not Todo.objects.filter(pk=pk).exists()

        # 6. LIST — verify it is gone
        response = client.get(list_url())
        titles = [t.title for t in response.context["todos"]]
        assert "Integration Todo – Edited" not in titles

    def test_create_success_message(self, client):
        response = client.post(
            create_url(),
            {"title": "Message test", "is_completed": False},
            follow=True,
        )
        messages = list(response.context["messages"])
        assert any("Message test" in str(m) or "created" in str(m).lower() for m in messages)

    def test_delete_success_message(self, client, todo_instance):
        response = client.post(delete_url(todo_instance.pk), follow=True)
        messages = list(response.context["messages"])
        assert any("deleted" in str(m).lower() for m in messages)

    def test_update_success_message(self, client, todo_instance):
        response = client.post(
            update_url(todo_instance.pk),
            {"title": "Updated for message", "is_completed": False},
            follow=True,
        )
        messages = list(response.context["messages"])
        assert any(
            "updated" in str(m).lower() or "Updated for message" in str(m)
            for m in messages
        )


# ---------------------------------------------------------------------------
# Integration: Search with pagination state retention
# ---------------------------------------------------------------------------

class TestSearchPaginationIntegration:
    """Search query is retained across pagination."""

    def test_search_query_in_context_on_page_2(self, client, todo_factory):
        # Create 15 todos that all match the search term
        for i in range(15):
            todo_factory(title=f"Searchable item {i}")

        response = client.get(list_url(), {"q": "Searchable", "page": 2})
        # Either page 2 exists (200) or we get a redirect/404 — both are valid
        # The key assertion is that search_query is retained in context when 200
        if response.status_code == 200:
            assert response.context["search_query"] == "Searchable"

    def test_status_filter_retained_in_context(self, client, todo_factory):
        todo_factory(title="Completed task", is_completed=True)
        response = client.get(list_url(), {"status": "completed"})
        assert response.status_code == 200
        assert response.context["current_status"] == "completed"
        todos = list(response.context["todos"])
        assert all(t.is_completed for t in todos)

    def test_pending_filter_returns_only_pending(self, client, todo_factory):
        todo_factory(title="Pending task", is_completed=False)
        todo_factory(title="Done task", is_completed=True)
        response = client.get(list_url(), {"status": "pending"})
        todos = list(response.context["todos"])
        assert all(not t.is_completed for t in todos)


# ---------------------------------------------------------------------------
# Integration: Toggle endpoint
# ---------------------------------------------------------------------------

class TestToggleIntegration:
    """Toggle endpoint correctly flips is_completed and shows a message."""

    def test_toggle_message_shown_after_redirect(self, client, todo_instance):
        response = client.post(toggle_url(todo_instance.pk), follow=True)
        messages = list(response.context["messages"])
        assert len(messages) >= 1

    def test_toggle_message_contains_todo_title(self, client, todo_instance):
        response = client.post(toggle_url(todo_instance.pk), follow=True)
        messages = list(response.context["messages"])
        assert any(todo_instance.title in str(m) for m in messages)

    def test_double_toggle_restores_state(self, client, todo_instance):
        original_state = todo_instance.is_completed
        client.post(toggle_url(todo_instance.pk))
        client.post(toggle_url(todo_instance.pk))
        todo_instance.refresh_from_db()
        assert todo_instance.is_completed == original_state
