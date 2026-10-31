"""Login, logout and the lockout response (FR-27, ADR-0009, ADR-0049)."""

from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.forms.utils import ErrorDict
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import LoginForm

LOCKOUT_MESSAGE = "Hesap geçici olarak kilitlendi. 15 dakika sonra yeniden deneyin."


class LoginView(auth_views.LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm


class LogoutView(auth_views.LogoutView):
    """POST only (Django's default since 5.0); redirects to LOGOUT_REDIRECT_URL."""


def lockout_response(
    request: HttpRequest,
    original_response: HttpResponse | None = None,
    credentials: dict | None = None,
) -> HttpResponse:
    """``AXES_LOCKOUT_CALLABLE``: the login page with the lockout error, HTTP 429.

    The form is not validated again (that would authenticate a second time);
    it keeps the submitted username and carries the lockout message as its
    only error (ADR-0049).
    """
    username = (credentials or {}).get("username") or request.POST.get("username", "")
    form = LoginForm(request, initial={"username": username})
    form._errors = ErrorDict(
        {NON_FIELD_ERRORS: form.error_class([LOCKOUT_MESSAGE], error_class="nonfield")}
    )
    return render(request, "registration/login.html", {"form": form}, status=429)
