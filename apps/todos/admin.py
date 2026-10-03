from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ["title", "is_completed", "created_at", "updated_at"]
    list_filter = ["is_completed"]
    search_fields = ["title"]
    date_hierarchy = "created_at"
    list_per_page = 25
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "is_completed"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
