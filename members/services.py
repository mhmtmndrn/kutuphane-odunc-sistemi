"""Member services (plan G06). Each public function is one transaction.

Creating and updating a member writes no audit event: the audit actions of
phase 4 small decision 8 do not include them. Consent events are their own
trail (KL-36). Reactivation writes MEMBER_REACTIVATED (KL-31).
"""

from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Case, IntegerField, Max, Q, Value, When

from accounts.models import Role
from accounts.permissions import require_role
from administration import clock
from administration.audit import AuditAction, record_audit
from administration.errors import RuleViolation
from administration.services import get_settings
from pdf.sheets import CARD_LAYOUT, SheetItem, render_sheet

from . import domain
from .models import CONSENT_ORDER, ConsentAction, ConsentEvent, Member

SEARCH_LIMIT = 50  # KL-10
_UPDATABLE = frozenset({"full_name", "phone", "email"})
# SQLite integers are 64-bit; a longer digit string cannot be a member number.
_MEMBER_NO_MAX_DIGITS = 18


def _clean_email(email: str | None) -> str | None:
    email = (email or "").strip()
    if not email:
        return None
    try:
        validate_email(email)
    except ValidationError:
        raise RuleViolation("Geçerli bir e-posta adresi girin") from None
    if len(email) > 254:
        raise RuleViolation("Geçerli bir e-posta adresi girin")
    return email


def _current_event(member: Member) -> ConsentEvent | None:
    return member.consent_events.order_by(*CONSENT_ORDER).first()


def _refresh_consent_flag(member: Member) -> None:
    """Recompute ``has_email_consent`` from the current event (ADR-0047)."""
    current = _current_event(member)
    member.has_email_consent = current is not None and current.action == ConsentAction.GIVEN
    member.save(update_fields=["has_email_consent"])


def _add_consent_event(actor, member: Member, given: bool, on: date) -> ConsentEvent:
    event = ConsentEvent.objects.create(
        member=member,
        action=ConsentAction.GIVEN if given else ConsentAction.WITHDRAWN,
        effective_on=on,
        recorded_by=actor,
    )
    _refresh_consent_flag(member)
    return event


@require_role(Role.CLERK)
@transaction.atomic
def create_member(actor, full_name: str, phone: str, email: str | None) -> Member:
    """``member_no`` is max + 1, assigned inside the IMMEDIATE transaction."""
    domain.validate_member_fields(full_name, phone)
    email = _clean_email(email)
    top = Member.objects.aggregate(top=Max("member_no"))["top"] or 0
    return Member.objects.create(
        member_no=top + 1, full_name=full_name.strip(), phone=phone.strip(), email=email
    )


@require_role(Role.CLERK)
@transaction.atomic
def update_member(actor, member: Member, **fields: str | None) -> Member:
    """Change ``full_name``, ``phone`` or ``email``.

    Clearing the e-mail while consent is GIVEN writes a WITHDRAWN event dated
    today in the same transaction (ADR-0047). An anonymized member is refused
    (plan §11, user decision).
    """
    unknown = fields.keys() - _UPDATABLE
    if unknown:
        raise TypeError(f"unknown member fields: {sorted(unknown)}")
    if member.is_anonymized:
        raise RuleViolation("Anonimleştirilmiş üye güncellenemez")
    full_name = fields.get("full_name", member.full_name) or ""
    phone = fields.get("phone", member.phone) or ""
    domain.validate_member_fields(full_name, phone)
    email = _clean_email(fields["email"]) if "email" in fields else member.email
    removing_email = member.email is not None and email is None
    member.full_name, member.phone, member.email = full_name.strip(), phone.strip(), email
    member.save()
    if removing_email:
        current = _current_event(member)
        if current is not None and current.action == ConsentAction.GIVEN:
            _add_consent_event(actor, member, False, clock.today())
    return member


@transaction.atomic
def search_members(q: str, limit: int = SEARCH_LIMIT) -> list[Member]:
    """KL-10. Digits: exact member number (listed first) or phone digits
    containing the query. Text: ``search_key`` containing ``normalize_tr(q)``,
    by name. LIKE wildcards in the query are literal (Django escapes them).
    """
    query = domain.classify_member_query(q)
    if query.is_empty:
        return []
    if query.text:
        matches = Member.objects.filter(search_key__contains=query.text)
        return list(matches.order_by("search_key", "member_no")[:limit])
    condition = Q(phone_digits__contains=query.digits)
    exact_first = Value(1)
    if len(query.digits) <= _MEMBER_NO_MAX_DIGITS:
        member_no = int(query.digits)
        condition |= Q(member_no=member_no)
        exact_first = Case(
            When(member_no=member_no, then=Value(0)), default=Value(1), output_field=IntegerField()
        )
    matches = Member.objects.filter(condition).order_by(exact_first, "member_no")
    return list(matches[:limit])


@require_role(Role.CLERK)
@transaction.atomic
def set_inactive(actor, member: Member) -> None:
    """Internal: only ``circulation.services.deactivate_member`` calls it (G11)."""
    member.is_active = False
    member.deactivated_on = clock.today()
    member.save(update_fields=["is_active", "deactivated_on"])


@require_role(Role.CLERK)
@transaction.atomic
def set_consent(actor, member: Member, given: bool, on: date) -> ConsentEvent:
    """Add a consent event under the ordering rule of ADR-0047."""
    current = _current_event(member)
    domain.check_consent_change(
        given=given,
        on=on,
        today=clock.today(),
        has_email=bool(member.email),
        currently_given=current is not None and current.action == ConsentAction.GIVEN,
    )
    return _add_consent_event(actor, member, given, on)


@require_role(Role.CLERK)
@transaction.atomic
def reactivate_member(actor, member: Member) -> None:
    """FR-40, ADR-0042: any staff member; retention restarts on the next
    deactivation."""
    if member.is_anonymized:
        raise RuleViolation("Anonimleştirilmiş üye aktifleştirilemez")
    if member.is_active:
        raise RuleViolation("Üye zaten aktif")
    member.is_active = True
    member.deactivated_on = None
    member.save(update_fields=["is_active", "deactivated_on"])
    record_audit(
        actor, AuditAction.MEMBER_REACTIVATED, "member", member.pk, {"member_no": member.member_no}
    )


@transaction.atomic
def member_by_no(member_no: int) -> Member:
    member = Member.objects.filter(member_no=member_no).first()
    if member is None:
        raise RuleViolation("Üye bulunamadı")
    return member


@transaction.atomic
def consent_dates(member: Member) -> tuple[date | None, date | None]:
    """The latest effective dates of giving and of withdrawing consent."""
    latest = {
        row["action"]: row["last"]
        for row in member.consent_events.values("action").annotate(last=Max("effective_on"))
    }
    return latest.get(ConsentAction.GIVEN), latest.get(ConsentAction.WITHDRAWN)


# --- Member cards (G08: FR-38, ADR-0032, ADR-0036, KL-25) -----------------------

SELECTION_MAX = 240  # KL-25
RANGE_AND_LIST = "Aralık ya da seçim kutuları kullanın, ikisini birden değil"


@transaction.atomic
def members_for_cards(
    member_nos: list[int] | None, start: int | None, end: int | None
) -> list[int]:
    """Member numbers to print, ascending (KL-25).

    Either a member number range (both ends positive, at most 240 wide) or
    the checkbox list (at most 240). Inactive and anonymized members are
    skipped, for the list too.
    """
    has_list = bool(member_nos)
    has_range = start is not None or end is not None
    if has_list and has_range:
        raise RuleViolation(RANGE_AND_LIST)
    if not (has_list or has_range):
        raise RuleViolation("En az bir üye seçin")
    printable = Member.objects.filter(is_active=True, anonymized_at__isnull=True).order_by(
        "member_no"
    )
    if has_range:
        if start is None or end is None or start < 1 or end < 1:
            raise RuleViolation("Başlangıç ve bitiş pozitif üye no olmalı")
        if start > end:
            raise RuleViolation("Başlangıç bitişten büyük olamaz")
        if end - start + 1 > SELECTION_MAX:
            raise RuleViolation("En fazla 240 öğe seçilebilir")
        nos = list(printable.filter(member_no__range=(start, end)).values_list("member_no", flat=True))
        if not nos:
            raise RuleViolation("Aralıkta basılacak üye yok")
        return nos
    wanted = set(member_nos or [])
    if len(wanted) > SELECTION_MAX:
        raise RuleViolation("En fazla 240 öğe seçilebilir")
    nos = list(printable.filter(member_no__in=wanted).values_list("member_no", flat=True))
    if not nos:
        raise RuleViolation("En az bir üye seçin")
    return nos


@transaction.atomic
def member_card_pdf(member_nos: list[int]) -> bytes:
    """One card per member: library name, "Üye No" and the barcode of the
    unpadded member number. No name is printed (ADR-0032)."""
    library_name = get_settings().library_name
    items = [
        SheetItem(
            header=library_name, barcode_value=str(no), caption=f"Üye No: {no}", footer=""
        )
        for no in member_nos
    ]
    return render_sheet(items, CARD_LAYOUT)
