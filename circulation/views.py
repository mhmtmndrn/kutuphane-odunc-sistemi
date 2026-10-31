"""Circulation desk screens (plan §4.1, G11, G12). Views only call forms and
services; a rule violation re-shows the same screen with 200 (plan §4.0)."""

from __future__ import annotations

from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from accounts.models import Role
from accounts.permissions import require_role, staff_view
from administration import clock
from administration.errors import RuleViolation
from administration.money import format_tl
from catalog.models import CopyStatus
from catalog.services import find_copy, is_barcode
from members.services import search_members

from . import services
from .domain import classify_member_input
from .forms import CopyMarkForm, NoteForm

COPY_BARCODE_WARNING = "Bu bir nüsha barkodu. Üye kartını okutun."
# SQLite integers are 64-bit; a longer digit string is no member number.
_MEMBER_NO_MAX_DIGITS = 18


def _see_other(url: str) -> HttpResponseRedirect:
    """303 after a successful POST (plan G11)."""
    response = HttpResponseRedirect(url)
    response.status_code = 303
    return response


def _member_no(value: str) -> int | None:
    value = value.strip()
    if value.isascii() and value.isdigit() and len(value) <= _MEMBER_NO_MAX_DIGITS:
        return int(value)
    return None


# --- Check-out (FR-07, FR-08, FR-11, ADR-0046) ------------------------------------


def _checkout_context(uye: str, nusha: str) -> tuple[dict, list[str]]:
    """Interpret the member and copy fields; returns the context and errors."""
    today = clock.today()
    context: dict = {"uye": uye, "nusha": nusha.strip()}
    errors: list[str] = []
    entry = classify_member_input(uye)
    if not entry.value:
        return context, errors
    if entry.kind == "COPY_BARCODE":
        context["warning"] = COPY_BARCODE_WARNING
        return context, errors
    if entry.kind in ("PHONE", "TEXT"):
        results = search_members(entry.value)
        context["member_results"] = results
        if not results:
            errors.append("Üye bulunamadı")
        return context, errors
    member_no = _member_no(entry.value)
    try:
        if member_no is None:
            raise RuleViolation("Üye bulunamadı")
        status = services.member_status(member_no, today)
    except RuleViolation as exc:
        errors.append(exc.message)
        return context, errors
    context["status"] = status
    barcode = context["nusha"]
    if not barcode:
        return context, errors
    if not is_barcode(barcode):
        copies = services.copies_matching(barcode, CopyStatus.ON_SHELF)
        context["copy_results"] = copies
        if not copies:
            errors.append("Nüsha bulunamadı")
        return context, errors
    try:
        context["preview"] = services.preview_checkout(member_no, barcode, today)
    except RuleViolation as exc:
        errors.append(exc.message)
    return context, errors


def _checkout_page(request: HttpRequest, uye: str, nusha: str, error: str | None = None):
    context, errors = _checkout_context(uye, nusha)
    if error:
        errors.insert(0, error)
    context["errors"] = errors
    preview = context.get("preview")
    status = context.get("status")
    context["can_confirm"] = bool(
        preview and not preview.blockers and status and not status.blockers and not error
    )
    context["next"] = f"{reverse('circulation:checkout')}?uye={status.member.member_no}" if status else ""
    return render(request, "circulation/checkout.html", context)


@staff_view
@require_http_methods(["GET", "POST"])
def checkout(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _checkout_page(request, request.GET.get("uye", ""), request.GET.get("nusha", ""))
    uye, nusha = request.POST.get("uye", ""), request.POST.get("nusha", "")
    member_no = _member_no(uye)
    try:
        if member_no is None:
            raise RuleViolation("Üye bulunamadı")
        loan = services.check_out(request.user, member_no, nusha)
    except RuleViolation as exc:
        return _checkout_page(request, uye, nusha, exc.message)
    messages.success(request, f"Son tarih {loan.due_on:%d.%m.%Y}")
    return _see_other(reverse("circulation:checkout"))


@staff_view
@require_POST
def renew(request: HttpRequest, loan_id: int) -> HttpResponse:
    loan = services.get_loan(loan_id)
    if loan is None or loan.member is None:
        raise Http404("Ödünç bulunamadı")
    member_no = str(loan.member.member_no)
    try:
        renewed = services.renew(request.user, loan_id)
    except RuleViolation as exc:
        # The checkout screen lists the member's loans with their buttons.
        return _checkout_page(request, member_no, "", exc.message)
    messages.success(request, f"Uzatıldı; yeni son tarih {renewed.due_on:%d.%m.%Y}")
    target = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        target = f"{reverse('circulation:checkout')}?uye={member_no}"
    return _see_other(target)


# --- Check-in (FR-09, FR-11, FR-12) -----------------------------------------------


def _checkin_page(request: HttpRequest, nusha: str = "", error: str | None = None, copies=None):
    context = {"nusha": nusha, "errors": [error] if error else [], "copy_results": copies}
    return render(request, "circulation/checkin.html", context)


@staff_view
@require_http_methods(["GET", "POST"])
def checkin(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _checkin_page(request)
    nusha = request.POST.get("nusha", "").strip()
    if not nusha:
        return _checkin_page(request)
    if not is_barcode(nusha):
        copies = services.copies_matching(nusha, CopyStatus.ON_LOAN)
        error = None if copies else "Nüsha bulunamadı"
        return _checkin_page(request, nusha, error, copies)
    try:
        result = services.check_in(request.user, nusha)
    except RuleViolation as exc:
        return _checkin_page(request, nusha, exc.message)
    if result.fine_kurus:
        messages.success(request, f"İade alındı; {format_tl(result.fine_kurus)} ceza yazıldı")
    else:
        messages.success(request, "İade alındı")
    return _see_other(reverse("circulation:checkin"))


# --- Copy screen and status operations (G12: FR-15, FR-16, FR-39) ----------------

# Operations shown for each status, and who sees them (architecture §5.1).
_ADMIN_ACTIONS = {
    CopyStatus.ON_SHELF: ("kayip", "hasarli", "kayittan-dus"),
    CopyStatus.ON_LOAN: ("kayip", "hasarli"),
    CopyStatus.LOST: ("bulundu", "kayittan-dus"),
    CopyStatus.DAMAGED: ("onarildi", "kayittan-dus"),
    CopyStatus.WITHDRAWN: (),
}
_CLERK_ACTIONS = {CopyStatus.LOST: ("bulundu",)}


def _get_copy(barcode: str):
    try:
        return find_copy(barcode)
    except RuleViolation as exc:
        raise Http404(exc.message) from None


def _copy_page(request: HttpRequest, copy, error: str | None = None) -> HttpResponse:
    copy.refresh_from_db()
    loans = services.copy_loans(copy)
    is_admin = request.user.role == Role.ADMIN
    actions = (_ADMIN_ACTIONS if is_admin else _CLERK_ACTIONS).get(copy.status, ())
    context = {
        "copy": copy,
        "loans": loans,
        "open_loan": next((loan for loan in loans if loan.is_open), None),
        "actions": set(actions),
        "with_fee": copy.status == CopyStatus.ON_LOAN,
        "errors": [error] if error else [],
    }
    return render(request, "circulation/copy_detail.html", context)


def _after_copy_post(request: HttpRequest, copy, operation) -> HttpResponse:
    try:
        message = operation()
    except RuleViolation as exc:
        return _copy_page(request, copy, exc.message)
    messages.success(request, message)
    return _see_other(reverse("circulation:copy", args=[copy.barcode]))


@staff_view
@require_http_methods(["GET"])
def copy_detail(request: HttpRequest, barcode: str) -> HttpResponse:
    return _copy_page(request, _get_copy(barcode))


def _mark(request: HttpRequest, barcode: str, target: str) -> HttpResponse:
    copy = _get_copy(barcode)
    form = CopyMarkForm(request.POST)
    if not form.is_valid():
        return _copy_page(request, copy, "; ".join(e for errs in form.errors.values() for e in errs))
    fee, note = form.cleaned_data["fee"], form.cleaned_data["note"]
    label = "kayıp" if target == CopyStatus.LOST else "hasarlı"

    def operation() -> str:
        if copy.status == CopyStatus.ON_LOAN:
            if fee is None:
                raise RuleViolation("Bedel girin (bedel yoksa 0)")
            mark = services.mark_lost if target == CopyStatus.LOST else services.mark_damaged
            mark(request.user, copy.barcode, fee, note)
        else:
            services.mark_shelf_copy(request.user, copy.barcode, target, note)
        return f"Nüsha {label} olarak işaretlendi"

    return _after_copy_post(request, copy, operation)


@require_role(Role.ADMIN)
@require_POST
def copy_lost(request: HttpRequest, barcode: str) -> HttpResponse:
    return _mark(request, barcode, CopyStatus.LOST)


@require_role(Role.ADMIN)
@require_POST
def copy_damaged(request: HttpRequest, barcode: str) -> HttpResponse:
    return _mark(request, barcode, CopyStatus.DAMAGED)


@staff_view
@require_POST
def copy_found(request: HttpRequest, barcode: str) -> HttpResponse:
    copy = _get_copy(barcode)
    try:
        result = services.mark_found(request.user, copy.barcode)
    except RuleViolation as exc:
        return _copy_page(request, copy, exc.message)
    text = "Nüsha bulundu olarak işaretlendi"
    if result.cancelled_kurus:
        text += f"; {format_tl(result.cancelled_kurus)} ödenmemiş bedel iptal edildi"
    messages.success(request, text)
    if result.refundable_kurus:
        # The refundable fee belongs to the copy's latest loan (ADR-0037).
        member = services.get_loan(max(loan.pk for loan in services.copy_loans(copy))).member
        messages.info(
            request,
            format_html(
                'Ödenmiş {} para iadesi için üyenin borç sayfasında: <a href="{}">Borç dökümü</a>',
                format_tl(result.refundable_kurus),
                reverse("billing:statement", args=[member.member_no]),
            ),
        )
    return _see_other(reverse("circulation:copy", args=[copy.barcode]))


def _note(request: HttpRequest) -> str:
    form = NoteForm(request.POST)
    return form.cleaned_data["note"] if form.is_valid() else ""


@require_role(Role.ADMIN)
@require_POST
def copy_repaired(request: HttpRequest, barcode: str) -> HttpResponse:
    copy = _get_copy(barcode)

    def operation() -> str:
        services.repair(request.user, copy.barcode, _note(request))
        return "Nüsha onarıldı olarak işaretlendi"

    return _after_copy_post(request, copy, operation)


@require_role(Role.ADMIN)
@require_POST
def copy_withdraw(request: HttpRequest, barcode: str) -> HttpResponse:
    copy = _get_copy(barcode)

    def operation() -> str:
        note = _note(request)
        if copy.status == CopyStatus.ON_SHELF:
            services.mark_shelf_copy(request.user, copy.barcode, CopyStatus.WITHDRAWN, note)
        else:
            services.withdraw(request.user, copy.barcode, note)
        return "Nüsha kayıttan düşüldü"

    return _after_copy_post(request, copy, operation)
