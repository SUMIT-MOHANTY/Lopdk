from django.contrib import admin
from django.urls import path

from . import views

app_name = "todos"

urlpatterns = [
    # Django admin (mounted at the app level for convenience)
    path("admin/", admin.site.urls),

    # Todo CRUD
    path("", views.TodoListView.as_view(), name="todo-list"),
    path("<int:pk>/", views.TodoDetailView.as_view(), name="todo-detail"),
    path("create/", views.TodoCreateView.as_view(), name="todo-create"),
    path("<int:pk>/update/", views.TodoUpdateView.as_view(), name="todo-update"),
    path("<int:pk>/delete/", views.TodoDeleteView.as_view(), name="todo-delete"),
    path("<int:pk>/toggle/", views.toggle_complete, name="todo-toggle"),
]
