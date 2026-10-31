"""Forms for the accounts app."""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Role


class LoginForm(AuthenticationForm):
    """Django's login form with Turkish labels and autofocus on the username."""

    username = forms.CharField(
        label="Kullanıcı adı",
        max_length=150,
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Parola",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class StaffCreateForm(forms.Form):
    username = forms.CharField(label="Kullanıcı adı", max_length=150)
    full_name = forms.CharField(label="Ad soyad", max_length=150)
    role = forms.ChoiceField(label="Rol", choices=Role.choices)
    password1 = forms.CharField(label="Parola", strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Parola (tekrar)", strip=False, widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") and cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Parolalar aynı değil")
        return cleaned


class StaffRoleForm(forms.Form):
    role = forms.ChoiceField(label="Rol", choices=Role.choices)


class PasswordResetByAdminForm(forms.Form):
    password = forms.CharField(label="Yeni parola", strip=False, widget=forms.PasswordInput)
