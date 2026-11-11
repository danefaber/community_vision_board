from django import forms


class SubscribeForm(forms.Form):
    email = forms.EmailField(label="Your email")

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()