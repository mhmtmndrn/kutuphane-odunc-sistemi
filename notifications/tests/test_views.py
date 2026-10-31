"""Overdue list and manual reminder view tests (G13): TC-171, TC-183, TC-298;
plus the G13 small decisions 1, 2 and 6 (plan §11)."""

from __future__ import annotations

import re
from datetime import date

import pytest
from django.core import mail
from django.test import Client

from accounts.models import Role
from administration import clock
from administration.models import ClosedDate
from members.models import Member
from notifications.models import ReminderLog, ReminderStatus
from tests.support.factories import make_book, make_copy, make_loan, make_member, make_staff

pytestmark = pytest.mark.django_db

LIST_URL = "/gecikenler/"
REMIND_URL = "/gecikenler/hatirlat/"


@pytest.fixture(autouse=True)
def today(monkeypatch: pytest.MonkeyPatch):
    def set_today(day: date) -> None:
        monkeypatch.setattr(clock, "today", lambda: day)

    set_today(date(2026, 11, 20))
    return set_today


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


@pytest.fixture
def clerk_client(client: Client, clerk) -> Client:
    client.force_login(clerk)
    return client


def consenting(full_name: str, email: str, **kwargs) -> Member:
    member = make_member(full_name, email=email, **kwargs)
    Member.objects.filter(pk=member.pk).update(has_email_consent=True)
    return Member.objects.get(pk=member.pk)


def overdue_loan(member: Member, title: str, due_on: date):
    return make_loan(member, make_copy(make_book(title)), loaned_on=date(2026, 10, 20), due_on=due_on)


def _body(response) -> str:
    return response.content.decode()


def _row(body: str, loan_id: int) -> str:
    match = re.search(rf'<tr id="loan-{loan_id}">(.*?)</tr>', body, re.S)
    assert match, f"no row for loan {loan_id}"
    return match.group(1)


def _messages(response) -> list[tuple[str, str]]:
    return [(m.tags, str(m)) for m in response.context["messages"]]


def test_tc171_overdue_list(clerk_client) -> None:
    three = overdue_loan(
        make_member("Ayşe Yılmaz", "0555 111 22 33", member_no=1042), "Tutunamayanlar", date(2026, 11, 17)
    )
    ten = overdue_loan(
        make_member("Mehmet Kaya", "0532 444 55 66", member_no=1043), "Puslu Kıtalar Atlası", date(2026, 11, 10)
    )
    not_late = overdue_loan(make_member("Can Ak", member_no=1044), "Kuyucaklı Yusuf", date(2026, 11, 25))
    due_today = overdue_loan(make_member("Ece Su", member_no=1045), "Saatleri Ayarlama", date(2026, 11, 20))
    response = clerk_client.get(LIST_URL)
    assert response.status_code == 200
    body = _body(response)
    assert f'id="loan-{not_late.pk}"' not in body
    assert f'id="loan-{due_today.pk}"' not in body
    assert body.index(f'id="loan-{ten.pk}"') < body.index(f'id="loan-{three.pk}"')
    row = _row(body, three.pk)
    for text in ("1042", "Ayşe Yılmaz", "0555 111 22 33", "Tutunamayanlar", "17.11.2026", ">3<", "15,00 TL"):
        assert text in row
    row = _row(body, ten.pk)
    for text in ("1043", "Mehmet Kaya", "0532 444 55 66", "Puslu Kıtalar Atlası", "10.11.2026", ">10<", "50,00 TL"):
        assert text in row
    assert 'href="/uyeler/1042/"' in _row(body, three.pk)


def test_tc298_checkboxes_labels_and_closed_dates(clerk_client) -> None:
    ClosedDate.objects.create(date=date(2026, 11, 15))
    no_email = overdue_loan(make_member("E Yok", email=None), "Kitap A", date(2026, 11, 17))
    no_consent = overdue_loan(make_member("R Yok", email="r@example.org"), "Kitap B", date(2026, 11, 17))
    ok = overdue_loan(consenting("Uygun Üye", "ok@example.org"), "Kitap C", date(2026, 11, 10))
    body = _body(clerk_client.get(LIST_URL))
    for loan in (no_email, no_consent, ok):
        assert f'<input type="checkbox" name="loan_ids" value="{loan.pk}"' in _row(body, loan.pk)
    assert "e-posta yok" in _row(body, no_email.pk)
    assert "rıza yok" not in _row(body, no_email.pk)
    assert "rıza yok" in _row(body, no_consent.pk)
    ok_row = _row(body, ok.pk)
    assert "rıza yok" not in ok_row and "e-posta yok" not in ok_row
    # 11-10 → 11-20 is 10 calendar days; 11-15 is closed (ADR-0040, KL-29).
    assert ">9<" in ok_row and "45,00 TL" in ok_row


def test_empty_overdue_list(clerk_client) -> None:
    body = _body(clerk_client.get(LIST_URL))
    assert "Geciken ödünç yok." in body
    assert 'name="loan_ids"' not in body


def test_tc183_manual_reminder_from_the_list(clerk_client, clerk) -> None:
    ok = overdue_loan(consenting("Ayşe Yılmaz", "ayse@example.org", member_no=1042), "Tutunamayanlar", date(2026, 11, 17))
    no_consent = overdue_loan(make_member("Mehmet Kaya", email="m@example.org", member_no=1043), "Kitap B", date(2026, 11, 17))
    response = clerk_client.post(REMIND_URL, {"loan_ids": [str(ok.pk), str(no_consent.pk)]})
    assert response.status_code == 303
    assert response["Location"] == LIST_URL
    assert [m.to for m in mail.outbox] == [["ayse@example.org"]]
    log = ReminderLog.objects.get()
    assert (log.loan_id, log.kind, log.status, log.triggered_by_id) == (ok.pk, "MANUAL", ReminderStatus.SENT, clerk.pk)
    followed = clerk_client.get(LIST_URL)
    assert _messages(followed) == [
        ("success", "1042 Ayşe Yılmaz, Tutunamayanlar: gönderildi"),
        ("warning", "1043 Mehmet Kaya, Kitap B: rıza yok"),
    ]
    body = _body(followed)
    assert "message-success" in body and "message-warning" in body


def test_manual_reminder_messages_for_every_outcome(clerk_client, today) -> None:
    no_email = overdue_loan(make_member("E Yok", email=None, member_no=7), "Kitap A", date(2026, 11, 17))
    not_overdue = overdue_loan(consenting("Can Ak", "c@example.org", member_no=8), "Kitap B", date(2026, 11, 25))
    response = clerk_client.post(REMIND_URL, {"loan_ids": [str(no_email.pk), str(not_overdue.pk)]}, follow=True)
    assert _messages(response) == [
        ("warning", "7 E Yok, Kitap A: e-posta yok"),
        ("warning", "8 Can Ak, Kitap B: gecikmemiş"),
    ]


def test_failed_reminder_message(clerk_client, monkeypatch) -> None:
    from django.core.mail.backends.locmem import EmailBackend

    def broken(self, messages):
        raise OSError("timed out")

    monkeypatch.setattr(EmailBackend, "send_messages", broken)
    loan = overdue_loan(consenting("Ayşe Yılmaz", "a@example.org", member_no=9), "Kitap A", date(2026, 11, 17))
    response = clerk_client.post(REMIND_URL, {"loan_ids": [str(loan.pk)]}, follow=True)
    assert _messages(response) == [("warning", "9 Ayşe Yılmaz, Kitap A: gönderilemedi")]


def test_empty_selection_shows_the_list_with_an_error(clerk_client) -> None:
    loan = overdue_loan(consenting("Ayşe Yılmaz", "a@example.org"), "Kitap A", date(2026, 11, 17))
    response = clerk_client.post(REMIND_URL, {})
    assert response.status_code == 200
    body = _body(response)
    assert "Hatırlatma göndermek için en az bir ödünç seçin" in body
    assert f'id="loan-{loan.pk}"' in body
    assert mail.outbox == []


@pytest.mark.parametrize("value", ["abc", "999999"])
def test_unknown_loan_shows_the_list_with_an_error(clerk_client, value: str) -> None:
    loan = overdue_loan(consenting("Ayşe Yılmaz", "a@example.org"), "Kitap A", date(2026, 11, 17))
    response = clerk_client.post(REMIND_URL, {"loan_ids": [str(loan.pk), value]})
    assert response.status_code == 200
    assert "Ödünç bulunamadı" in _body(response)
    assert mail.outbox == []


def test_remind_is_post_only(clerk_client) -> None:
    assert clerk_client.get(REMIND_URL).status_code == 405


@pytest.mark.parametrize("url", [LIST_URL, REMIND_URL])
def test_anonymous_goes_to_login(client: Client, url: str) -> None:
    response = client.post(url) if url == REMIND_URL else client.get(url)
    assert response.status_code == 302
    assert response["Location"].startswith("/giris/")


def test_overdue_link_in_menu_and_home(clerk_client) -> None:
    body = _body(clerk_client.get("/"))
    assert body.count('href="/gecikenler/"') == 2
    assert ">Gecikenler<" in body
