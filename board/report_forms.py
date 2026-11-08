from django import forms
from .models import PostReport


class PostReportForm(forms.ModelForm):
    class Meta:
        model = PostReport
        fields = ["reason", "details"]

        widgets = {
            "reason": forms.TextInput(
                attrs={"placeholder": "Reason for reporting"}
            ),
            "details": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Additional details (optional)",
                }
            ),
        }
