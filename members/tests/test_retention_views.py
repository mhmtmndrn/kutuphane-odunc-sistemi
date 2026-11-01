"""Retention screens and the anonymized member's name (G15): TC-308, TC-309,
TC-331 and TC-334 (KL-34, ADR-0045; G14–G16 small decisions 7 and 8)."""

from __future__ import annotations

import re
from datetime import date

import pytest
from django.test import Client

from accounts.models import Role
from administration import clock
from billing.models import EntryKind
from circulation.models import CloseReason
from members.models import ANONYMIZED_NAME, Member
from tests.support.factories import make_charge, make_copy, make_loan, make_member, make_staff

pytestmark = pytest.mark.django_db

RETENTION_URL = "/uyeler/saklama/"


@pytest.fixture
def admin_client(client: Client) -> Client:
    client.force_login(make_staff("ayse.y", role=Role.ADMIN))
    return client


@pytest.fixture
def clerk_client() -> Client:
    client = Client()
    client.force_login(make_staff("ali", role=Role.CLERK))
    return client


@pytest.fixture(autouse=True)
def today(monkeypatch: pytest.MonkeyPatch) -> date:
    day = date(2028, 11, 5)
    monkeypatch.setattr(clock, "today", lambda: day)
    return day


def _row(body: str, member_no: int) -> str:
    match = re.search(rf'<tr>\s*<td><a href="/uyeler/{member_no}/">.*?</tr>', body, re.S)
    assert match, f"no row for {member_no}"
    return match.group(0)


def test_tc308_deferred_list_for_admin_only(admin_client: Client, clerk_client: Client) -> None:
    later = make_member("Can Ak", is_active=False, deactivated_on=date(2026, 11, 1))
    earlier = make_member("Ece Su", is_active=False, deactivated_on=date(2026, 10, 1))
    make_charge(later, EntryKind.FINE, 2000)
    make_charge(earlier, EntryKind.FEE, 4550)
    make_member("Borçsuz Üye", is_active=False, deactivated_on=date(2026, 9, 1))

    response = admin_client.get(RETENTION_URL)
    assert response.status_code == 200
    body = response.content.decode()
    assert body.index(f"/uyeler/{earlier.member_no}/") < body.index(f"/uyeler/{later.member_no}/")
    row = _row(body, earlier.member_no)
    for text in ("Ece Su", "01.10.2026", "01.10.2028", "45,50 TL", "borç nedeniyle bekliyor"):
        assert text in row
    row = _row(body, later.member_no)
    for text in ("Can Ak", "01.11.2026", "01.11.2028", "20,00 TL", "borç nedeniyle bekliyor"):
        assert text in row
    assert "Borçsuz Üye" not in body

    assert clerk_client.get(RETENTION_URL).status_code == 403


def test_deferred_list_empty(admin_client: Client) -> None:
    body = admin_client.get(RETENTION_URL).content.decode()
    assert "Borç nedeniyle bekleyen üye yok." in body


def test_tc309_anonymized_member_detail_with_total_loans(admin_client: Client) -> None:
    member = make_member(anonymized=True)
    for closed in (date(2026, 3, 1), date(2026, 5, 1)):
        make_loan(
            member,
            make_copy(),
            loaned_on=date(2026, 2, 1),
            due_on=closed,
            closed_on=closed,
            close_reason=CloseReason.RETURNED,
        )
    Member.objects.filter(pk=member.pk).update(archived_loan_count=3)
    body = admin_client.get(f"/uyeler/{member.member_no}/").content.decode()
    assert "Anonimleştirilmiş üye" in body
    assert "Toplam ödünç: 5" in body


def test_total_loans_for_an_ordinary_member(clerk_client: Client) -> None:
    member = make_member()
    make_loan(member, make_copy())
    body = clerk_client.get(f"/uyeler/{member.member_no}/").content.decode()
    assert "Toplam ödünç: 1" in body


def test_tc331_display_name() -> None:
    assert ANONYMIZED_NAME == "Anonimleştirilmiş üye"
    assert make_member("Ayşe Yılmaz").display_name == "Ayşe Yılmaz"
    assert make_member(anonymized=True).display_name == "Anonimleştirilmiş üye"


def test_tc331_anonymized_name_on_every_screen(clerk_client: Client) -> None:
    member = make_member(anonymized=True, member_no=4242)
    # An open overdue loan cannot arise for an anonymized member through the
    # services; the factory builds it to check the overdue list's name.
    make_loan(member, make_copy(), loaned_on=date(2028, 10, 1), due_on=date(2028, 10, 15))
    screens = {
        "search": "/uyeler/?q=4242",
        "checkout": "/odunc/?uye=4242",
        "statement": "/borclar/4242/",
        "overdue": "/gecikenler/",
    }
    for name, url in screens.items():
        response = clerk_client.get(url)
        assert response.status_code == 200, name
        assert "Anonimleştirilmiş üye" in response.content.decode(), name


def test_tc334_retention_link_for_admin_only(admin_client: Client, clerk_client: Client) -> None:
    admin_home = admin_client.get("/").content.decode()
    clerk_home = clerk_client.get("/").content.decode()
    assert f'href="{RETENTION_URL}"' in admin_home
    assert f'href="{RETENTION_URL}"' not in clerk_home
