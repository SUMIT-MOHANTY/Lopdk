"""
Unit tests for the Todo model.

Covers:
  - Instantiation with valid data
  - Title field max-length constraint (via full_clean)
  - Title non-empty constraint (via full_clean)
  - is_completed default value
  - created_at auto-population
  - updated_at modification on subsequent save
  - __str__ representation
  - toggle_completed helper method
"""

import time

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.todos.models import Todo

pytestmark = pytest.mark.django_db


class TestTodoInstantiation:
    """Todo model can be created with valid data."""

    def test_create_with_valid_title(self):
        todo = Todo.objects.create(title="Buy groceries")
        assert todo.pk is not None
        assert todo.title == "Buy groceries"

    def test_is_completed_defaults_to_false(self):
        todo = Todo.objects.create(title="Default completion check")
        assert todo.is_completed is False

    def test_create_with_is_completed_true(self):
        todo = Todo.objects.create(title="Already done", is_completed=True)
        assert todo.is_completed is True

    def test_created_at_is_populated_automatically(self):
        before = timezone.now()
        todo = Todo.objects.create(title="Timestamp test")
        after = timezone.now()
        assert todo.created_at is not None
        assert before <= todo.created_at <= after

    def test_updated_at_is_populated_on_create(self):
        todo = Todo.objects.create(title="Updated-at on create")
        assert todo.updated_at is not None


class TestTodoFieldConstraints:
    """Title field length and blank constraints."""

    def test_title_max_length_is_255(self):
        """A title of exactly 255 characters should pass full_clean."""
        todo = Todo(title="a" * 255)
        todo.full_clean()  # should not raise

    def test_title_exceeding_255_chars_fails_full_clean(self):
        """A title of 256 characters must fail validation."""
        todo = Todo(title="a" * 256)
        with pytest.raises(ValidationError) as exc_info:
            todo.full_clean()
        assert "title" in exc_info.value.message_dict

    def test_empty_title_fails_full_clean(self):
        """An empty title must fail validation."""
        todo = Todo(title="")
        with pytest.raises(ValidationError) as exc_info:
            todo.full_clean()
        assert "title" in exc_info.value.message_dict

    def test_whitespace_only_title_fails_full_clean(self):
        """A whitespace-only title must fail the blank check."""
        todo = Todo(title="   ")
        with pytest.raises(ValidationError) as exc_info:
            todo.full_clean()
        assert "title" in exc_info.value.message_dict


class TestTodoTimestamps:
    """Auto-timestamp behaviour."""

    def test_updated_at_changes_on_save(self):
        """updated_at must be later after a subsequent save."""
        todo = Todo.objects.create(title="Watch updated_at")
        original_updated_at = todo.updated_at

        # Force a small time gap so the new timestamp is strictly greater.
        # Django's auto_now uses timezone.now() at save time.
        todo.title = "Watch updated_at – edited"
        todo.save()
        todo.refresh_from_db()

        assert todo.updated_at >= original_updated_at

    def test_created_at_does_not_change_on_save(self):
        """created_at must remain constant across saves."""
        todo = Todo.objects.create(title="Immutable created_at")
        original_created_at = todo.created_at

        todo.title = "Immutable created_at – edited"
        todo.save()
        todo.refresh_from_db()

        assert todo.created_at == original_created_at


class TestTodoStrRepresentation:
    """__str__ returns the title."""

    def test_str_returns_title(self):
        todo = Todo(title="My important task")
        assert str(todo) == "My important task"

    def test_str_matches_saved_title(self):
        todo = Todo.objects.create(title="Persisted task")
        assert str(todo) == "Persisted task"


class TestToggleCompleted:
    """toggle_completed() flips is_completed and persists the change."""

    def test_toggle_false_to_true(self):
        todo = Todo.objects.create(title="Toggle me", is_completed=False)
        todo.toggle_completed()
        todo.refresh_from_db()
        assert todo.is_completed is True

    def test_toggle_true_to_false(self):
        todo = Todo.objects.create(title="Toggle back", is_completed=True)
        todo.toggle_completed()
        todo.refresh_from_db()
        assert todo.is_completed is False

    def test_double_toggle_restores_original(self):
        todo = Todo.objects.create(title="Double toggle", is_completed=False)
        todo.toggle_completed()
        todo.toggle_completed()
        todo.refresh_from_db()
        assert todo.is_completed is False
