from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    """ModelForm for creating and updating Todo instances."""

    class Meta:
        model = Todo
        fields = ["title", "is_completed"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter todo title…",
                    "autofocus": True,
                    "maxlength": 255,
                }
            ),
            "is_completed": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        labels = {
            "title": "Title",
            "is_completed": "Mark as completed",
        }
        help_texts = {
            "title": "Maximum 255 characters.",
        }

    def clean_title(self):
        """Reject empty or whitespace-only titles and enforce max_length."""
        title = self.cleaned_data.get("title", "")
        title = title.strip()
        if not title:
            raise forms.ValidationError(
                "Title cannot be empty or contain only whitespace.",
                code="blank_title",
            )
        if len(title) > 255:
            raise forms.ValidationError(
                "Title must be 255 characters or fewer (%(length)d given).",
                code="max_length",
                params={"length": len(title)},
            )
        return title
