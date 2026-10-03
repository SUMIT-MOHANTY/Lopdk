from django.db import models
from django.core.validators import MaxLengthValidator


class Todo(models.Model):
    title = models.CharField(
        max_length=255,
        validators=[MaxLengthValidator(255)],
        verbose_name="Title",
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name="Completed",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Todo"
        verbose_name_plural = "Todos"

    def __str__(self):
        return self.title

    def toggle_completed(self):
        """Flip the is_completed flag and save."""
        self.is_completed = not self.is_completed
        self.save(update_fields=["is_completed", "updated_at"])
