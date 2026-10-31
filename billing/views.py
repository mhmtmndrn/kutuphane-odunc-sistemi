"""Ledger screens (plan §4.1, G09). Views only call forms and services.

A rule violation re-shows the statement with 200 and the message (plan §4.0).
"""

from __future__ import annotations

from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from accounts.models import Role
from accounts.permissions import require_role, staff_view
from administration.errors import RuleViolation
from administration.money import format_tl
from members.services import member_by_no

from . import services
from .forms import CancelForm, PaymentForm, RefundForm, WaiverForm


def _get_member(member_no: int):
    try:
        return member_by_no(member_no)
    except RuleViolation as exc:
        raise Http404(exc.message) from None


def _charge_choices(rows) -> list[tuple[int, str]]:
    """Open charges for the waiver form: kind, date, amount and unpaid part."""
    return [
        (
            row.entry_id,
            f"{row.kind_label} · {timezone.localtime(row.created_at):%d.%m.%Y} · "
            f"{format_tl(row.amount_kurus)} (ödenmemiş {format_tl(row.unpaid_kurus)})",
        )
        for row in rows
        if row.unpaid_kurus
    ]


def _page(request: HttpRequest, member, *, payment_form=None, waiver_form=None) -> HttpResponse:
    rows = services.statement(member)
    charges = _charge_choices(rows)
    is_admin = request.user.role == Role.ADMIN
    context = {
        "member": member,
        "balance": services.member_balance(member),
        "rows": rows,
        "is_admin": is_admin,
        "payment_form": payment_form or PaymentForm(),
        "waiver_form": waiver_form or WaiverForm(charges=charges),
        "has_open_charges": bool(charges),
        "refundable_rows": [r for r in rows if r.refundable_kurus > 0] if is_admin else [],
        "cancellable_rows": [r for r in rows if r.manually_cancellable] if is_admin else [],
    }
    return render(request, "billing/statement.html", context)


def _form_errors(form) -> str:
    return "; ".join(str(error) for errors in form.errors.values() for error in errors)


@staff_view
@require_http_methods(["GET"])
def statement(request: HttpRequest, member_no: int) -> HttpResponse:
    return _page(request, _get_member(member_no))


@staff_view
@require_POST
def payment(request: HttpRequest, member_no: int) -> HttpResponse:
    member = _get_member(member_no)
    form = PaymentForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data["amount"]
        try:
            services.record_payment(request.user, member, amount if amount is not None else 0)
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, f"Ödeme alındı: {format_tl(amount)}")
            return redirect("billing:statement", member_no=member_no)
    return _page(request, member, payment_form=form)


@require_role(Role.ADMIN)
@require_POST
def waiver(request: HttpRequest, member_no: int) -> HttpResponse:
    member = _get_member(member_no)
    charges = _charge_choices(services.statement(member))
    form = WaiverForm(request.POST, charges=charges)
    if form.is_valid():
        data = form.cleaned_data
        try:
            charge = services.get_entry(member, data["charge_id"])
            services.waive(request.user, charge, data["amount"] or 0, data["reason"])
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, f"Af kaydedildi: {format_tl(data['amount'])}")
            return redirect("billing:statement", member_no=member_no)
    return _page(request, member, waiver_form=form)


def _row_action(request: HttpRequest, member_no: int, form_class, action) -> HttpResponse:
    """Refund and manual cancellation: one small form per fee row."""
    member = _get_member(member_no)
    form = form_class(request.POST)
    if not form.is_valid():
        messages.error(request, _form_errors(form))
        return _page(request, member)
    try:
        fee = services.get_entry(member, form.cleaned_data["fee_id"])
        success = action(fee, form.cleaned_data)
    except RuleViolation as exc:
        messages.error(request, exc.message)
        return _page(request, member)
    messages.success(request, success)
    return redirect("billing:statement", member_no=member_no)


@require_role(Role.ADMIN)
@require_POST
def refund(request: HttpRequest, member_no: int) -> HttpResponse:
    def action(fee, data) -> str:
        services.refund(request.user, fee, data["amount"] or 0)
        return f"Para iadesi kaydedildi: {format_tl(data['amount'])}"

    return _row_action(request, member_no, RefundForm, action)


@require_role(Role.ADMIN)
@require_POST
def cancel(request: HttpRequest, member_no: int) -> HttpResponse:
    def action(fee, data) -> str:
        cancellation = services.cancel_fee_manual(request.user, fee, data["reason"])
        return f"Bedel iptal edildi: {format_tl(cancellation.amount_kurus)}"

    return _row_action(request, member_no, CancelForm, action)
