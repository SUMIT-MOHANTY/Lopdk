"""
Unit tests for TodoForm.

Covers:
  - Valid submission with a normal title
  - Rejection of empty titles
  - Rejection of whitespace-only titles (clean_title)
  - Rejection of titles exceeding 255 characters
  - Update scenario with partial data (instance kwarg)
  - CSRF token presence in rendered form HTML
"""

import pytest
from django.test import RequestFactory

from apps.todos.forms import TodoForm
from apps.todos.models import Todo

pytestmark = pytest.mark.django_db


class TestTodoFormValidSubmission:
    """TodoForm accepts well-formed data."""

    def test_valid_title_is_accepted(self):
        form = TodoForm(data={"title": "Buy milk", "is_completed": False})
        assert form.is_valid(), form.errors

    def test_valid_form_saves_to_db(self):
        form = TodoForm(data={"title": "Saved via form", "is_completed": False})
        assert form.is_valid()
        todo = form.save()
        assert Todo.objects.filter(pk=todo.pk).exists()

    def test_is_completed_defaults_false_when_omitted(self):
        """Omitting is_completed (checkbox unchecked) should still be valid."""
        form = TodoForm(data={"title": "No checkbox"})
        assert form.is_valid(), form.errors
        assert form.cleaned_data["is_completed"] is False

    def test_title_exactly_255_chars_is_valid(self):
        form = TodoForm(data={"title": "x" * 255, "is_completed": False})
        assert form.is_valid(), form.errors


class TestTodoFormTitleRejection:
    """TodoForm rejects invalid title values."""

    def test_empty_title_is_rejected(self):
        form = TodoForm(data={"title": "", "is_completed": False})
        assert not form.is_valid()
        assert "title" in form.errors

    def test_whitespace_only_title_is_rejected(self):
        form = TodoForm(data={"title": "   ", "is_completed": False})
        assert not form.is_valid()
        assert "title" in form.errors

    def test_whitespace_only_error_message(self):
        form = TodoForm(data={"title": "\t\n ", "is_completed": False})
        form.is_valid()
        error_text = " ".join(form.errors["title"])
        assert "whitespace" in error_text.lower() or "empty" in error_text.lower()

    def test_title_exceeding_255_chars_is_rejected(self):
        form = TodoForm(data={"title": "a" * 256, "is_completed": False})
        assert not form.is_valid()
        assert "title" in form.errors

    def test_title_of_300_chars_is_rejected(self):
        form = TodoForm(data={"title": "z" * 300, "is_completed": False})
        assert not form.is_valid()
        assert "title" in form.errors


class TestTodoFormUpdateScenario:
    """TodoForm can update an existing Todo instance."""

    def test_update_title_via_form(self):
        todo = Todo.objects.create(title="Original title")
        form = TodoForm(
            data={"title": "Updated title", "is_completed": False},
            instance=todo,
        )
        assert form.is_valid(), form.errors
        updated = form.save()
        assert updated.pk == todo.pk
        assert updated.title == "Updated title"

    def test_update_is_completed_via_form(self):
        todo = Todo.objects.create(title="Mark complete", is_completed=False)
        form = TodoForm(
            data={"title": "Mark complete", "is_completed": True},
            instance=todo,
        )
        assert form.is_valid(), form.errors
        updated = form.save()
        assert updated.is_completed is True

    def test_update_with_invalid_data_does_not_save(self):
        todo = Todo.objects.create(title="Do not change me")
        form = TodoForm(
            data={"title": "", "is_completed": False},
            instance=todo,
        )
        assert not form.is_valid()
        todo.refresh_from_db()
        assert todo.title == "Do not change me"


class TestTodoFormCsrfToken:
    """
    Verify that a rendered TodoForm inside a Django template context
    includes a CSRF token input field.
    """

    def test_csrf_token_present_in_rendered_form(self):
        """
        Use Django's RequestFactory + template rendering to confirm the
        {% csrf_token %} tag produces a hidden input in the form HTML.
        """
        from django.template import Context, Template
        from django.middleware.csrf import get_token

        factory = RequestFactory(enforce_csrf_checks=False)
        request = factory.get("/")
        # Ensure a CSRF token is attached to the request session
        csrf_token = get_token(request)

        template = Template(
            "{% load i18n %}"
            "<form method='post'>{% csrf_token %}"
            "{{ form.as_p }}</form>"
        )
        context = Context({"form": TodoForm(), "request": request})
        rendered = template.render(context)

        assert 'name="csrfmiddlewaretoken"' in rendered
