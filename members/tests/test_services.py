"""Service tests for members (G06).

TC-44…TC-51, TC-57…TC-59, TC-254…TC-258, TC-260 (service part), TC-261;
plus update rules, ``set_inactive``, ``member_by_no`` and ``consent_dates``.
"""

from __future__ import annotations

from datetime import date, datetime, timezone as dt_timezone

import pytest
from django.core.exceptions import PermissionDenied

from accounts.models import Role
from administration import clock
from administration.audit import AuditAction
from administration.errors import RuleViolation
from administration.models import AuditEvent
from members import services
from members.models import ConsentAction, ConsentEvent, Member
from tests.support.factories import make_member, make_staff

pytestmark = pytest.mark.django_db


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


def set_today(monkeypatch: pytest.MonkeyPatch, day: date) -> None:
    monkeypatch.setattr(clock, "today", lambda: day)


def _member(*args, **kwargs) -> Member:
    return Member.objects.get(pk=make_member(*args, **kwargs).pk)


# --- Create (FR-01, AC-01) ----------------------------------------------------


def test_tc44_create_member_fills_derived_fields(clerk) -> None:
    member = services.create_member(clerk, "Ayşe Yılmaz", "0555 111 22 33", None)
    member.refresh_from_db()
    assert member.member_no >= 1
    assert Member.objects.filter(member_no=member.member_no).count() == 1
    assert member.phone == "0555 111 22 33"
    assert member.phone_digits == "05551112233"
    assert member.search_key == "ayse yilmaz"
    assert member.email is None
    assert member.is_active and member.deactivated_on is None
    assert not member.has_email_consent
    assert member.archived_loan_count == 0


def test_tc45_member_numbers_are_sequential(clerk) -> None:
    first = services.create_member(clerk, "Ayşe Yılmaz", "0555 111 22 33", None)
    second = services.create_member(clerk, "Mehmet Demir", "0532 000 00 00", None)
    assert second.member_no == first.member_no + 1


def test_member_number_follows_the_highest_existing(clerk) -> None:
    make_member(member_no=1041)
    assert services.create_member(clerk, "Ayşe Yılmaz", "0555", None).member_no == 1042


def test_first_member_number_is_one(clerk) -> None:
    assert services.create_member(clerk, "Ayşe Yılmaz", "0555", None).member_no == 1


@pytest.mark.parametrize(
    ("full_name", "phone", "message"),
    [("", "0555 111 22 33", "Ad soyad boş olamaz"), ("Ayşe Yılmaz", "", "Telefon boş olamaz")],
)
def test_tc46_blank_name_or_phone_is_refused(clerk, full_name, phone, message) -> None:
    with pytest.raises(RuleViolation) as exc:
        services.create_member(clerk, full_name, phone, None)
    assert exc.value.message == message
    assert Member.objects.count() == 0


def test_create_member_trims_and_keeps_email(clerk) -> None:
    member = services.create_member(clerk, "  Ayşe Yılmaz ", " 0555 ", " ayse@example.org ")
    assert (member.full_name, member.phone, member.email) == ("Ayşe Yılmaz", "0555", "ayse@example.org")


def test_blank_email_is_stored_as_null(clerk) -> None:
    assert services.create_member(clerk, "Ayşe Yılmaz", "0555", "  ").email is None


def test_invalid_email_is_refused(clerk) -> None:
    with pytest.raises(RuleViolation) as exc:
        services.create_member(clerk, "Ayşe Yılmaz", "0555", "ayse@")
    assert exc.value.message == "Geçerli bir e-posta adresi girin"
    assert Member.objects.count() == 0


def test_email_longer_than_254_is_refused(clerk) -> None:
    email = "a" * 60 + "@" + ".".join(["b" * 60] * 3) + ".org"  # 249 < 254 < len
    long_email = "c" * 10 + email
    assert len(long_email) > 254
    with pytest.raises(RuleViolation) as exc:
        services.create_member(clerk, "Ayşe Yılmaz", "0555", long_email)
    assert exc.value.message == "Geçerli bir e-posta adresi girin"


def test_create_member_requires_an_active_staff_actor() -> None:
    inactive = make_staff("eski", is_active=False)
    with pytest.raises(PermissionDenied):
        services.create_member(inactive, "Ayşe Yılmaz", "0555", None)


# --- Search (FR-01, KL-10, NFR-10) --------------------------------------------


@pytest.mark.parametrize("q", ["ayşe", "AYŞE", "ayse"])
def test_tc47_name_search_ignores_case_and_turkish_letters(clerk, q: str) -> None:
    ayse = services.create_member(clerk, "Ayşe Yılmaz", "0555 111 22 33", None)
    services.create_member(clerk, "Mehmet Demir", "0532 000 00 00", None)
    assert services.search_members(q) == [ayse]


def test_tc48_member_number_and_phone_search(clerk) -> None:
    ayse = make_member("Ayşe Yılmaz", "0555 111 22 33", member_no=1042)
    make_member("Mehmet Demir", "0532 000 00 00", member_no=1043)
    assert services.search_members("1042") == [ayse]
    assert services.search_members("05551112233") == [ayse]


def test_digit_search_lists_the_exact_member_number_first() -> None:
    by_phone = make_member("Ali Kaya", "0212 000 00 07", member_no=3)
    by_no = make_member("Zeynep Ak", "0532 111 11 11", member_no=7)
    assert services.search_members("7") == [by_no, by_phone]


def test_partial_phone_digits_match() -> None:
    ayse = make_member("Ayşe Yılmaz", "0555 111 22 33", member_no=1)
    assert services.search_members("2233") == [ayse]


def test_very_long_digit_query_does_not_overflow() -> None:
    make_member("Ayşe Yılmaz", "0555 111 22 33", member_no=1)
    assert services.search_members("9" * 30) == []


def test_tc49_renamed_member_is_found_by_the_new_name_only(clerk) -> None:
    member = services.create_member(clerk, "Ayşe Yılmaz", "0555 111 22 33", None)
    services.update_member(clerk, member, full_name="Ayşe Demir")
    assert services.search_members("demir") == [member]
    assert services.search_members("yılmaz") == []


@pytest.mark.parametrize("q", ["%", "_"])
def test_tc50_like_wildcards_are_literal(q: str) -> None:
    make_member("Ayşe Yılmaz", "0555 111 22 33")
    make_member("Mehmet Demir", "0532 000 00 00")
    assert services.search_members(q) == []


@pytest.mark.parametrize("count", [50, 51])
def test_tc51_search_returns_at_most_50(count: int) -> None:
    for i in range(count):
        make_member(f"Deneme Üye {i}", f"0500 000 {i:04d}")
    assert len(services.search_members("deneme")) == 50


def test_empty_query_returns_nothing() -> None:
    make_member()
    assert services.search_members("") == []
    assert services.search_members("  ( ) ") == []


def test_text_search_orders_by_name() -> None:
    zeynep = make_member("Zeynep Ak", "0500", member_no=1)
    ali = make_member("Ali Ak", "0501", member_no=2)
    assert services.search_members("ak") == [ali, zeynep]


@pytest.mark.parametrize("q", ["0555-111-2233", "(0555) 111 22 33", "Ayşe Yılmaz"])
def test_tc261_phone_with_separators_and_full_name_find_the_member(q: str) -> None:
    ayse = make_member("Ayşe Yılmaz", "0555 111 22 33", member_no=1)
    make_member("Mehmet Demir", "0532 000 00 00", member_no=2)
    assert services.search_members(q) == [ayse]


# --- Update -------------------------------------------------------------------


def test_update_member_changes_fields_and_derived_values(clerk) -> None:
    member = _member()
    services.update_member(clerk, member, phone="(0532) 444-55-66", email="a@example.org")
    member.refresh_from_db()
    assert member.phone == "(0532) 444-55-66"
    assert member.phone_digits == "05324445566"
    assert member.email == "a@example.org"


def test_update_member_validates_the_merged_values(clerk) -> None:
    member = _member()
    with pytest.raises(RuleViolation) as exc:
        services.update_member(clerk, member, phone="")
    assert exc.value.message == "Telefon boş olamaz"
    member.refresh_from_db()
    assert member.phone == "0555 111 22 33"


def test_update_member_refuses_unknown_fields(clerk) -> None:
    with pytest.raises(TypeError):
        services.update_member(clerk, _member(), member_no=5)


def test_anonymized_member_cannot_be_updated(clerk) -> None:
    member = _member(anonymized=True)
    with pytest.raises(RuleViolation) as exc:
        services.update_member(clerk, member, full_name="Ayşe Yılmaz")
    assert exc.value.message == "Anonimleştirilmiş üye güncellenemez"
    member.refresh_from_db()
    assert member.full_name is None


def test_tc254_removing_email_withdraws_consent_in_the_same_transaction(
    clerk, monkeypatch
) -> None:
    member = _member(email="ayse@example.org")
    set_today(monkeypatch, date(2026, 11, 5))
    services.set_consent(clerk, member, True, date(2026, 11, 5))
    set_today(monkeypatch, date(2026, 11, 10))
    services.update_member(clerk, member, email=None)
    member.refresh_from_db()
    assert member.email is None
    assert not member.has_email_consent
    latest = member.consent_events.order_by("-id").first()
    assert latest.action == ConsentAction.WITHDRAWN
    assert latest.effective_on == date(2026, 11, 10)
    assert latest.recorded_by == clerk


def test_removing_email_without_consent_writes_no_event(clerk) -> None:
    member = _member(email="ayse@example.org")
    services.update_member(clerk, member, email="")
    member.refresh_from_db()
    assert member.email is None
    assert member.consent_events.count() == 0


def test_changing_email_keeps_consent(clerk, monkeypatch) -> None:
    member = _member(email="ayse@example.org")
    set_today(monkeypatch, date(2026, 11, 5))
    services.set_consent(clerk, member, True, date(2026, 11, 5))
    services.update_member(clerk, member, email="ayse.yilmaz@example.org")
    member.refresh_from_db()
    assert member.has_email_consent
    assert member.consent_events.count() == 1


# --- Consent (FR-03, AC-03, ADR-0047) -----------------------------------------


def test_tc57_consent_given_then_withdrawn(clerk, monkeypatch) -> None:
    member = _member(email="ayse@example.org")
    set_today(monkeypatch, date(2026, 11, 1))
    services.set_consent(clerk, member, True, date(2026, 11, 1))
    member.refresh_from_db()
    assert member.has_email_consent
    set_today(monkeypatch, date(2026, 12, 1))
    services.set_consent(clerk, member, False, date(2026, 12, 1))
    member.refresh_from_db()
    assert not member.has_email_consent
    assert member.consent_events.count() == 2
    assert services.consent_dates(member) == (date(2026, 11, 1), date(2026, 12, 1))


def test_tc58_given_withdrawn_given(clerk, monkeypatch) -> None:
    member = _member(email="ayse@example.org")
    set_today(monkeypatch, date(2026, 12, 20))
    services.set_consent(clerk, member, True, date(2026, 11, 1))
    services.set_consent(clerk, member, False, date(2026, 12, 1))
    event = services.set_consent(clerk, member, True, date(2026, 12, 15))
    assert isinstance(event, ConsentEvent)
    member.refresh_from_db()
    assert member.consent_events.count() == 3
    assert member.has_email_consent
    assert services.consent_dates(member) == (date(2026, 12, 15), date(2026, 12, 1))


def test_tc59_failure_after_the_event_insert_rolls_back(clerk, monkeypatch) -> None:
    member = _member(email="ayse@example.org")
    set_today(monkeypatch, date(2026, 11, 1))
    real_refresh = services._refresh_consent_flag

    def refresh_then_fail(target: Member) -> None:
        real_refresh(target)
        raise RuntimeError("boom")

    monkeypatch.setattr(services, "_refresh_consent_flag", refresh_then_fail)
    with pytest.raises(RuntimeError):
        services.set_consent(clerk, member, True, date(2026, 11, 1))
    member = Member.objects.get(pk=member.pk)
    assert ConsentEvent.objects.count() == 0
    assert not member.has_email_consent


def test_tc255_future_consent_dates_are_refused(clerk, monkeypatch) -> None:
    member = _member(email="ayse@example.org")
    set_today(monkeypatch, date(2026, 11, 1))
    for on in (date(2026, 11, 5), date(2026, 11, 2)):
        with pytest.raises(RuleViolation) as exc:
            services.set_consent(clerk, member, True, on)
        assert exc.value.message == "Rıza tarihi gelecekte olamaz"
    assert ConsentEvent.objects.count() == 0
    services.set_consent(clerk, member, True, date(2026, 11, 1))
    assert ConsentEvent.objects.count() == 1


def test_tc256_repeating_the_current_state_is_refused(clerk, monkeypatch) -> None:
    set_today(monkeypatch, date(2026, 11, 1))
    consenting = _member(email="ayse@example.org")
    services.set_consent(clerk, consenting, True, date(2026, 11, 1))
    without_events = _member("Mehmet Demir", "0532", email="mehmet@example.org")
    events_before, audit_before = ConsentEvent.objects.count(), AuditEvent.objects.count()
    with pytest.raises(RuleViolation) as exc:
        services.set_consent(clerk, consenting, True, date(2026, 11, 1))
    assert exc.value.message == "Üyenin rızası zaten var"
    with pytest.raises(RuleViolation) as exc:
        services.set_consent(clerk, without_events, False, date(2026, 11, 1))
    assert exc.value.message == "Üyenin rızası zaten yok"
    assert ConsentEvent.objects.count() == events_before
    assert AuditEvent.objects.count() == audit_before


def test_tc257_older_event_does_not_change_the_current_state(clerk, monkeypatch) -> None:
    member = _member(email="ayse@example.org")
    set_today(monkeypatch, date(2026, 11, 20))
    services.set_consent(clerk, member, True, date(2026, 11, 10))
    services.set_consent(clerk, member, False, date(2026, 11, 5))
    member.refresh_from_db()
    assert member.consent_events.count() == 2
    assert member.has_email_consent


def test_tc257_same_day_event_recorded_later_wins(clerk, monkeypatch) -> None:
    member = _member(email="ayse@example.org")
    set_today(monkeypatch, date(2026, 11, 20))
    services.set_consent(clerk, member, True, date(2026, 11, 10))
    services.set_consent(clerk, member, False, date(2026, 11, 10))
    member.refresh_from_db()
    assert not member.has_email_consent
    given, withdrawn = member.consent_events.order_by("id")
    assert (withdrawn.recorded_at, withdrawn.id) > (given.recorded_at, given.id)


def test_tc258_consent_needs_an_email_address(clerk, monkeypatch) -> None:
    set_today(monkeypatch, date(2026, 11, 1))
    member = _member(email=None)
    with pytest.raises(RuleViolation) as exc:
        services.set_consent(clerk, member, True, date(2026, 11, 1))
    assert exc.value.message == "Rıza için e-posta adresi gerekli"
    assert ConsentEvent.objects.count() == 0


def test_consent_event_records_actor_and_time(clerk, monkeypatch) -> None:
    set_today(monkeypatch, date(2026, 11, 1))
    member = _member(email="ayse@example.org")
    event = services.set_consent(clerk, member, True, date(2026, 10, 30))
    assert event.recorded_by == clerk
    assert event.effective_on == date(2026, 10, 30)
    assert event.recorded_at is not None
    assert AuditEvent.objects.count() == 0  # KL-36: the events are the trail


def test_consent_dates_without_events() -> None:
    assert services.consent_dates(_member()) == (None, None)


# --- Reactivation (FR-40, ADR-0042) -------------------------------------------


def test_reactivate_member_restores_and_audits(clerk) -> None:
    member = _member(member_no=42, is_active=False, deactivated_on=date(2026, 10, 1))
    services.reactivate_member(clerk, member)
    member.refresh_from_db()
    assert member.is_active and member.deactivated_on is None
    event = AuditEvent.objects.get()
    assert event.action == AuditAction.MEMBER_REACTIVATED
    assert (event.actor, event.target_type, event.target_id) == (clerk, "member", member.pk)
    assert event.details == {"member_no": 42}


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"anonymized": True}, "Anonimleştirilmiş üye aktifleştirilemez"),
        ({"is_active": True}, "Üye zaten aktif"),
    ],
)
def test_tc260_reactivation_refusals(clerk, kwargs, message) -> None:
    member = _member(**kwargs)
    with pytest.raises(RuleViolation) as exc:
        services.reactivate_member(clerk, member)
    assert exc.value.message == message
    assert AuditEvent.objects.count() == 0


# --- set_inactive and lookups -------------------------------------------------


def test_set_inactive_writes_today(clerk, monkeypatch) -> None:
    set_today(monkeypatch, date(2026, 11, 16))
    member = _member()
    services.set_inactive(clerk, member)
    member.refresh_from_db()
    assert not member.is_active
    assert member.deactivated_on == date(2026, 11, 16)


def test_member_by_no() -> None:
    member = make_member(member_no=42)
    assert services.member_by_no(42) == member
    with pytest.raises(RuleViolation) as exc:
        services.member_by_no(43)
    assert exc.value.message == "Üye bulunamadı"


def test_inactive_member_requires_a_deactivation_date() -> None:
    from django.db import IntegrityError, transaction

    member = make_member()
    with pytest.raises(IntegrityError), transaction.atomic():
        Member.objects.filter(pk=member.pk).update(is_active=False, deactivated_on=None)


def test_member_save_derives_search_key_and_phone_digits() -> None:
    member = make_member("İsmail ÇAĞLAR", "(0532) 1")
    assert (member.search_key, member.phone_digits) == ("ismail caglar", "05321")
    anonymous = make_member(anonymized=True)
    assert (anonymous.search_key, anonymous.phone_digits) == ("", None)
    assert anonymous.anonymized_at == datetime(2026, 1, 1, tzinfo=dt_timezone.utc)
