"""Custom template filters for the Todos app."""

from django import template

register = template.Library()


@register.filter(name="status_badge")
def status_badge(is_completed):
    """Return a Bootstrap-compatible badge HTML string for a todo status.

    Usage in templates::

        {{ todo.is_completed|status_badge }}
    """
    if is_completed:
        return '<span class="badge bg-success">Completed</span>'
    return '<span class="badge bg-warning text-dark">Pending</span>'


@register.filter(name="status_label")
def status_label(is_completed):
    """Return a plain-text status label.

    Usage::

        {{ todo.is_completed|status_label }}
    """
    return "Completed" if is_completed else "Pending"


@register.filter(name="toggle_icon")
def toggle_icon(is_completed):
    """Return an icon class string representing the toggle action.

    Usage::

        <i class="{{ todo.is_completed|toggle_icon }}"></i>
    """
    if is_completed:
        return "bi bi-arrow-counterclockwise"  # Bootstrap Icons: undo
    return "bi bi-check-circle"  # Bootstrap Icons: mark complete


@register.filter(name="row_class")
def row_class(is_completed):
    """Return a CSS class for a table row based on completion status.

    Usage::

        <tr class="{{ todo.is_completed|row_class }}">
    """
    return "table-success" if is_completed else ""
