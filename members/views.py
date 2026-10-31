"""Member screens (plan §4.1, G06). Views only call forms and services."""

from __future__ import annotations

from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from accounts.permissions import staff_view
from administration import clock
from administration.errors import RuleViolation

from . import services
from .forms import CardSelectionForm, ConsentForm, MemberForm
from .models import Member


def _get_member(member_no: int) -> Member:
    try:
        return services.member_by_no(member_no)
    except RuleViolation as exc:
        raise Http404(exc.message) from None


@staff_view
@require_http_methods(["GET"])
def member_search(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("q", "").strip()
    results = services.search_members(q) if q else []
    has_printable = any(m.is_active and not m.is_anonymized for m in results)
    context = {"q": q, "results": results, "has_printable": has_printable}
    return render(request, "members/search.html", context)


@staff_view
@require_http_methods(["GET", "POST"])
def member_create(request: HttpRequest) -> HttpResponse:
    form = MemberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            member = services.create_member(
                request.user, data["full_name"], data["phone"], data["email"]
            )
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, "Üye kaydedildi")
            return redirect("members:detail", member_no=member.member_no)
    return render(request, "members/form.html", {"form": form, "member": None})


@staff_view
@require_http_methods(["GET", "POST"])
def member_edit(request: HttpRequest, member_no: int) -> HttpResponse:
    member = _get_member(member_no)
    if request.method == "GET":
        form = MemberForm(
            initial={"full_name": member.full_name, "phone": member.phone, "email": member.email}
        )
    else:
        form = MemberForm(request.POST)
        if form.is_valid():
            try:
                services.update_member(request.user, member, **form.cleaned_data)
            except RuleViolation as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(request, "Üye bilgileri kaydedildi")
                return redirect("members:detail", member_no=member_no)
    return render(request, "members/form.html", {"form": form, "member": member})


def _detail_page(request: HttpRequest, member: Member, *, consent_form=None) -> HttpResponse:
    given_on, withdrawn_on = services.consent_dates(member)
    context = {
        "member": member,
        "given_on": given_on,
        "withdrawn_on": withdrawn_on,
        "consent_form": consent_form or ConsentForm(initial={"on": clock.today()}),
        "can_reactivate": not member.is_active and not member.is_anonymized,
    }
    return render(request, "members/detail.html", context)


@staff_view
@require_http_methods(["GET"])
def member_detail(request: HttpRequest, member_no: int) -> HttpResponse:
    return _detail_page(request, _get_member(member_no))


@staff_view
@require_POST
def member_reactivate(request: HttpRequest, member_no: int) -> HttpResponse:
    member = _get_member(member_no)
    try:
        services.reactivate_member(request.user, member)
    except RuleViolation as exc:
        # Plan §4.0: re-show the same screen with 200 and the message.
        messages.error(request, exc.message)
        return _detail_page(request, _get_member(member_no))
    messages.success(request, "Üye aktifleştirildi")
    return redirect("members:detail", member_no=member_no)


@staff_view
@require_POST
def member_consent(request: HttpRequest, member_no: int) -> HttpResponse:
    member = _get_member(member_no)
    form = ConsentForm(request.POST)
    if form.is_valid():
        given = form.cleaned_data["given"]
        try:
            services.set_consent(request.user, member, given, form.cleaned_data["on"])
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, "Rıza kaydedildi" if given else "Rıza geri alındı")
            return redirect("members:detail", member_no=member_no)
    return _detail_page(request, _get_member(member_no), consent_form=form)


@staff_view
@require_http_methods(["GET", "POST"])
def card_print(request: HttpRequest) -> HttpResponse:
    """GET: the range form; POST: a range or ``member_nos`` -> card PDF (ADR-0036)."""
    form = CardSelectionForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            member_nos = services.members_for_cards(data["member_nos"], data["start"], data["end"])
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            response = HttpResponse(
                services.member_card_pdf(member_nos), content_type="application/pdf"
            )
            response["Content-Disposition"] = 'inline; filename="uye-kartlari.pdf"'
            return response
    return render(request, "members/card_range.html", {"form": form})
