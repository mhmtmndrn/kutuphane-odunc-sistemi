"""Forms for the accounts app."""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm


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
