"""``send_reminders`` command tests (G13): TC-180, TC-185, TC-295; plus the
default date and the invalid ``--date`` message (G13 small decision 7)."""

from __future__ import annotations

import smtplib
from datetime import date
from io import StringIO

import pytest
from django.core import mail
from django.core.mail.backends.locmem import EmailBackend
from django.core.management import CommandError, call_command

from administration import clock
from administration.models import Job, JobRun
from members.models import Member
from notifications.models import ReminderLog, ReminderStatus
from tests.support.factories import make_loan, make_member

pytestmark = pytest.mark.django_db


@pytest.fixture
def smtp_fails(monkeypatch: pytest.MonkeyPatch):
    failing: set[str] = set()
    original = EmailBackend.send_messages

    def send_messages(self, messages):
        for message in messages:
            if failing.intersection(message.to):
                raise smtplib.SMTPServerDisconnected("Connection unexpectedly closed")
        return original(self, messages)

    monkeypatch.setattr(EmailBackend, "send_messages", send_messages)
    return failing


def consenting(email: str) -> Member:
    member = make_member(email=email)
    Member.objects.filter(pk=member.pk).update(has_email_consent=True)
    return Member.objects.get(pk=member.pk)


def run(*args: str) -> str:
    out = StringIO()
    call_command("send_reminders", *args, stdout=out)
    return out.getvalue()


def run_failing(*args: str) -> tuple[str, CommandError]:
    out = StringIO()
    with pytest.raises(CommandError) as info:
        call_command("send_reminders", *args, stdout=out)
    return out.getvalue(), info.value


def test_tc185_given_date_counts_and_exit_zero() -> None:
    make_loan(consenting("ayse@example.org"))  # due 2026-11-16
    output = run("--date", "2026-11-14")
    assert output.strip() == "gönderilen=1, başarısız=0, atlanan=0"
    job = JobRun.objects.get()
    assert (job.job, job.run_on, job.status, job.detail) == (
        Job.REMINDERS,
        date(2026, 11, 14),
        JobRun.Status.SUCCESS,
        "gönderilen=1, başarısız=0, atlanan=0",
    )
    assert len(mail.outbox) == 1


def test_tc180_smtp_failure_then_retry(smtp_fails) -> None:
    make_loan(consenting("ayse@example.org"))
    smtp_fails.add("ayse@example.org")
    output, error = run_failing("--date", "2026-11-14")
    assert error.returncode == 1
    assert output.strip() == "gönderilen=0, başarısız=1, atlanan=0"
    log = ReminderLog.objects.get()
    assert log.status == ReminderStatus.FAILED
    assert log.error == "SMTPServerDisconnected: Connection unexpectedly closed"
    assert JobRun.objects.get().status == JobRun.Status.SUCCESS
    smtp_fails.clear()
    assert run("--date", "2026-11-15").strip() == "gönderilen=1, başarısız=0, atlanan=0"
    assert ReminderLog.objects.filter(status=ReminderStatus.SENT).count() == 1
    assert len(mail.outbox) == 1


def test_tc295_partial_failure(smtp_fails) -> None:
    make_loan(consenting("ok@example.org"))
    failing = make_loan(consenting("f@example.org"))
    smtp_fails.add("f@example.org")
    output, error = run_failing("--date", "2026-11-14")
    assert error.returncode == 1
    assert output.strip() == "gönderilen=1, başarısız=1, atlanan=0"
    job = JobRun.objects.get()
    assert job.status == JobRun.Status.SUCCESS
    assert job.detail == "gönderilen=1, başarısız=1, atlanan=0"
    smtp_fails.clear()
    assert run("--date", "2026-11-15").strip() == "gönderilen=1, başarısız=0, atlanan=0"
    assert [m.to for m in mail.outbox] == [["ok@example.org"], ["f@example.org"]]
    sent = ReminderLog.objects.filter(status=ReminderStatus.SENT, loan=failing)
    assert sent.count() == 1


def test_default_date_is_today(monkeypatch) -> None:
    monkeypatch.setattr(clock, "today", lambda: date(2026, 11, 15))
    make_loan(consenting("ayse@example.org"))
    run()
    assert JobRun.objects.get().run_on == date(2026, 11, 15)
    assert len(mail.outbox) == 1


@pytest.mark.parametrize("value", ["2026-13-01", "14.11.2026", "yarın"])
def test_invalid_date_is_a_command_error(value: str) -> None:
    with pytest.raises(CommandError, match=f"^Geçersiz tarih: {value}$"):
        call_command("send_reminders", "--date", value, stdout=StringIO())
    assert not JobRun.objects.exists()
