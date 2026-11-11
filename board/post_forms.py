
from django import forms

from .models import Post


class PostForm(forms.ModelForm):
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

    def clean_contact_email(self):
        email = self.cleaned_data.get("contact_email")
        if not email:
            raise forms.ValidationError("Email is required.")
        return email
