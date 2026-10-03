import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Todo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=255,
                        verbose_name="Title",
                    ),
                ),
                (
                    "is_completed",
                    models.BooleanField(
                        default=False,
                        verbose_name="Completed",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Created At",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="Updated At",
                    ),
                ),
            ],
            options={
                "verbose_name": "Todo",
                "verbose_name_plural": "Todos",
                "ordering": ["-created_at"],
            },
        ),
    ]
