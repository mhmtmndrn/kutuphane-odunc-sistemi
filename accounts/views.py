"""Login, logout, password change and staff management (FR-21, FR-27, FR-41)."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordChangeForm
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.utils import ErrorDict
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from administration.errors import RuleViolation

from . import services
from .forms import LoginForm, PasswordResetByAdminForm, StaffCreateForm, StaffRoleForm
from .models import Role, StaffUser
from .permissions import require_role, staff_view

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


@staff_view
@require_http_methods(["GET", "POST"])
def password_change(request: HttpRequest) -> HttpResponse:
    """The staff member's own password (ADR-0043, KL-32)."""
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            services.change_own_password(request.user, form.cleaned_data["new_password1"])
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            update_session_auth_hash(request, request.user)
            messages.success(request, "Parolanız değiştirildi")
            return redirect("/")
    return render(request, "registration/password_change.html", {"form": form})


# --- Staff management (admin) -------------------------------------------------


def _get_staff(request: HttpRequest, pk: int) -> StaffUser:
    try:
        return services.get_staff(request.user, pk)
    except StaffUser.DoesNotExist:
        raise Http404("Personel bulunamadı") from None


@require_role(Role.ADMIN)
@require_http_methods(["GET"])
def staff_list(request: HttpRequest) -> HttpResponse:
    return render(
        request, "accounts/staff_list.html", {"staff": services.staff_list(request.user)}
    )


@require_role(Role.ADMIN)
@require_http_methods(["GET", "POST"])
def staff_create(request: HttpRequest) -> HttpResponse:
    form = StaffCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            user = services.create_staff(
                request.user, data["username"], data["full_name"], Role(data["role"]),
                data["password1"],
            )
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, "Personel hesabı oluşturuldu")
            return redirect("accounts:staff-detail", pk=user.pk)
    return render(request, "accounts/staff_form.html", {"form": form, "staff_user": None})


def _detail_page(request, staff_user, *, role_form=None, password_form=None, status=200):
    context = {
        "staff_user": staff_user,
        "role_form": role_form or StaffRoleForm(initial={"role": staff_user.role}),
        "password_form": password_form or PasswordResetByAdminForm(),
    }
    return render(request, "accounts/staff_form.html", context, status=status)


@require_role(Role.ADMIN)
@require_http_methods(["GET", "POST"])
def staff_detail(request: HttpRequest, pk: int) -> HttpResponse:
    staff_user = _get_staff(request, pk)
    if request.method == "GET":
        return _detail_page(request, staff_user)
    form = StaffRoleForm(request.POST)
    if form.is_valid():
        try:
            services.set_role(request.user, staff_user, Role(form.cleaned_data["role"]))
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, "Rol kaydedildi")
            return redirect("accounts:staff-detail", pk=pk)
    staff_user.refresh_from_db()
    return _detail_page(request, staff_user, role_form=form)


@require_role(Role.ADMIN)
@require_POST
def staff_deactivate(request: HttpRequest, pk: int) -> HttpResponse:
    staff_user = _get_staff(request, pk)
    try:
        services.deactivate_staff(request.user, staff_user)
    except RuleViolation as exc:
        messages.error(request, exc.message)
    else:
        messages.success(request, "Hesap pasifleştirildi")
    return redirect("accounts:staff-detail", pk=pk)


@require_role(Role.ADMIN)
@require_POST
def staff_reset_password(request: HttpRequest, pk: int) -> HttpResponse:
    staff_user = _get_staff(request, pk)
    form = PasswordResetByAdminForm(request.POST)
    if form.is_valid():
        try:
            services.reset_password(request.user, staff_user, form.cleaned_data["password"])
        except RuleViolation as exc:
            form.add_error("password", exc.message)
        else:
            messages.success(request, "Parola sıfırlandı; ilk girişte değiştirilecek")
            return redirect("accounts:staff-detail", pk=pk)
    return _detail_page(request, staff_user, password_form=form)


@require_role(Role.ADMIN)
@require_POST
def staff_unlock(request: HttpRequest, pk: int) -> HttpResponse:
    staff_user = _get_staff(request, pk)
    services.unlock_staff(request.user, staff_user)
    messages.success(request, "Hesap kilidi kaldırıldı")
    return redirect("accounts:staff-detail", pk=pk)
