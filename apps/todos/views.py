from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import TodoForm
from .models import Todo


class TodoListView(ListView):
    """List all todos with optional search and status filtering, paginated."""

    model = Todo
    template_name = "todos/todo_list.html"
    context_object_name = "todos"
    paginate_by = 10

    def get_queryset(self):
        # Base queryset – select_related / prefetch_related hooks are ready
        # for a future User FK; no raw SQL used.
        queryset = (
            Todo.objects.all()
            # .select_related("user")   # uncomment when User FK is added
            # .prefetch_related(...)     # uncomment for M2M relations
        )

        # --- Search ---
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )

        # --- Status filter ---
        status = self.request.GET.get("status", "").strip()
        if status == "completed":
            queryset = queryset.filter(is_completed=True)
        elif status == "pending":
            queryset = queryset.filter(is_completed=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retain filter state across pagination
        context["search_query"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        return context


class TodoDetailView(DetailView):
    """Display a single Todo."""

    model = Todo
    template_name = "todos/todo_detail.html"
    context_object_name = "todo"


class TodoCreateView(SuccessMessageMixin, CreateView):
    """Create a new Todo."""

    model = Todo
    form_class = TodoForm
    template_name = "todos/todo_form.html"
    success_url = reverse_lazy("todo-list")
    success_message = "Todo \"%(title)s\" was created successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Todo"
        context["submit_label"] = "Create"
        return context


class TodoUpdateView(SuccessMessageMixin, UpdateView):
    """Update an existing Todo."""

    model = Todo
    form_class = TodoForm
    template_name = "todos/todo_form.html"
    success_url = reverse_lazy("todo-list")
    success_message = "Todo \"%(title)s\" was updated successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Update Todo"
        context["submit_label"] = "Save Changes"
        return context


class TodoDeleteView(SuccessMessageMixin, DeleteView):
    """Delete a Todo with confirmation."""

    model = Todo
    template_name = "todos/todo_confirm_delete.html"
    context_object_name = "todo"
    success_url = reverse_lazy("todo-list")
    success_message = "Todo was deleted successfully."

    def delete(self, request, *args, **kwargs):
        # SuccessMessageMixin does not fire on DeleteView by default in older
        # Django versions; add the message manually before deletion.
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@require_POST
def toggle_complete(request, pk):
    """POST-only FBV: flip the is_completed flag of a Todo."""
    todo = get_object_or_404(Todo, pk=pk)
    todo.is_completed = not todo.is_completed
    todo.save(update_fields=["is_completed", "updated_at"])
    status_label = "completed" if todo.is_completed else "marked as pending"
    messages.success(
        request,
        f"Todo \"{todo.title}\" {status_label}.",
    )
    return redirect("todo-list")
