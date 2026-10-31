"""Administration screens (plan §4.1). Views only call forms and services."""

from __future__ import annotations

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from accounts.models import Role
from accounts.permissions import require_role, staff_view

from . import services
from .errors import RuleViolation
from .forms import ClosedDateForm, SettingsForm, WeeklyClosedForm

AUDIT_PAGE_SIZE = 50  # KL-11


@staff_view
@require_http_methods(["GET"])
def home(request: HttpRequest) -> HttpResponse:
    panel = services.admin_home(request.user) if request.user.role == Role.ADMIN else None
    return render(request, "administration/home.html", {"panel": panel})


@require_role(Role.ADMIN)
@require_http_methods(["GET", "POST"])
def settings_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SettingsForm(request.POST)
        if form.is_valid():
            try:
                services.update_settings(request.user, **form.changes())
            except RuleViolation as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(request, "Ayarlar kaydedildi")
                return redirect("administration:settings")
    else:
        form = SettingsForm(initial=SettingsForm.initial_from(services.get_settings()))
    return render(request, "administration/settings.html", {"form": form})


def _closed_days_page(request, *, weekly_form=None, date_form=None, status=200) -> HttpResponse:
    weekly_form = weekly_form or WeeklyClosedForm(
        initial={"weekdays": [str(d) for d in sorted(services.weekly_closed())]}
    )
    context = {
        "weekly_form": weekly_form,
        "date_form": date_form or ClosedDateForm(),
        "closed_dates": services.closed_date_list(),
    }
    return render(request, "administration/closed_days.html", context, status=status)


@require_role(Role.ADMIN)
@require_http_methods(["GET", "POST"])
def closed_days(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _closed_days_page(request)
    form = WeeklyClosedForm(request.POST)
    if form.is_valid():
        try:
            services.set_weekly_closed(request.user, set(form.cleaned_data["weekdays"]))
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, "Haftalık kapalı günler kaydedildi")
            return redirect("administration:closed-days")
    return _closed_days_page(request, weekly_form=form)


@require_role(Role.ADMIN)
@require_POST
def closed_date_add(request: HttpRequest) -> HttpResponse:
    form = ClosedDateForm(request.POST)
    if form.is_valid():
        try:
            services.add_closed_date(
                request.user, form.cleaned_data["date"], form.cleaned_data["note"]
            )
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, "Kapalı tarih eklendi")
            return redirect("administration:closed-days")
    return _closed_days_page(request, date_form=form)


@require_role(Role.ADMIN)
@require_POST
def closed_date_remove(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        services.remove_closed_date(request.user, pk)
    except RuleViolation as exc:
        messages.error(request, exc.message)
    else:
        messages.success(request, "Kapalı tarih silindi")
    return redirect("administration:closed-days")


@require_role(Role.ADMIN)
@require_http_methods(["GET"])
def audit_list(request: HttpRequest) -> HttpResponse:
    paginator = Paginator(services.audit_events(request.user), AUDIT_PAGE_SIZE)
    page = paginator.get_page(request.GET.get("sayfa"))
    return render(request, "administration/audit_list.html", {"page": page})
