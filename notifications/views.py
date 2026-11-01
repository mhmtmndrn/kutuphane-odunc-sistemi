"""Overdue list and manual reminders (plan §4.1, G13). Views only call forms
and services; a rule violation re-shows the list with 200 (plan §4.0)."""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from accounts.permissions import staff_view
from administration import clock
from administration.errors import RuleViolation

from . import services
from .domain import OUTCOME_LABELS

EMPTY_SELECTION = "Hatırlatma göndermek için en az bir ödünç seçin"
# SQLite integers are 64-bit; a longer digit string is no loan id.
_ID_MAX_DIGITS = 18


def _see_other(url: str) -> HttpResponseRedirect:
    """303 after a successful POST (G11 convention)."""
    response = HttpResponseRedirect(url)
    response.status_code = 303
    return response


def _list_page(request: HttpRequest, error: str | None = None) -> HttpResponse:
    context = {
        "entries": services.overdue_list(clock.today()),
        "errors": [error] if error else [],
    }
    return render(request, "notifications/overdue.html", context)


def _loan_ids(values: list[str]) -> list[int]:
    ids = []
    for value in values:
        value = value.strip()
        if not (value.isascii() and value.isdigit() and len(value) <= _ID_MAX_DIGITS):
            raise RuleViolation("Ödünç bulunamadı")
        ids.append(int(value))
    return ids


@staff_view
@require_GET
def overdue_list(request: HttpRequest) -> HttpResponse:
    return _list_page(request)


@staff_view
@require_POST
def remind(request: HttpRequest) -> HttpResponse:
    values = request.POST.getlist("loan_ids")
    if not values:
        return _list_page(request, EMPTY_SELECTION)
    try:
        results = services.send_manual_reminders(request.user, _loan_ids(values))
    except RuleViolation as exc:
        return _list_page(request, exc.message)
    for result in results:
        who = " ".join(str(part) for part in (result.member_no, result.full_name) if part)
        text = f"{who or '—'}, {result.title}: {OUTCOME_LABELS[result.outcome]}"
        if result.outcome == "sent":
            messages.success(request, text)
        else:
            messages.warning(request, text)
    return _see_other(reverse("notifications:overdue"))
