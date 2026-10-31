"""Notification service tests (G13): TC-172, TC-174…TC-179, TC-181, TC-182,
TC-184, TC-294, TC-296, TC-297; plus the G13 small decisions 3–5 (plan §11)."""

from __future__ import annotations

import smtplib
from datetime import date

import pytest
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.core.mail.backends.locmem import EmailBackend
from django.db import IntegrityError, connection, transaction
from django.test import override_settings

from accounts.models import Role
from administration import clock
from administration.errors import RuleViolation
from administration.models import ClosedDate, LibrarySettings
from members import services as member_services
from members.models import Member
from notifications import services
from notifications.domain import ReminderCounts, ReminderKind
from notifications.models import ReminderLog, ReminderStatus
from tests.support.factories import make_book, make_copy, make_loan, make_member, make_staff

pytestmark = pytest.mark.django_db

DUE = date(2026, 11, 16)  # make_loan default: loaned 11-02 + 14 days


@pytest.fixture
def today(monkeypatch: pytest.MonkeyPatch):
    def set_today(day: date) -> None:
        monkeypatch.setattr(clock, "today", lambda: day)

    set_today(date(2026, 11, 2))
    return set_today


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


@pytest.fixture
def smtp_fails(monkeypatch: pytest.MonkeyPatch):
    """Make the e-mail backend fail for the given recipients."""
    failing: dict[str, Exception] = {}
    original = EmailBackend.send_messages

    def send_messages(self, messages):
        for message in messages:
            for address in message.to:
                if address in failing:
                    raise failing[address]
        return original(self, messages)

    monkeypatch.setattr(EmailBackend, "send_messages", send_messages)

    def fail(address: str, exc: Exception | None = None) -> None:
        failing[address] = exc or smtplib.SMTPServerDisconnected("Connection unexpectedly closed")

    return fail


def consenting(email: str = "ayse@example.org", **kwargs) -> Member:
    """A member with an e-mail address and current consent."""
    member = make_member(email=email, **kwargs)
    Member.objects.filter(pk=member.pk).update(has_email_consent=True)
    member.refresh_from_db()
    return member


def _logs(**filters) -> list[tuple]:
    return list(
        ReminderLog.objects.filter(**filters)
        .order_by("id")
        .values_list("kind", "status", "due_on")
    )


# --- Overdue list (FR-20) -------------------------------------------------------


def test_tc172_accrued_fine_uses_the_loan_rate_snapshot() -> None:
    loan = make_loan(consenting(), daily_fine_kurus=500, fine_cap_kurus=15000)
    LibrarySettings.objects.filter(pk=1).update(daily_fine_kurus=1000)
    entries = services.overdue_list(date(2026, 12, 26))  # 40 days late
    assert [(e.row.loan.pk, e.row.late_days, e.row.accrued_fine) for e in entries] == [
        (loan.pk, 40, 15000)
    ]


def test_overdue_list_marks_rows_without_e_mail_or_consent() -> None:
    no_email = make_loan(make_member("E Yok", email=None))
    no_consent = make_loan(make_member("R Yok", email="r@example.org"))
    ok = make_loan(consenting())
    blocks = {e.row.loan.pk: e.block for e in services.overdue_list(date(2026, 11, 20))}
    assert blocks == {no_email.pk: "no_email", no_consent.pk: "no_consent", ok.pk: None}


# --- Automatic reminders (FR-18, S6) ---------------------------------------------


def test_tc174_due_soon_is_sent_once_per_due_date() -> None:
    member = consenting()
    loan = make_loan(member)
    first = services.send_due_reminders(date(2026, 11, 14))
    assert first == ReminderCounts(sent=1, failed=0, skipped=0)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["ayse@example.org"]
    log = ReminderLog.objects.get()
    assert (log.loan_id, log.kind, log.status, log.due_on) == (
        loan.pk,
        ReminderKind.DUE_SOON,
        ReminderStatus.SENT,
        DUE,
    )
    assert log.triggered_by is None and log.error is None and log.sent_at is not None
    second = services.send_due_reminders(date(2026, 11, 14))
    assert second == ReminderCounts(sent=0, failed=0, skipped=0)
    assert len(mail.outbox) == 1


def test_tc175_no_consent_means_no_e_mail_and_no_log() -> None:
    make_loan(make_member(email="ayse@example.org"))
    assert services.send_due_reminders(date(2026, 11, 14)) == ReminderCounts(0, 0, 0)
    assert mail.outbox == []
    assert not ReminderLog.objects.exists()


def test_tc176_consent_without_e_mail_sends_nothing() -> None:
    member = make_member(email=None)
    Member.objects.filter(pk=member.pk).update(has_email_consent=True)
    make_loan(member)
    services.send_due_reminders(date(2026, 11, 14))
    assert mail.outbox == []
    assert not ReminderLog.objects.exists()


def test_tc176_closed_loan_in_the_window_sends_nothing() -> None:
    make_loan(consenting(), closed_on=date(2026, 11, 13), close_reason="RETURNED")
    services.send_due_reminders(date(2026, 11, 14))
    assert mail.outbox == []


def test_inactive_member_gets_no_automatic_reminder() -> None:
    # S6: the member must be active (one condition changed alone).
    member = consenting()
    make_loan(member)
    Member.objects.filter(pk=member.pk).update(is_active=False, deactivated_on=date(2026, 11, 3))
    services.send_due_reminders(date(2026, 11, 14))
    assert mail.outbox == []


def test_tc177_withdrawn_consent_stops_reminders(today, clerk) -> None:
    member = make_member(email="ayse@example.org")
    today(date(2026, 11, 1))
    member_services.set_consent(clerk, member, True, date(2026, 11, 1))
    make_loan(member, loaned_on=date(2026, 11, 19), due_on=date(2026, 12, 3))
    today(date(2026, 12, 1))
    member_services.set_consent(clerk, member, False, date(2026, 12, 1))
    services.send_due_reminders(date(2026, 12, 1))
    services.send_due_reminders(date(2026, 12, 2))
    assert mail.outbox == []
    assert not ReminderLog.objects.exists()


def test_tc178_server_down_through_the_due_soon_window() -> None:
    make_loan(consenting())
    counts = services.send_due_reminders(date(2026, 11, 17))
    assert counts == ReminderCounts(sent=1, failed=0, skipped=0)
    assert _logs() == [(ReminderKind.OVERDUE_1, ReminderStatus.SENT, DUE)]
    assert "İade tarihi geçti" in mail.outbox[0].subject


def test_tc179_overdue_1_is_not_repeated_in_its_window() -> None:
    make_loan(consenting())
    services.send_due_reminders(date(2026, 11, 17))
    for day in range(18, 24):
        assert services.send_due_reminders(date(2026, 11, day)) == ReminderCounts(0, 0, 0)
    assert len(mail.outbox) == 1
    assert _logs() == [(ReminderKind.OVERDUE_1, ReminderStatus.SENT, DUE)]


def test_tc181_unique_violation_after_sending_counts_as_skipped(monkeypatch) -> None:
    loan = make_loan(consenting())
    original = services._send

    def send_while_another_run_logs(message):
        original(message)
        # A concurrent run sent the same reminder and logged it first.
        ReminderLog.objects.create(
            loan=loan, kind=ReminderKind.DUE_SOON, status=ReminderStatus.SENT, due_on=DUE
        )

    monkeypatch.setattr(services, "_send", send_while_another_run_logs)
    counts = services.send_due_reminders(date(2026, 11, 14))
    assert counts == ReminderCounts(sent=0, failed=0, skipped=1)
    assert ReminderLog.objects.filter(status=ReminderStatus.SENT).count() == 1
    monkeypatch.setattr(services, "_send", original)
    assert services.send_due_reminders(date(2026, 11, 15)) == ReminderCounts(0, 0, 0)
    assert len(mail.outbox) == 1


def test_tc182_renewed_loan_gets_due_soon_for_the_new_due_date() -> None:
    loan = make_loan(consenting())
    services.send_due_reminders(date(2026, 11, 14))
    loan.renewed_on = date(2026, 11, 15)
    loan.due_on = date(2026, 11, 30)
    loan.save(update_fields=["renewed_on", "due_on"])
    counts = services.send_due_reminders(date(2026, 11, 28))
    assert counts == ReminderCounts(sent=1, failed=0, skipped=0)
    assert _logs() == [
        (ReminderKind.DUE_SOON, ReminderStatus.SENT, DUE),
        (ReminderKind.DUE_SOON, ReminderStatus.SENT, date(2026, 11, 30)),
    ]
    assert len(mail.outbox) == 2
    assert "30.11.2026" in mail.outbox[1].body


def test_smtp_failure_is_logged_and_retried_in_the_window(smtp_fails) -> None:
    make_loan(consenting())
    smtp_fails("ayse@example.org")
    counts = services.send_due_reminders(date(2026, 11, 14))
    assert counts == ReminderCounts(sent=0, failed=1, skipped=0)
    log = ReminderLog.objects.get()
    assert log.status == ReminderStatus.FAILED
    assert log.error == "SMTPServerDisconnected: Connection unexpectedly closed"


def test_timeout_is_logged_as_failed(smtp_fails) -> None:
    # ADR-0052: EMAIL_TIMEOUT raises socket.timeout (an OSError).
    make_loan(consenting())
    smtp_fails("ayse@example.org", TimeoutError("timed out"))
    assert services.send_due_reminders(date(2026, 11, 14)) == ReminderCounts(0, 1, 0)
    assert ReminderLog.objects.get().error == "TimeoutError: timed out"


def test_error_text_is_cut_to_500_characters(smtp_fails) -> None:
    make_loan(consenting())
    smtp_fails("ayse@example.org", smtplib.SMTPException("x" * 700))
    services.send_due_reminders(date(2026, 11, 14))
    assert len(ReminderLog.objects.get().error) == 500


def test_other_exceptions_propagate(smtp_fails) -> None:
    # G13 small decision 5: only SMTPException and OSError become FAILED.
    make_loan(consenting())
    smtp_fails("ayse@example.org", ValueError("bug"))
    with pytest.raises(ValueError):
        services.send_due_reminders(date(2026, 11, 14))
    assert not ReminderLog.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_no_transaction_is_open_while_sending(monkeypatch) -> None:
    # G13 small decision 3 (data-design §5): no database lock during SMTP.
    clerk = make_staff("ali", role=Role.CLERK)
    monkeypatch.setattr(clock, "today", lambda: date(2026, 11, 18))
    make_loan(consenting("a@example.org"))
    make_loan(consenting("b@example.org"), due_on=date(2026, 11, 20))
    seen: list[bool] = []
    original = services._send

    def spy(message):
        seen.append(connection.in_atomic_block)
        original(message)

    monkeypatch.setattr(services, "_send", spy)
    services.send_due_reminders(date(2026, 11, 18))
    overdue = ReminderLog.objects.get(kind=ReminderKind.OVERDUE_1).loan_id
    services.send_manual_reminders(clerk, [overdue])
    assert seen == [False, False, False]


# --- Reminder log constraints (ADR-0039) -----------------------------------------


def test_tc294_partial_unique_index() -> None:
    loan = make_loan(consenting())

    def log(kind, status=ReminderStatus.SENT, due_on=DUE):
        return ReminderLog.objects.create(loan=loan, kind=kind, status=status, due_on=due_on)

    log(ReminderKind.DUE_SOON)
    with pytest.raises(IntegrityError), transaction.atomic():
        log(ReminderKind.DUE_SOON)
    log(ReminderKind.DUE_SOON, due_on=date(2026, 11, 30))
    log(ReminderKind.MANUAL)
    log(ReminderKind.MANUAL)
    log(ReminderKind.OVERDUE_1, status=ReminderStatus.FAILED)
    log(ReminderKind.OVERDUE_1, status=ReminderStatus.FAILED)
    assert ReminderLog.objects.count() == 6


@pytest.mark.parametrize(
    ("field", "value"), [("kind", "WEEKLY"), ("status", "QUEUED")]
)
def test_reminder_log_check_constraints(field: str, value: str) -> None:
    loan = make_loan(consenting())
    values = {"kind": ReminderKind.DUE_SOON, "status": ReminderStatus.SENT, field: value}
    with pytest.raises(IntegrityError), transaction.atomic():
        ReminderLog.objects.create(loan=loan, due_on=DUE, **values)


# --- E-mail texts (KL-13) ---------------------------------------------------------

CONSENT_LINE = (
    "Bu e-postayı hatırlatma almaya onay verdiğiniz için alıyorsunuz. "
    "Onayınızı kütüphane masasında geri alabilirsiniz."
)


@override_settings(DEFAULT_FROM_EMAIL="kutuphane@merkez.example")
def test_tc296_e_mail_texts() -> None:
    LibrarySettings.objects.filter(pk=1).update(library_name="Merkez")
    make_loan(consenting(), make_copy(make_book("Tutunamayanlar")))
    services.send_due_reminders(date(2026, 11, 14))
    services.send_due_reminders(date(2026, 11, 17))
    due_soon, overdue = mail.outbox
    assert due_soon.subject == "Merkez: İade tarihi yaklaşıyor"
    assert due_soon.body == (
        "Merhaba,\n\n"
        "\"Tutunamayanlar\" kitabının son iade tarihi 16.11.2026. "
        "Bu tarihe kadar iade ederseniz gecikme cezası oluşmaz.\n\n"
        f"{CONSENT_LINE}\n\nMerkez\n"
    )
    assert overdue.subject == "Merkez: İade tarihi geçti"
    assert overdue.body == (
        "Merhaba,\n\n"
        "\"Tutunamayanlar\" kitabının son iade tarihi 16.11.2026 idi. "
        "Geciken her gün için 5,00 TL ceza işler (ödünç başına en fazla 150,00 TL). "
        "Kitabı en kısa sürede iade etmenizi rica ederiz.\n\n"
        f"{CONSENT_LINE}\n\nMerkez\n"
    )
    for message in (due_soon, overdue):
        assert message.to == ["ayse@example.org"]
        assert message.cc == [] and message.bcc == []
        assert message.from_email == "kutuphane@merkez.example"


def test_e_mail_fine_comes_from_the_loan_snapshot() -> None:
    # G13 small decision 4 (ADR-0023): not from the current settings.
    make_loan(consenting(), daily_fine_kurus=300, fine_cap_kurus=9000)
    LibrarySettings.objects.filter(pk=1).update(daily_fine_kurus=1000, fine_cap_kurus=50000)
    services.send_due_reminders(date(2026, 11, 17))
    body = mail.outbox[0].body
    assert "3,00 TL" in body and "90,00 TL" in body
    assert "10,00 TL" not in body


def test_e_mail_text_is_not_html_escaped() -> None:
    make_loan(consenting(), make_copy(make_book("Tom & Jerry'nin \"Günü\"")))
    LibrarySettings.objects.filter(pk=1).update(library_name="Ada & Kitap")
    services.send_due_reminders(date(2026, 11, 14))
    message = mail.outbox[0]
    assert message.subject == "Ada & Kitap: İade tarihi yaklaşıyor"
    assert "\"Tom & Jerry'nin \"Günü\"\"" in message.body


# --- Manual reminders (FR-19, KL-28) ----------------------------------------------


def test_tc184_manual_reminders_have_no_repeat_guard(today, clerk) -> None:
    today(date(2026, 11, 18))
    loan = make_loan(consenting())
    for _ in range(2):
        [result] = services.send_manual_reminders(clerk, [loan.pk])
        assert result.outcome == "sent"
    assert _logs(kind=ReminderKind.MANUAL) == [
        (ReminderKind.MANUAL, ReminderStatus.SENT, DUE),
        (ReminderKind.MANUAL, ReminderStatus.SENT, DUE),
    ]
    assert services.send_due_reminders(date(2026, 11, 18)) == ReminderCounts(1, 0, 0)
    assert len(mail.outbox) == 3
    assert ReminderLog.objects.filter(kind=ReminderKind.OVERDUE_1).count() == 1
    assert "İade tarihi geçti" in mail.outbox[0].subject


def test_tc297_manual_outcomes(today, clerk, smtp_fails) -> None:
    today(date(2026, 11, 20))
    not_overdue = make_loan(consenting("n@example.org"), due_on=date(2026, 11, 20))
    no_email = make_loan(make_member("E Yok", email=None))
    no_consent = make_loan(make_member("R Yok", email="r@example.org"))
    failing = make_loan(consenting("f@example.org"))
    ok = make_loan(consenting("ok@example.org"))
    smtp_fails("f@example.org")
    ids = [not_overdue.pk, no_email.pk, no_consent.pk, failing.pk, ok.pk]
    results = services.send_manual_reminders(clerk, ids)
    assert [(r.loan_id, r.outcome) for r in results] == [
        (not_overdue.pk, "not_overdue"),
        (no_email.pk, "no_email"),
        (no_consent.pk, "no_consent"),
        (failing.pk, "failed"),
        (ok.pk, "sent"),
    ]
    rows = list(
        ReminderLog.objects.order_by("id").values_list(
            "loan_id", "kind", "status", "due_on", "triggered_by"
        )
    )
    assert rows == [
        (failing.pk, ReminderKind.MANUAL, ReminderStatus.FAILED, DUE, clerk.pk),
        (ok.pk, ReminderKind.MANUAL, ReminderStatus.SENT, DUE, clerk.pk),
    ]
    assert [m.to for m in mail.outbox] == [["ok@example.org"]]
    assert "İade tarihi geçti" in mail.outbox[0].subject


def test_manual_result_carries_the_message_fields(today, clerk) -> None:
    today(date(2026, 11, 20))
    member = consenting(full_name="Ayşe Yılmaz", member_no=1042)
    loan = make_loan(member, make_copy(make_book("Tutunamayanlar")))
    [result] = services.send_manual_reminders(clerk, [loan.pk])
    assert (result.member_no, result.full_name, result.title) == (
        1042,
        "Ayşe Yılmaz",
        "Tutunamayanlar",
    )


def test_manual_closed_loan_is_not_overdue(today, clerk) -> None:
    today(date(2026, 11, 20))
    loan = make_loan(consenting(), closed_on=date(2026, 11, 19), close_reason="RETURNED")
    [result] = services.send_manual_reminders(clerk, [loan.pk])
    assert result.outcome == "not_overdue"
    assert mail.outbox == []


def test_manual_duplicate_ids_send_once(today, clerk) -> None:
    today(date(2026, 11, 20))
    loan = make_loan(consenting())
    results = services.send_manual_reminders(clerk, [loan.pk, loan.pk])
    assert [r.outcome for r in results] == ["sent"]
    assert len(mail.outbox) == 1


def test_manual_unknown_loan_sends_nothing(today, clerk) -> None:
    today(date(2026, 11, 20))
    loan = make_loan(consenting())
    with pytest.raises(RuleViolation, match="Ödünç bulunamadı"):
        services.send_manual_reminders(clerk, [loan.pk, 999999])
    assert mail.outbox == []
    assert not ReminderLog.objects.exists()


def test_manual_reminder_requires_an_active_staff_member(today) -> None:
    loan = make_loan(consenting())
    inactive = make_staff("eski", is_active=False)
    with pytest.raises(PermissionDenied):
        services.send_manual_reminders(inactive, [loan.pk])
    with pytest.raises(PermissionDenied):
        services.send_manual_reminders(None, [loan.pk])


def test_manual_overdue_follows_the_overdue_list(today, clerk) -> None:
    # Due yesterday and today is a closed date: zero late days, but the loan
    # is on the overdue list (due_on < today), so the reminder goes out.
    today(date(2026, 11, 17))
    ClosedDate.objects.create(date=date(2026, 11, 17))
    loan = make_loan(consenting())
    [result] = services.send_manual_reminders(clerk, [loan.pk])
    assert result.outcome == "sent"
