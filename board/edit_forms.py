from django import forms

from .models import Post


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "description",
            "category",
            "location",
            "contact_name",
            "contact_email",
            "contact_method",
            "contact_phone",
        ]
